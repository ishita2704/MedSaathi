import time
import traceback
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from ..auth.route import authenticate
from ..config.db import reports_collection
from .vectorstore import load_vectorstore, save_image_upload


router=APIRouter(prefix="/reports",tags=["reports"])

@router.post("/upload")
async def upload_reports(
    user=Depends(authenticate),
    files: Optional[List[UploadFile]] = File(default=None),
    ct_scan: Optional[UploadFile] = File(default=None),
    xray: Optional[UploadFile] = File(default=None),
):
    if user["role"] !="patient":
        raise HTTPException(status_code=403,detail="Only patients can upload reports for diagnosis")

    if not files and not ct_scan and not xray:
        raise HTTPException(
            status_code=400,
            detail="Upload at least one PDF/TXT report or one CT/X-ray image.",
        )

    doc_id=str(uuid.uuid4())
    try:
        text_result = {
            "filenames": [],
            "num_chunks": 0,
            "has_text_reports": False,
        }
        if files:
            text_result = await load_vectorstore(files, uploaded=user["username"], doc_id=doc_id)

        image_records = {}
        if ct_scan:
            image_records["ct_scan"] = await save_image_upload(ct_scan, doc_id, "ct_scan")
        if xray:
            image_records["xray"] = await save_image_upload(xray, doc_id, "xray")

        reports_collection.insert_one({
            "doc_id": doc_id,
            "uploader": user["username"],
            "text_filenames": text_result["filenames"],
            "num_chunks": text_result["num_chunks"],
            "has_text_reports": text_result["has_text_reports"],
            "image_files": image_records,
            "uploaded_at": time.time(),
        })

        upload_types = []
        if text_result["has_text_reports"]:
            upload_types.append("reports")
        if "ct_scan" in image_records:
            upload_types.append("ct_scan")
        if "xray" in image_records:
            upload_types.append("xray")

        return {
            "message": "Uploaded and indexed",
            "doc_id": doc_id,
            "upload_types": upload_types,
        }
    except Exception as e:
        error_details = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}\n\nTraceback: {error_details}")