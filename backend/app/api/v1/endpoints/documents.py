import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...core.config import settings
from ...services.agent_service import AgentService

router = APIRouter()


class DocumentInfo(BaseModel):
    """Document information model"""
    filename: str
    file_path: str
    file_size: int
    content_type: str
    uploaded_at: str


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    file_path: str
    file_size: int
    status: str
    trace_id: Optional[str] = None


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    process_immediately: bool = Form(False),
    goal: Optional[str] = Form("Analyze document for compliance and risks"),
    current_user: str = Depends(require_permissions(["write"])),
    agent_service: AgentService = Depends()
):
    """Upload and optionally process a document"""
    
    # Validate file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size {file.size} exceeds maximum allowed size of {settings.MAX_FILE_SIZE}"
        )
    
    try:
        # Create unique filename
        import uuid
        document_id = str(uuid.uuid4())
        filename = f"{document_id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Process document if requested
        trace_id = None
        if process_immediately:
            result = await agent_service.process_document(file_path, goal)
            trace_id = result.get("trace_id")
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            status="uploaded" if not process_immediately else "processed",
            trace_id=trace_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    goal: str = "Analyze document for compliance and risks",
    current_user: str = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Process an uploaded document"""
    try:
        # Find document file
        document_files = [
            f for f in os.listdir(settings.UPLOAD_DIR)
            if f.startswith(document_id)
        ]
        
        if not document_files:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path = os.path.join(settings.UPLOAD_DIR, document_files[0])
        
        # Process document
        result = await agent_service.process_document(file_path, goal)
        
        return {
            "document_id": document_id,
            "trace_id": result["trace_id"],
            "status": result["status"],
            "confidence": result.get("confidence", 0.0),
            "duration_ms": result.get("duration_ms", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_documents(
    current_user: str = Depends(get_current_user)
):
    """List all uploaded documents"""
    try:
        documents = []
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename.endswith(tuple(settings.ALLOWED_FILE_TYPES)):
                file_path = os.path.join(settings.UPLOAD_DIR, filename)
                file_size = os.path.getsize(file_path)
                
                # Extract document ID from filename
                document_id = filename.split("_")[0]
                
                documents.append({
                    "document_id": document_id,
                    "filename": "_".join(filename.split("_")[1:]),
                    "file_path": file_path,
                    "file_size": file_size,
                    "uploaded_at": "2024-01-01T00:00:00Z"  # Would get from metadata in real implementation
                })
        
        return {"documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: str = Depends(require_permissions(["delete"]))
):
    """Delete a document"""
    try:
        # Find document file
        document_files = [
            f for f in os.listdir(settings.UPLOAD_DIR)
            if f.startswith(document_id)
        ]
        
        if not document_files:
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path = os.path.join(settings.UPLOAD_DIR, document_files[0])
        os.remove(file_path)
        
        return {"message": "Document deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
