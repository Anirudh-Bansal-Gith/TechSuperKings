
from models import Complaint, ComplaintAttachment
from storage import upload_file, delete_file


def save_complaint(db, llm_output, uploaded_files, user_details=None):
    """
    Save the structured complaint, user details and attachment metadata.

    Original files are uploaded to B2. Their storage keys and metadata
    are saved in Turso. If a later step fails, the DB transaction is
    rolled back and files uploaded during this call are deleted.
    """

    output = llm_output.model_dump(mode="json")
    uploaded_files = uploaded_files or []
    user_details = user_details or {}
    uploaded_keys = []

    # Convert UserInfo field names to Complaint model field names.
    mapped_user_details = {
        db_field: user_details[schema_field]
        for schema_field, db_field in USER_FIELD_MAPPING.items()
        if schema_field in user_details
    }

    try:
        complaint = Complaint(
            **output,
            **user_details
        )

        db.add(complaint)

        # Obtain the generated complaint ID before constructing B2 keys.
        db.flush()

        attachment_results = []

        for file in uploaded_files:
            info = upload_file(file, complaint.id)
            uploaded_keys.append(info["storage_key"])

            attachment = ComplaintAttachment(
                complaint_id=complaint.id,
                storage_key=info["storage_key"],
                mime_type=info["mime_type"],
                file_size=info["file_size"],
            )

            db.add(attachment)
            attachment_results.append(info)

        db.commit()

        return {
            **output,
            **user_details,
            "complaint_id": complaint.id,
            "attachments": attachment_results,
        }

    except Exception:
        db.rollback()

        # Best-effort cleanup of uploaded B2 objects.
        for key in uploaded_keys:
            try:
                delete_file(key)
            except Exception:
                pass

        raise
