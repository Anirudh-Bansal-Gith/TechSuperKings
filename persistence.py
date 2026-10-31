from models import Complaint, ComplaintAttachment
from storage import upload_file, delete_file


def save_complaint(db, llm_output, uploaded_files):
    """
    Save the structured complaint and its attachment metadata.

    Original files are uploaded to B2. Their storage keys and metadata
    are saved in Turso. If a later step fails, the DB transaction is
    rolled back and files uploaded during this call are deleted.
    """
    output = llm_output.model_dump(mode="json")
    uploaded_files = uploaded_files or []
    uploaded_keys = []

    try:
        complaint = Complaint(**output)
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
            "complaint_id": complaint.id,
            "attachments": attachment_results,
        }

    except Exception:
        db.rollback()

        # Best-effort cleanup. Do not hide the original exception if
        # deleting an uploaded object also fails.
        for key in uploaded_keys:
            try:
                delete_file(key)
            except Exception:
                pass

        raise
