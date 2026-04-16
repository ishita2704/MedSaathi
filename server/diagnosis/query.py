import os
import asyncio
import base64
import mimetypes
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rbac-diagnosis-index")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_reports")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

pc=Pinecone(api_key=PINECONE_API_KEY)
index=pc.Index(PINECONE_INDEX_NAME)

# Legacy text embedding models are deprecated in the v1beta API.
# Use the Gemini embedding model and explicitly truncate to match Pinecone dimension.
embed_model=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
# Groq decommissioned `llama3-8b-8192`. Use the recommended replacement.
llm=ChatGroq(temperature=0,model_name="llama-3.1-8b-instant",groq_api_key=GROQ_API_KEY)
vision_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

prompt=PromptTemplate.from_template(
    """
You are a medical assistant. Using only the provided context (portions of the user's report), produce:
1) A concise probable diagnosis (1-2 lines)
2) Key findings from the report (bullet points)
3) Recommended next steps (tests/treatments) — label clearly as suggestions, not medical advice.

Context:
{context}

User question:
{question}
""")

rag_chain=prompt | llm


def _image_part_from_path(image_path: str):
    suffix = Path(image_path).suffix.lower()
    mime_type = mimetypes.types_map.get(suffix, "image/png")
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")

    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:{mime_type};base64,{encoded}",
        },
    }


async def diagnose_from_images(report: dict, question: str):
    image_files = report.get("image_files", {})
    image_parts = []
    sources = []

    for modality, label in (("ct_scan", "CT scan"), ("xray", "X-ray")):
        image_info = image_files.get(modality)
        if not image_info:
            continue

        image_parts.append({"type": "text", "text": f"{label} image:"})
        image_parts.append(_image_part_from_path(image_info["saved_path"]))
        sources.append(image_info["filename"])

    if not image_parts:
        return None

    prompt_text = (
        "You are a medical assistant reviewing uploaded medical images. "
        "Use only the visible content of the images and the user's question.\n"
        "Provide:\n"
        "1) A concise probable diagnosis (1-2 lines)\n"
        "2) Key visual findings (bullet points)\n"
        "3) Recommended next steps as suggestions, not medical advice\n\n"
        f"User question:\n{question}"
    )

    message = HumanMessage(content=[
        {"type": "text", "text": prompt_text},
        *image_parts,
    ])
    final = await asyncio.to_thread(vision_llm.invoke, [message])
    return {"diagnosis": final.content, "sources": sources}

async def diagnosis_report(user:str,doc_id:str,question:str, report: dict | None = None):
    if report and report.get("image_files") and not report.get("has_text_reports"):
        image_result = await diagnose_from_images(report, question)
        if image_result:
            return image_result

    # embed question
    embedding=await asyncio.to_thread(
        embed_model.embed_query,
        question,
        output_dimensionality=768,
    )
    # query pinecone
    results=await asyncio.to_thread(index.query,vector=embedding,top_k=5,include_metadata=True)

    # filter for doc_id matches
    contexts=[]
    sources_set=set()
    for match in results.get("matches",[]):
        md=match.get("metadata",{})
        if md.get("doc_id") == doc_id:
            # take text snippet 
            text_snippet=md.get("text") or ""
            contexts.append(text_snippet)
            sources_set.add(md.get("source"))

    if not contexts:
        return {"diagnosis":None,"explanation":"No report contentindexed for this doc_id"}
    
    # limit context length
    context_text="/n/n".join(contexts[:5])

    # final call the rag chain
    final=await asyncio.to_thread(rag_chain.invoke,{"context":context_text,"question":question})

    return {"diagnosis":final.content,"sources":list(sources_set)}