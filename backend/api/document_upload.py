# Document Upload API Endpoint
# Purpose: Handle file uploads from frontend and store for processing

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/api", tags=["documents"])

# Configure upload directory
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    thread_id: str = Form(...)
):
    """
    Upload document files for visa application processing.
    
    Args:
        file: Uploaded file (passport, photo, etc.)
        document_type: Type of document (passport_bio_page, passport_photo)
        thread_id: Thread ID for the visa application
    
    Returns:
        File upload confirmation with storage path
    """
    
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not allowed. Use JPEG, PNG, or PDF."
            )
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Create thread-specific directory
        thread_dir = os.path.join(UPLOAD_DIR, thread_id)
        os.makedirs(thread_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{document_type}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = os.path.join(thread_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "file_path": file_path,
            "document_type": document_type,
            "thread_id": thread_id,
            "filename": unique_filename,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "file_size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"File upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail="File upload failed. Please try again."
        )


@router.get("/uploads/{thread_id}/{filename}")
async def get_uploaded_file(thread_id: str, filename: str):
    """Retrieve uploaded file (for testing/verification)"""
    
    try:
        file_path = os.path.join(UPLOAD_DIR, thread_id, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file info (in production, you might serve the actual file)
        file_stats = os.stat(file_path)
        
        return {
            "thread_id": thread_id,
            "filename": filename,
            "file_path": file_path,
            "file_size": file_stats.st_size,
            "upload_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"File retrieval error: {e}")
        raise HTTPException(status_code=500, detail="File retrieval failed")


@router.delete("/uploads/{thread_id}/{filename}")
async def delete_uploaded_file(thread_id: str, filename: str):
    """Delete uploaded file"""
    
    try:
        file_path = os.path.join(UPLOAD_DIR, thread_id, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"status": "success", "message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"File deletion error: {e}")
        raise HTTPException(status_code=500, detail="File deletion failed")