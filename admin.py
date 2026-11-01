
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Complaint, ComplaintAttachment, AdminRemark

router = APIRouter(prefix="/admin", tags=["Admin"])


class ComplaintUpdate(BaseModel):
    query_description: str | None = None
    department: str | None = None
    importance_score: int | None = None
    user_name: str | None = None
    email_id: str | None = None
    phone_number: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    location: str | None = None
    status: str | None = None


class RemarkCreate(BaseModel):
    remark: str


def complaint_to_dict(complaint, db):
    attachments = (
        db.query(ComplaintAttachment)
        .filter(ComplaintAttachment.complaint_id == complaint.id)
        .all()
    )

    return {
        "id": complaint.id,
        "query_description": complaint.query_description,
        "department": complaint.department,
        "importance_score": complaint.importance_score,
        "user_name": complaint.user_name,
        "email_id": complaint.email_id,
        "phone_number": complaint.phone_number,
        "latitude": complaint.latitude,
        "longitude": complaint.longitude,
        "location": complaint.location,
        "status": complaint.status,
        "attachments": [
            {
                "id": a.id,
                "storage_key": a.storage_key,
                "mime_type": a.mime_type,
                "file_size": a.file_size,
            }
            for a in attachments
        ],
    }


@router.get("/complaints")
def get_complaints(db: Session = Depends(get_db)):
    complaints = (
        db.query(Complaint)
        .order_by(Complaint.id.desc())
        .all()
    )

    return [complaint_to_dict(c, db) for c in complaints]


@router.get("/complaints/{complaint_id}")
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    result = complaint_to_dict(complaint, db)

    remarks = (
        db.query(AdminRemark)
        .filter(AdminRemark.complaint_id == complaint_id)
        .order_by(AdminRemark.created_at.desc())
        .all()
    )

    result["remarks"] = [
        {
            "id": r.id,
            "remark": r.remark,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in remarks
    ]

    return result


@router.patch("/complaints/{complaint_id}")
def update_complaint(
    complaint_id: int,
    updates: ComplaintUpdate,
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    changes = updates.model_dump(exclude_unset=True)

    non_nullable = {
        "query_description",
        "department",
        "importance_score",
        "user_name",
        "status",
    }

    for field, value in changes.items():
        if field in non_nullable and value is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null",
            )
        if field == "status" and isinstance(value, str) and not value.strip():
            raise HTTPException(status_code=422, detail="Status cannot be empty")
        setattr(complaint, field, value)

    db.commit()
    db.refresh(complaint)

    return complaint_to_dict(complaint, db)


@router.post("/complaints/{complaint_id}/remarks")
def add_remark(
    complaint_id: int,
    body: RemarkCreate,
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    remark_text = body.remark.strip()
    if not remark_text:
        raise HTTPException(status_code=422, detail="Remark cannot be empty")

    remark = AdminRemark(
        complaint_id=complaint_id,
        remark=remark_text,
    )

    db.add(remark)
    db.commit()
    db.refresh(remark)

    return {
        "id": remark.id,
        "complaint_id": remark.complaint_id,
        "remark": remark.remark,
        "created_at": remark.created_at.isoformat() if remark.created_at else None,
    }
