from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from pydantic import BaseModel
import json
import zipfile
import io
from datetime import datetime
import csv

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


class AuditEvent(BaseModel):
    """Audit event model"""
    id: str
    timestamp: str
    userId: str
    userName: str
    action: str
    resource: str
    resourceId: str
    severity: str
    category: str
    details: str
    ipAddress: str
    userAgent: str
    sessionId: str
    metadata: Optional[dict] = None
    complianceTags: Optional[List[str]] = None


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[AuditEvent]
    pagination: dict


class ExportRequest(BaseModel):
    """Export request model"""
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    user: Optional[str] = None
    searchTerm: Optional[str] = None


# Mock audit events storage - in production, this would be a database
AUDIT_EVENTS = [
    {
        "id": "audit_001",
        "timestamp": "2024-01-15T10:30:00Z",
        "userId": "user_001",
        "userName": "admin@redline.com",
        "action": "document_upload",
        "resource": "Contract_V1.pdf",
        "resourceId": "doc_001",
        "severity": "medium",
        "category": "document",
        "details": "Uploaded contract document for processing",
        "ipAddress": "192.168.1.100",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "sessionId": "sess_12345",
        "metadata": {"file_size": 1024000, "content_type": "application/pdf"},
        "complianceTags": ["SOX", "GDPR"]
    },
    {
        "id": "audit_002",
        "timestamp": "2024-01-15T10:35:00Z",
        "userId": "system",
        "userName": "system",
        "action": "document_processed",
        "resource": "Contract_V1.pdf",
        "resourceId": "doc_001",
        "severity": "low",
        "category": "system",
        "details": "Document processed successfully by AI agent",
        "ipAddress": "127.0.0.1",
        "userAgent": "REDLINE-Agent/1.0",
        "sessionId": "sess_system",
        "metadata": {"processing_time": 2500, "confidence": 0.89, "extracted_entities": 15},
        "complianceTags": []
    },
    {
        "id": "audit_003",
        "timestamp": "2024-01-15T11:00:00Z",
        "userId": "user_002",
        "userName": "user@redline.com",
        "action": "document_compare",
        "resource": "Contract_V1.pdf vs Contract_V2.pdf",
        "resourceId": "comp_001",
        "severity": "high",
        "category": "document",
        "details": "Compared contract versions - critical differences detected",
        "ipAddress": "192.168.1.101",
        "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "sessionId": "sess_67890",
        "metadata": {"differences": 5, "risk_level": "high", "compliance_impact": "significant"},
        "complianceTags": ["SOX", "Legal Review"]
    },
    {
        "id": "audit_004",
        "timestamp": "2024-01-15T11:30:00Z",
        "userId": "user_001",
        "userName": "admin@redline.com",
        "action": "settings_changed",
        "resource": "System Configuration",
        "resourceId": "config_001",
        "severity": "medium",
        "category": "system",
        "details": "Modified document processing settings",
        "ipAddress": "192.168.1.100",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "sessionId": "sess_12345",
        "metadata": {"setting": "ocr_confidence_threshold", "old_value": 0.8, "new_value": 0.9},
        "complianceTags": []
    },
    {
        "id": "audit_005",
        "timestamp": "2024-01-15T12:00:00Z",
        "userId": "system",
        "userName": "system",
        "action": "security_alert",
        "resource": "Authentication",
        "resourceId": "auth_001",
        "severity": "critical",
        "category": "security",
        "details": "Multiple failed login attempts detected",
        "ipAddress": "203.0.113.1",
        "userAgent": "Unknown",
        "sessionId": "sess_failed",
        "metadata": {"failed_attempts": 5, "blocked_ip": True},
        "complianceTags": ["Security", "Access Control"]
    }
]


