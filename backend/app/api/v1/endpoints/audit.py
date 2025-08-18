from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
import json
import zipfile
import io
from datetime import datetime

from ...core.security import get_current_user, require_permissions
from ...services.agent_service import AgentService

router = APIRouter()


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
    current_user: str = Depends(get_current_user)
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
    current_user: str = Depends(get_current_user)
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
    current_user: str = Depends(require_permissions(["read"])),
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
            "created_by": current_user,
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
    current_user: str = Depends(require_permissions(["read"]))
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
            "created_by": current_user,
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
    current_user: str = Depends(get_current_user)
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
    current_user: str = Depends(get_current_user)
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
    current_user: str = Depends(require_permissions(["read"]))
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
