import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()

class AuditEvent(BaseModel):
    """Audit event model"""
    eventId: str
    timestamp: str
    eventType: str
    description: str
    severity: str
    user: str
    systemComponent: str
    metadata: Optional[dict] = None
    complianceRelevance: Optional[str] = None

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[AuditEvent]
    pagination: dict

class ExportRequest(BaseModel):
    """Export request model"""
    format: str = "csv"  # csv, json, pdf
    dateRange: Optional[dict] = None
    eventTypes: Optional[List[str]] = None
    severity: Optional[List[str]] = None

# Mock audit events storage
AUDIT_EVENTS = {}

@router.get("/events", response_model=PaginatedResponse)
async def get_audit_events(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated audit events with filtering"""
    try:
        # Filter events by user
        user_events = [
            event for event in AUDIT_EVENTS.values()
            if event.get("user") == current_user["email"]
        ]
        
        # Apply filters
        filtered_events = user_events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.get("eventType") == event_type]
        
        if severity:
            filtered_events = [e for e in filtered_events if e.get("severity") == severity]
        
        if start_date:
            filtered_events = [e for e in filtered_events if e.get("timestamp") >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events if e.get("timestamp") <= end_date]
        
        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Calculate pagination
        total = len(filtered_events)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        # Get page of events
        page_events = filtered_events[start_idx:end_idx]
        
        # Convert to AuditEvent
        audit_events = []
        for event in page_events:
            audit_event = AuditEvent(
                eventId=event["eventId"],
                timestamp=event["timestamp"],
                eventType=event["eventType"],
                description=event["description"],
                severity=event["severity"],
                user=event["user"],
                systemComponent=event["systemComponent"],
                metadata=event.get("metadata"),
                complianceRelevance=event.get("complianceRelevance")
            )
            audit_events.append(audit_event)
        
        return PaginatedResponse(
            data=audit_events,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit events: {str(e)}")

@router.get("/events/{event_id}", response_model=AuditEvent)
async def get_audit_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific audit event"""
    try:
        if event_id not in AUDIT_EVENTS:
            raise HTTPException(status_code=404, detail="Audit event not found")
        
        event = AUDIT_EVENTS[event_id]
        
        # Check if user has access to this event
        if event.get("user") != current_user["email"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return AuditEvent(
            eventId=event["eventId"],
            timestamp=event["timestamp"],
            eventType=event["eventType"],
            description=event["description"],
            severity=event["severity"],
            user=event["user"],
            systemComponent=event["systemComponent"],
            metadata=event.get("metadata"),
            complianceRelevance=event.get("complianceRelevance")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve audit event: {str(e)}")

@router.post("/generate")
async def generate_audit_trail(
    document_id: str,
    current_user: dict = Depends(require_permissions(["audit"])),
    agent_service: AgentService = Depends()
):
    """Generate audit trail for a document"""
    try:
        # Import document store from documents endpoint
        from .documents import DOCUMENT_STORE
        
        if document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = DOCUMENT_STORE[document_id]
        document = doc_data["document"]
        
        # Get processing history
        processing_history = agent_service.get_all_processing_history()
        relevant_history = [
            h for h in processing_history
            if h.get("document_id") == document_id
        ]
        
        # Generate audit trail using agent service
        audit_result = await agent_service.generate_audit_trail(
            document=document,
            processing_history=relevant_history
        )
        
        # Create audit events from the result
        if audit_result["status"] == "completed" and audit_result["result"]:
            audit_data = audit_result["result"]
            audit_events = audit_data.get("audit_events", [])
            
            # Store audit events
            for event in audit_events:
                event_id = event.get("event_id", str(uuid.uuid4()))
                AUDIT_EVENTS[event_id] = {
                    "eventId": event_id,
                    "timestamp": event.get("timestamp", datetime.utcnow().isoformat()),
                    "eventType": event.get("event_type", "audit_generated"),
                    "description": event.get("description", ""),
                    "severity": event.get("severity", "LOW"),
                    "user": current_user["email"],
                    "systemComponent": event.get("system_component", "audit_agent"),
                    "metadata": event.get("metadata", {}),
                    "complianceRelevance": event.get("compliance_relevance", "")
                }
        
        return {
            "status": audit_result["status"],
            "audit_id": audit_result["result"].get("audit_id") if audit_result["result"] else None,
            "confidence": audit_result.get("confidence", 0.0),
            "rationale": audit_result.get("rationale", ""),
            "events_generated": len(audit_result["result"].get("audit_events", [])) if audit_result["result"] else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audit trail: {str(e)}")

@router.post("/export")
async def export_audit_log(
    request: ExportRequest,
    current_user: dict = Depends(require_permissions(["export"]))
):
    """Export audit log in specified format"""
    try:
        # Filter events by user
        user_events = [
            event for event in AUDIT_EVENTS.values()
            if event.get("user") == current_user["email"]
        ]
        
        # Apply filters
        filtered_events = user_events
        
        if request.dateRange:
            start_date = request.dateRange.get("start")
            end_date = request.dateRange.get("end")
            
            if start_date:
                filtered_events = [e for e in filtered_events if e.get("timestamp") >= start_date]
            if end_date:
                filtered_events = [e for e in filtered_events if e.get("timestamp") <= end_date]
        
        if request.eventTypes:
            filtered_events = [e for e in filtered_events if e.get("eventType") in request.eventTypes]
        
        if request.severity:
            filtered_events = [e for e in filtered_events if e.get("severity") in request.severity]
        
        # Generate export based on format
        if request.format.lower() == "csv":
            # Generate CSV content
            csv_content = "Event ID,Timestamp,Event Type,Description,Severity,User,System Component,Compliance Relevance\n"
            for event in filtered_events:
                csv_content += f"{event['eventId']},{event['timestamp']},{event['eventType']},{event['description']},{event['severity']},{event['user']},{event['systemComponent']},{event.get('complianceRelevance', '')}\n"
            
            return {
                "format": "csv",
                "content": csv_content,
                "filename": f"audit_log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                "total_events": len(filtered_events)
            }
        
        elif request.format.lower() == "json":
            return {
                "format": "json",
                "content": filtered_events,
                "filename": f"audit_log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                "total_events": len(filtered_events)
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported export format: {request.format}")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export audit log: {str(e)}")

@router.get("/stats/summary")
async def get_audit_stats(current_user: dict = Depends(get_current_user)):
    """Get audit statistics"""
    try:
        # Filter events by user
        user_events = [
            event for event in AUDIT_EVENTS.values()
            if event.get("user") == current_user["email"]
        ]
        
        total_events = len(user_events)
        
        # Count by event type
        event_type_counts = {}
        for event in user_events:
            event_type = event.get("eventType", "unknown")
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        # Count by severity
        severity_counts = {}
        for event in user_events:
            severity = event.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by system component
        component_counts = {}
        for event in user_events:
            component = event.get("systemComponent", "unknown")
            component_counts[component] = component_counts.get(component, 0) + 1
        
        # Calculate compliance events
        compliance_events = len([
            e for e in user_events
            if e.get("complianceRelevance") and "compliance" in e.get("complianceRelevance", "").lower()
        ])
        
        return {
            "total_events": total_events,
            "event_type_distribution": event_type_counts,
            "severity_distribution": severity_counts,
            "component_distribution": component_counts,
            "compliance_events": compliance_events,
            "compliance_percentage": (compliance_events / total_events * 100) if total_events > 0 else 0.0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit statistics: {str(e)}")

@router.post("/events")
async def create_audit_event(
    event_type: str,
    description: str,
    severity: str = "LOW",
    system_component: str = "user_action",
    metadata: Optional[dict] = None,
    compliance_relevance: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new audit event"""
    try:
        event_id = str(uuid.uuid4())
        
        audit_event = {
            "eventId": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "eventType": event_type,
            "description": description,
            "severity": severity,
            "user": current_user["email"],
            "systemComponent": system_component,
            "metadata": metadata or {},
            "complianceRelevance": compliance_relevance
        }
        
        AUDIT_EVENTS[event_id] = audit_event
        
        return {
            "status": "success",
            "event_id": event_id,
            "message": "Audit event created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create audit event: {str(e)}")

@router.get("/compliance/report")
async def get_compliance_report(
    document_id: Optional[str] = None,
    current_user: dict = Depends(require_permissions(["audit"])),
    agent_service: AgentService = Depends()
):
    """Generate compliance report"""
    try:
        if document_id:
            # Import document store from documents endpoint
            from .documents import DOCUMENT_STORE
            
            if document_id not in DOCUMENT_STORE:
                raise HTTPException(status_code=404, detail="Document not found")
            
            doc_data = DOCUMENT_STORE[document_id]
            document = doc_data["document"]
            
            # Generate compliance report using agent service
            audit_result = await agent_service.generate_audit_trail(
                document=document,
                processing_history=[]
            )
            
            if audit_result["status"] == "completed" and audit_result["result"]:
                audit_data = audit_result["result"]
                compliance_report = audit_data.get("compliance_report", {})
                
                return {
                    "status": "success",
                    "compliance_score": compliance_report.get("overall_compliance_score", 0.0),
                    "compliance_summary": compliance_report.get("compliance_summary", ""),
                    "regulatory_implications": compliance_report.get("regulatory_implications", ""),
                    "findings": compliance_report.get("compliance_findings", []),
                    "next_steps": compliance_report.get("next_steps", [])
                }
        
        # Generate general compliance report
        user_events = [
            event for event in AUDIT_EVENTS.values()
            if event.get("user") == current_user["email"]
        ]
        
        compliance_events = [
            e for e in user_events
            if e.get("complianceRelevance") and "compliance" in e.get("complianceRelevance", "").lower()
        ]
        
        high_severity_events = [
            e for e in user_events
            if e.get("severity") in ["HIGH", "CRITICAL"]
        ]
        
        return {
            "status": "success",
            "total_events": len(user_events),
            "compliance_events": len(compliance_events),
            "high_severity_events": len(high_severity_events),
            "compliance_percentage": (len(compliance_events) / len(user_events) * 100) if user_events else 0.0,
            "risk_level": "LOW" if len(high_severity_events) == 0 else "MEDIUM" if len(high_severity_events) < 5 else "HIGH"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance report: {str(e)}")
