"""Image upload endpoint"""
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io

router = APIRouter()

# Ensure uploads directory exists
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
MAX_FILE_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10485760))  # 10MB default

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Upload an image file for product search.
    
    Returns:
        - file_id: Unique identifier for the uploaded image
        - filename: Original filename
        - size: File size in bytes
        - format: Image format (jpeg, png, etc.)
    """
    try:
        # Validate file extension if present; fall back to PIL format detection
        _, ext = os.path.splitext(file.filename or "")
        
        # Read file content
        content = await file.read()
        
        # Check file size
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )
        
        # Validate image and determine format
        try:
            img = Image.open(io.BytesIO(content))
            img_format = (img.format or "JPEG").upper()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

        # Ensure extension is allowed; if missing or unknown, infer from PIL format
        if not ext:
            ext = f".{img_format.lower()}"

        if ext.lower() not in ALLOWED_EXTENSIONS:
            # Sometimes PIL reports formats like 'MPO' etc. Try to map common ones
            inferred_ext = f".{img_format.lower()}"
            if inferred_ext not in ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            ext = inferred_ext
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_ext = ext.lower()
        saved_filename = f"{file_id}{file_ext}"
        saved_path = os.path.join(UPLOADS_DIR, saved_filename)
        
        # Save file
        with open(saved_path, "wb") as f:
            f.write(content)
        
        return JSONResponse({
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "format": img_format,
            "timestamp": datetime.now().isoformat()
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/upload/history")
async def get_upload_history():
    """Get list of recently uploaded images"""
    try:
        files = []
        if os.path.exists(UPLOADS_DIR):
            for filename in sorted(os.listdir(UPLOADS_DIR), reverse=True)[:50]:
                filepath = os.path.join(UPLOADS_DIR, filename)
                if os.path.isfile(filepath):
                    file_id = os.path.splitext(filename)[0]
                    files.append({
                        "file_id": file_id,
                        "filename": filename,
                        "size": os.path.getsize(filepath),
                        "timestamp": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    })
        return JSONResponse({"files": files})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