@router.get("/events", response_model=PaginatedResponse)
async def get_audit_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get paginated audit events with filtering"""
    try:
        # Filter events based on parameters
        filtered_events = AUDIT_EVENTS.copy()
        
        if severity:
            filtered_events = [e for e in filtered_events if e["severity"] == severity]
        
        if category:
            filtered_events = [e for e in filtered_events if e["category"] == category]
        
        if user:
            filtered_events = [e for e in filtered_events if e["userName"] == user]
        
        if startDate:
            start_dt = datetime.fromisoformat(startDate.replace('Z', '+00:00'))
            filtered_events = [e for e in filtered_events if datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00')) >= start_dt]
        
        if endDate:
            end_dt = datetime.fromisoformat(endDate.replace('Z', '+00:00'))
            filtered_events = [e for e in filtered_events if datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00')) <= end_dt]
        
        if search:
            search_lower = search.lower()
            filtered_events = [
                e for e in filtered_events
                if search_lower in e["action"].lower() or
                   search_lower in e["details"].lower() or
                   search_lower in e["userName"].lower() or
                   search_lower in e["resource"].lower()
            ]
        
        # Calculate pagination
        total = len(filtered_events)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_events = filtered_events[start_idx:end_idx]
        
        # Convert to AuditEvent models
        audit_events = [
            AuditEvent(**event) for event in paginated_events
        ]
        
        return PaginatedResponse(
            data=audit_events,
            pagination={
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}", response_model=AuditEvent)
async def get_audit_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific audit event by ID"""
    try:
        event = next((e for e in AUDIT_EVENTS if e["id"] == event_id), None)
        if not event:
            raise HTTPException(status_code=404, detail="Audit event not found")
        
        return AuditEvent(**event)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_audit_log(
    startDate: Optional[str] = Query(None),
    endDate: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
    searchTerm: Optional[str] = Query(None),
    current_user: dict = Depends(require_permissions(["read"]))
):
    """Export audit log as CSV"""
    try:
        # Filter events based on parameters
        filtered_events = AUDIT_EVENTS.copy()
        
        if severity:
            filtered_events = [e for e in filtered_events if e["severity"] == severity]
        
        if category:
            filtered_events = [e for e in filtered_events if e["category"] == category]
        
        if user:
            filtered_events = [e for e in filtered_events if e["userName"] == user]
        
        if startDate:
            start_dt = datetime.fromisoformat(startDate.replace('Z', '+00:00'))
            filtered_events = [e for e in filtered_events if datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00')) >= start_dt]
        
        if endDate:
            end_dt = datetime.fromisoformat(endDate.replace('Z', '+00:00'))
            filtered_events = [e for e in filtered_events if datetime.fromisoformat(e["timestamp"].replace('Z', '+00:00')) <= end_dt]
        
        if searchTerm:
            search_lower = searchTerm.lower()
            filtered_events = [
                e for e in filtered_events
                if search_lower in e["action"].lower() or
                   search_lower in e["details"].lower() or
                   search_lower in e["userName"].lower() or
                   search_lower in e["resource"].lower()
            ]
        
        # Create CSV content
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        
        # Write header
        csv_writer.writerow([
            "ID", "Timestamp", "User ID", "User Name", "Action", "Resource", "Resource ID",
            "Severity", "Category", "Details", "IP Address", "User Agent", "Session ID",
            "Compliance Tags", "Metadata"
        ])
        
        # Write data
        for event in filtered_events:
            csv_writer.writerow([
                event["id"],
                event["timestamp"],
                event["userId"],
                event["userName"],
                event["action"],
                event["resource"],
                event["resourceId"],
                event["severity"],
                event["category"],
                event["details"],
                event["ipAddress"],
                event["userAgent"],
                event["sessionId"],
                ", ".join(event.get("complianceTags", [])),
                json.dumps(event.get("metadata", {}))
            ])
        
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()
        
        # Create response with CSV content
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=audit_log_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_audit_stats(current_user: dict = Depends(get_current_user)):
    """Get audit statistics"""
    try:
        total_events = len(AUDIT_EVENTS)
        
        # Count by severity
        severity_counts = {}
        for event in AUDIT_EVENTS:
            severity = event["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by category
        category_counts = {}
        for event in AUDIT_EVENTS:
            category = event["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Count by user
        user_counts = {}
        for event in AUDIT_EVENTS:
            user = event["userName"]
            user_counts[user] = user_counts.get(user, 0) + 1
        
        return {
            "total_events": total_events,
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "user_activity": user_counts,
            "recent_activity": {
                "last_24h": len([e for e in AUDIT_EVENTS if "2024-01-15" in e["timestamp"]]),
                "last_7d": len([e for e in AUDIT_EVENTS if "2024-01-15" in e["timestamp"]]),
                "last_30d": len([e for e in AUDIT_EVENTS if "2024-01-15" in e["timestamp"]])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Keep existing audit bundle endpoints
class AuditBundleRequest(BaseModel):
    """Audit bundle request model"""
    trace_id: str
    document_id: Optional[str] = None
    include_metadata: bool = True
    format: str = "json"  # json, csv, pdf, zip


class AuditBundleResponse(BaseModel):
    """Audit bundle response model"""
    bundle_id: str
    trace_id: str
    document_id: Optional[str]
    format: str
    size_bytes: int
    hash: str
    created_at: str


@router.get("/trails")
async def get_audit_trails(
    current_user: dict = Depends(get_current_user)
):
    """Get all audit trails"""
    # In a real implementation, this would fetch from database
    return {
        "audit_trails": [
            {
                "trail_id": "audit_123",
                "trace_id": "trace_456",
                "document_id": "doc_789",
                "created_at": "2024-01-01T00:00:00Z",
                "status": "completed",
                "entry_count": 15,
                "final_hash": "abc123..."
            }
        ]
    }


@router.get("/trails/{trail_id}")
async def get_audit_trail(
    trail_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific audit trail"""
    # In a real implementation, this would fetch from database
    return {
        "trail_id": trail_id,
        "trace_id": "trace_456",
        "document_id": "doc_789",
        "created_at": "2024-01-01T00:00:00Z",
        "status": "completed",
        "entries": [
            {
                "entry_id": 1,
                "timestamp": "2024-01-01T00:00:00Z",
                "agent": "ingestion",
                "action": "pdf_extract",
                "rationale": "Extracting text from PDF document",
                "confidence": 0.95,
                "duration_ms": 1500,
                "hash": "hash1..."
            }
        ],
        "final_hash": "abc123..."
    }


@router.post("/bundles", response_model=AuditBundleResponse)
async def create_audit_bundle(
    request: AuditBundleRequest,
    current_user: dict = Depends(require_permissions(["read"])),
    agent_service: AgentService = Depends()
):
    """Create an audit bundle for export"""
    try:
        # Get trace data
        trace_data = await agent_service.get_trace(request.trace_id)
        if not trace_data:
            raise HTTPException(status_code=404, detail="Trace not found")
        
        # Create bundle ID
        bundle_id = f"bundle_{request.trace_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create bundle content
        bundle_content = {
            "bundle_id": bundle_id,
            "trace_id": request.trace_id,
            "document_id": request.document_id,
            "created_at": datetime.now().isoformat(),
            "created_by": current_user["email"],
            "trace_data": trace_data,
            "metadata": {
                "format": request.format,
                "include_metadata": request.include_metadata
            }
        }
        
        # Calculate bundle hash
        import hashlib
        bundle_json = json.dumps(bundle_content, sort_keys=True, default=str)
        bundle_hash = hashlib.sha256(bundle_json.encode()).hexdigest()
        
        return AuditBundleResponse(
            bundle_id=bundle_id,
            trace_id=request.trace_id,
            document_id=request.document_id,
            format=request.format,
            size_bytes=len(bundle_json),
            hash=bundle_hash,
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bundles/{bundle_id}/download")
async def download_audit_bundle(
    bundle_id: str,
    format: str = "json",
    current_user: dict = Depends(require_permissions(["read"]))
):
    """Download an audit bundle"""
    try:
        # In a real implementation, this would fetch from database
        # For demo purposes, create sample bundle
        bundle_content = {
            "bundle_id": bundle_id,
            "trace_id": "trace_456",
            "document_id": "doc_789",
            "created_at": datetime.now().isoformat(),
            "created_by": current_user["email"],
            "audit_entries": [
                {
                    "entry_id": 1,
                    "timestamp": "2024-01-01T00:00:00Z",
                    "agent": "ingestion",
                    "action": "pdf_extract",
                    "rationale": "Extracting text from PDF document",
                    "confidence": 0.95,
                    "duration_ms": 1500
                }
            ],
            "findings": [
                {
                    "id": "finding_1",
                    "severity": "high",
                    "category": "compliance",
                    "description": "Missing privacy notice",
                    "policy_reference": "GDPR Article 13"
                }
            ],
            "entities": [
                {
                    "text": "John Doe",
                    "label": "PERSON",
                    "confidence": 0.9,
                    "page": 1
                }
            ]
        }
        
        if format == "json":
            return Response(
                content=json.dumps(bundle_content, indent=2),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={bundle_id}.json"}
            )
        
        elif format == "zip":
            # Create ZIP file with multiple formats
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add JSON version
                zip_file.writestr(f"{bundle_id}.json", json.dumps(bundle_content, indent=2))
                
                # Add CSV version (simplified)
                csv_content = "Entry ID,Timestamp,Agent,Action,Confidence\n"
                for entry in bundle_content["audit_entries"]:
                    csv_content += f"{entry['entry_id']},{entry['timestamp']},{entry['agent']},{entry['action']},{entry['confidence']}\n"
                zip_file.writestr(f"{bundle_id}.csv", csv_content)
                
                # Add summary text
                summary = f"Audit Bundle: {bundle_id}\n"
                summary += f"Created: {bundle_content['created_at']}\n"
                summary += f"Trace ID: {bundle_content['trace_id']}\n"
                summary += f"Total Entries: {len(bundle_content['audit_entries'])}\n"
                summary += f"Total Findings: {len(bundle_content['findings'])}\n"
                zip_file.writestr(f"{bundle_id}_summary.txt", summary)
            
            zip_buffer.seek(0)
            return Response(
                content=zip_buffer.getvalue(),
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={bundle_id}.zip"}
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bundles")
async def list_audit_bundles(
    current_user: dict = Depends(get_current_user)
):
    """List all audit bundles"""
    # In a real implementation, this would fetch from database
    return {
        "bundles": [
            {
                "bundle_id": "bundle_123",
                "trace_id": "trace_456",
                "document_id": "doc_789",
                "format": "json",
                "size_bytes": 1024,
                "hash": "abc123...",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
    }


@router.get("/validation/{bundle_id}")
async def validate_audit_bundle(
    bundle_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Validate audit bundle integrity"""
    # In a real implementation, this would validate the bundle hash
    return {
        "bundle_id": bundle_id,
        "integrity_valid": True,
        "calculated_hash": "abc123...",
        "stored_hash": "abc123...",
        "validation_timestamp": datetime.now().isoformat(),
        "validation_status": "passed"
    }


@router.get("/metrics")
async def get_audit_metrics(
    current_user: dict = Depends(require_permissions(["read"]))
):
    """Get audit metrics and statistics"""
    return {
        "total_trails": 150,
        "total_bundles": 75,
        "avg_entries_per_trail": 12.5,
        "compliance_score": 0.85,
        "recent_activity": [
            {
                "date": "2024-01-01",
                "trails_created": 5,
                "bundles_exported": 3
            }
        ]
    }
