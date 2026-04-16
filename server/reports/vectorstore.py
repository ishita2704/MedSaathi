import os
import time
import asyncio
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rbac-diagnosis-index")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploaded_reports")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.makedirs(UPLOAD_DIR, exist_ok=True)

# initialize pinecone
pc=Pinecone(api_key=PINECONE_API_KEY)
spec=ServerlessSpec(cloud="aws",region=PINECONE_ENV)
existing_indexes=[i["name"] for i in pc.list_indexes()]

if PINECONE_INDEX_NAME not in existing_indexes:
    pc.create_index(name=PINECONE_INDEX_NAME,dimension=768,metric="dotproduct",spec=spec)
    while not pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)

index=pc.Index(PINECONE_INDEX_NAME)


async def save_image_upload(image_file: UploadFile, doc_id: str, prefix: str) -> Dict[str, str]:
    filename = Path(image_file.filename or f"{prefix}.png").name
    save_name = f"{doc_id}_{prefix}_{filename}"
    save_path = Path(UPLOAD_DIR) / save_name
    content = await image_file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "filename": filename,
        "saved_path": str(save_path),
    }


async def load_vectorstore(uploaded_files:List[UploadFile],uploaded:str,doc_id:str):
    """
        Save files, chunk texts, embed texts, upsert in Pinecone and write metadata to Mongo
    """

    from langchain_community.document_loaders import PyPDFLoader, TextLoader

    # Legacy text embedding models are deprecated in the v1beta API.
    # Use the Gemini embedding model and explicitly truncate to match Pinecone dimension.
    embed_model=GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    all_chunks = []
    processed_filenames = []
    splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)

    for file in uploaded_files:
        filename=Path(file.filename).name
        save_path=Path(UPLOAD_DIR) / f"{doc_id}_{filename}"
        content=await file.read()
        with open(save_path,"wb") as f:
            f.write(content)
            
        if filename.lower().endswith('.pdf'):
            loader = PyPDFLoader(str(save_path))
        elif filename.lower().endswith('.txt'):
            loader = TextLoader(str(save_path))
        else:
            continue
            
        try:
            documents = loader.load()
            chunks = splitter.split_documents(documents)
            for chunk in chunks:
                chunk.metadata['source_file'] = filename
            all_chunks.extend(chunks)
            processed_filenames.append(filename)
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    if not all_chunks:
        return {
            "filenames": processed_filenames,
            "num_chunks": 0,
            "has_text_reports": False,
        }

    texts=[chunk.page_content for chunk in all_chunks]
    ids=[f"{doc_id}-{i}" for i in range(len(all_chunks))]
    metadatas=[
            {
                "source": chunk.metadata.get("source_file", "unknown"),
                "doc_id": doc_id,
                "uploader": uploaded,
                "page": chunk.metadata.get("page", None),
                "text": chunk.page_content[:2000]  # store snippet in metadata (avoid huge fields)
            }
            for chunk in all_chunks
    ]

    # get embeddings in thread
    embeddings=await asyncio.to_thread(
        embed_model.embed_documents,
        texts,
        output_dimensionality=768,
    )
    # upsert - run in thread to avoid blocking
    def upsert():
        index.upsert(vectors=list(zip(ids,embeddings,metadatas)))


    await asyncio.to_thread(upsert)

    return {
        "filenames": processed_filenames,
        "num_chunks": len(all_chunks),
        "has_text_reports": True,
    }