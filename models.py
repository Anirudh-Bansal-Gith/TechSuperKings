from sqlalchemy import (
    Column, ForeignKey, Integer, String, Float,
    DateTime, Text, func
)

from database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query_description = Column(String, nullable=False)
    department = Column(String, nullable=False)
    importance_score = Column(Integer, nullable=False)
    user_name = Column(String, nullable=False)
    email_id = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location = Column(String, nullable=True)

    status = Column(String, nullable=False, default="Pending")


class ComplaintAttachment(Base):
    __tablename__ = "complaint_attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=False,
        index=True,
    )
    storage_key = Column(String, nullable=False, unique=True)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)


class AdminRemark(Base):
    __tablename__ = "admin_remarks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id"),
        nullable=False,
        index=True,
    )
    remark = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )