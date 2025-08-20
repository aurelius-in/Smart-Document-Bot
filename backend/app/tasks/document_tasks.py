"""
Document Processing Tasks for AI Document Agent
Handles document upload, processing, and analysis tasks
"""

import os
import logging
from typing import Dict, Any, Optional
from celery import current_task
from ..core.celery_config import celery_app
from ..services.agent_service import AgentService
from ..services.memory_service import MemoryService
from ..database.connection import get_db
from ..database.models import Document, ProcessingHistory
from ..core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: int, user_id: int) -> Dict[str, Any]:
    """
    Process a document through the complete AI pipeline
    
    Args:
        document_id: ID of the document to process
        user_id: ID of the user who uploaded the document
        
    Returns:
        Dictionary containing processing results
    """
    try:
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Starting document processing"}
        )
        
        # Get database session
        db = next(get_db())
        
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Initialize services
        agent_service = AgentService()
        memory_service = MemoryService()
        
        # Step 1: Extract text (10%)
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Extracting text"}
        )
        
        text_result = extract_text.delay(document_id)
        extracted_text = text_result.get(timeout=300)
        
        # Step 2: Classify document (20%)
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Classifying document"}
        )
        
        classification_result = classify_document.delay(document_id, extracted_text)
        classification = classification_result.get(timeout=300)
        
        # Step 3: Extract entities (40%)
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 40, "total": 100, "status": "Extracting entities"}
        )
        
        entities_result = extract_entities.delay(document_id, extracted_text)
        entities = entities_result.get(timeout=300)
        
        # Step 4: Assess risk (60%)
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Assessing risk"}
        )
        
        risk_result = assess_risk.delay(document_id, extracted_text, entities)
        risk_assessment = risk_result.get(timeout=300)
        
        # Step 5: Store in vector database (80%)
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 80, "total": 100, "status": "Storing in vector database"}
        )
        
        # Store document in vector database
        await memory_service.store_long_term(
            f"doc_{document_id}",
            extracted_text,
            metadata={
                "document_id": document_id,
                "user_id": user_id,
                "classification": classification,
                "entities": entities,
                "risk_assessment": risk_assessment
            }
        )
        
        # Step 6: Update document status (100%)
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 100, "total": 100, "status": "Completing processing"}
        )
        
        # Update document status
        document.status = "processed"
        document.processing_progress = 100
        db.commit()
        
        # Log processing history
        history = ProcessingHistory(
            document_id=document_id,
            stage="complete",
            status="success",
            details={
                "classification": classification,
                "entities_count": len(entities),
                "risk_score": risk_assessment.get("risk_score", 0)
            }
        )
        db.add(history)
        db.commit()
        
        return {
            "document_id": document_id,
            "status": "success",
            "classification": classification,
            "entities": entities,
            "risk_assessment": risk_assessment,
            "processing_time": current_task.request.execution_time
        }
        
    except Exception as exc:
        logger.error(f"Document processing failed: {exc}")
        
        # Update document status
        if 'document' in locals():
            document.status = "failed"
            document.processing_error = str(exc)
            db.commit()
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        else:
            raise exc

@celery_app.task(bind=True, max_retries=3)
def extract_text(self, document_id: int) -> str:
    """Extract text from document"""
    try:
        db = next(get_db())
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Use ingestion agent to extract text
        agent_service = AgentService()
        result = await agent_service.ingestion_agent.run(
            "Extract text from document",
            {"document_path": document.file_path}
        )
        
        # Update document with extracted text
        document.extracted_text = result.get("text", "")
        db.commit()
        
        return document.extracted_text
        
    except Exception as exc:
        logger.error(f"Text extraction failed: {exc}")
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        else:
            raise exc

@celery_app.task(bind=True, max_retries=3)
def classify_document(self, document_id: int, text: str) -> Dict[str, Any]:
    """Classify document type and domain"""
    try:
        agent_service = AgentService()
        result = await agent_service.classifier_agent.run(
            "Classify document type and domain",
            {"text": text}
        )
        
        return result
        
    except Exception as exc:
        logger.error(f"Document classification failed: {exc}")
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        else:
            raise exc

@celery_app.task(bind=True, max_retries=3)
def extract_entities(self, document_id: int, text: str) -> Dict[str, Any]:
    """Extract named entities from document"""
    try:
        agent_service = AgentService()
        result = await agent_service.entity_agent.run(
            "Extract named entities from text",
            {"text": text}
        )
        
        return result
        
    except Exception as exc:
        logger.error(f"Entity extraction failed: {exc}")
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        else:
            raise exc

@celery_app.task(bind=True, max_retries=3)
def assess_risk(self, document_id: int, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
    """Assess document risk and compliance"""
    try:
        agent_service = AgentService()
        result = await agent_service.risk_agent.run(
            "Assess document risk and compliance",
            {"text": text, "entities": entities}
        )
        
        return result
        
    except Exception as exc:
        logger.error(f"Risk assessment failed: {exc}")
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        else:
            raise exc

@celery_app.task(bind=True, max_retries=3)
def compare_documents(self, document1_id: int, document2_id: int) -> Dict[str, Any]:
    """Compare two documents for similarities and differences"""
    try:
        agent_service = AgentService()
        result = await agent_service.compare_agent.run(
            "Compare two documents",
            {"document1_id": document1_id, "document2_id": document2_id}
        )
        
        return result
        
    except Exception as exc:
        logger.error(f"Document comparison failed: {exc}")
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        else:
            raise exc

@celery_app.task
def process_pending_documents():
    """Process all pending documents in the queue"""
    try:
        db = next(get_db())
        pending_documents = db.query(Document).filter(
            Document.status == "pending"
        ).limit(10).all()
        
        for document in pending_documents:
            process_document.delay(document.id, document.user_id)
            
        return {"processed": len(pending_documents)}
        
    except Exception as exc:
        logger.error(f"Pending document processing failed: {exc}")
        raise exc
