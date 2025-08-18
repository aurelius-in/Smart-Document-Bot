import os
import shutil
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...core.config import settings
from ...services.agent_service import AgentService
from ...models.base import Document, DocumentType

router = APIRouter()

class DocumentInfo(BaseModel):
    """Document information model"""
    id: str
    filename: str
    size: int
    type: str
    status: str
    uploadedAt: str
    processedAt: Optional[str] = None
    metadata: Optional[dict] = None
    extractedText: Optional[str] = None
    entities: Optional[List[dict]] = None
    confidence: Optional[float] = None

class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    fileId: str
    filename: str
    size: int
    status: str
    message: Optional[str] = None

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[DocumentInfo]
    pagination: dict

# Mock document storage
DOCUMENT_STORE = {}

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    process_immediately: bool = Form(False),
    goal: Optional[str] = Form("Analyze document for compliance and risks"),
    current_user: dict = Depends(get_current_user),
    agent_service: AgentService = Depends()
):
    """Upload and optionally process a document"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(settings.UPLOAD_DIR, document_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create document object
        document = Document(
            id=document_id,
            filename=file.filename,
            content="",  # Will be extracted during processing
            doc_type=DocumentType.UNKNOWN,
            metadata={
                "file_path": file_path,
                "file_size": file_size,
                "content_type": file.content_type,
                "uploaded_by": current_user["email"],
                "uploaded_at": datetime.utcnow().isoformat()
            }
        )
        
        # Store document
        DOCUMENT_STORE[document_id] = {
            "document": document,
            "status": "uploaded",
            "uploaded_at": datetime.utcnow().isoformat(),
            "processed_at": None,
            "processing_result": None
        }
        
        # Process immediately if requested
        if process_immediately:
            # Extract text first using ingestion agent
            ingestion_result = await agent_service.execute_single_agent(
                "ingestion", 
                document, 
                "Extract text from uploaded document"
            )
            
            if ingestion_result and ingestion_result.output:
                # Update document with extracted content
                document.content = ingestion_result.output.get("extracted_text", "")
                document.metadata.update({
                    "extraction_result": ingestion_result.output,
                    "extracted_at": datetime.utcnow().isoformat()
                })
                
                # Process through complete pipeline
                processing_result = await agent_service.process_document(document, goal)
                
                # Update document store
                DOCUMENT_STORE[document_id].update({
                    "status": processing_result["status"],
                    "processed_at": datetime.utcnow().isoformat(),
                    "processing_result": processing_result,
                    "document": document
                })
                
                return DocumentUploadResponse(
                    fileId=document_id,
                    filename=file.filename,
                    size=file_size,
                    status=processing_result["status"],
                    message=f"Document processed with {processing_result['confidence']:.2f} confidence"
                )
        
        return DocumentUploadResponse(
            fileId=document_id,
            filename=file.filename,
            size=file_size,
            status="uploaded",
            message="Document uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=PaginatedResponse)
async def get_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated list of documents"""
    try:
        # Get all documents
        all_documents = list(DOCUMENT_STORE.values())
        
        # Calculate pagination
        total = len(all_documents)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get page of documents
        page_documents = all_documents[start_idx:end_idx]
        
        # Convert to DocumentInfo
        document_infos = []
        for doc_data in page_documents:
            document = doc_data["document"]
            processing_result = doc_data.get("processing_result", {})
            
            # Extract entities from processing result
            entities = []
            if processing_result and processing_result.get("result"):
                orchestration_result = processing_result["result"]
                if orchestration_result and "execution_results" in orchestration_result:
                    entity_result = orchestration_result["execution_results"].get("stage_3")  # Entity stage
                    if entity_result and entity_result.output:
                        entities = entity_result.output.get("entities", [])
            
            document_info = DocumentInfo(
                id=document.id,
                filename=document.filename,
                size=document.metadata.get("file_size", 0),
                type=document.doc_type.value if document.doc_type else "unknown",
                status=doc_data["status"],
                uploadedAt=doc_data["uploaded_at"],
                processedAt=doc_data.get("processed_at"),
                metadata=document.metadata,
                extractedText=document.content[:500] + "..." if len(document.content) > 500 else document.content,
                entities=entities,
                confidence=processing_result.get("confidence", 0.0) if processing_result else None
            )
            document_infos.append(document_info)
        
        return PaginatedResponse(
            data=document_infos,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific document by ID"""
    try:
        if document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = DOCUMENT_STORE[document_id]
        document = doc_data["document"]
        processing_result = doc_data.get("processing_result", {})
        
        # Extract entities from processing result
        entities = []
        if processing_result and processing_result.get("result"):
            orchestration_result = processing_result["result"]
            if orchestration_result and "execution_results" in orchestration_result:
                entity_result = orchestration_result["execution_results"].get("stage_3")  # Entity stage
                if entity_result and entity_result.output:
                    entities = entity_result.output.get("entities", [])
        
        return DocumentInfo(
            id=document.id,
            filename=document.filename,
            size=document.metadata.get("file_size", 0),
            type=document.doc_type.value if document.doc_type else "unknown",
            status=doc_data["status"],
            uploadedAt=doc_data["uploaded_at"],
            processedAt=doc_data.get("processed_at"),
            metadata=document.metadata,
            extractedText=document.content,
            entities=entities,
            confidence=processing_result.get("confidence", 0.0) if processing_result else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    goal: str = "Analyze document for compliance and risks",
    current_user: dict = Depends(require_permissions(["analyze"])),
    agent_service: AgentService = Depends()
):
    """Process a document through the agent pipeline"""
    try:
        if document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = DOCUMENT_STORE[document_id]
        document = doc_data["document"]
        
        # Check if document has content, if not extract it first
        if not document.content:
            ingestion_result = await agent_service.execute_single_agent(
                "ingestion", 
                document, 
                "Extract text from document"
            )
            
            if ingestion_result and ingestion_result.output:
                document.content = ingestion_result.output.get("extracted_text", "")
                document.metadata.update({
                    "extraction_result": ingestion_result.output,
                    "extracted_at": datetime.utcnow().isoformat()
                })
        
        # Process through complete pipeline
        processing_result = await agent_service.process_document(document, goal)
        
        # Update document store
        DOCUMENT_STORE[document_id].update({
            "status": processing_result["status"],
            "processed_at": datetime.utcnow().isoformat(),
            "processing_result": processing_result,
            "document": document
        })
        
        return {
            "status": "success",
            "processing_id": processing_result.get("processing_id"),
            "confidence": processing_result.get("confidence", 0.0),
            "rationale": processing_result.get("rationale", ""),
            "workflow_status": processing_result.get("workflow_status", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(require_permissions(["delete"]))
):
    """Delete a document"""
    try:
        if document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = DOCUMENT_STORE[document_id]
        document = doc_data["document"]
        
        # Delete file from filesystem
        file_path = document.metadata.get("file_path")
        if file_path and os.path.exists(file_path):
            upload_dir = os.path.dirname(file_path)
            shutil.rmtree(upload_dir, ignore_errors=True)
        
        # Remove from store
        del DOCUMENT_STORE[document_id]
        
        return {"status": "success", "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/stats/summary")
async def get_document_stats(current_user: dict = Depends(get_current_user)):
    """Get document statistics"""
    try:
        total_documents = len(DOCUMENT_STORE)
        processed_documents = len([d for d in DOCUMENT_STORE.values() if d["status"] == "completed"])
        failed_documents = len([d for d in DOCUMENT_STORE.values() if d["status"] == "failed"])
        uploaded_documents = len([d for d in DOCUMENT_STORE.values() if d["status"] == "uploaded"])
        
        # Calculate average confidence
        confidences = []
        for doc_data in DOCUMENT_STORE.values():
            processing_result = doc_data.get("processing_result", {})
            if processing_result and "confidence" in processing_result:
                confidences.append(processing_result["confidence"])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            "total_documents": total_documents,
            "processed_documents": processed_documents,
            "failed_documents": failed_documents,
            "uploaded_documents": uploaded_documents,
            "average_confidence": avg_confidence,
            "success_rate": (processed_documents / total_documents * 100) if total_documents > 0 else 0.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
