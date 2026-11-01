
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Complaint

router = APIRouter(prefix="/track", tags=["Complaint Tracking"])


@router.get("/{complaint_id}")
def track_complaint(
    complaint_id: int,
    phone_number: str,
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id,
        Complaint.phone_number == phone_number,
    ).first()

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found. Check your complaint ID and phone number.",
        )

    return {
        "complaint_id": complaint.id,
        "status": complaint.status,
        "department": complaint.department,
        "description": complaint.query_description,
        "location": complaint.location,
    }
