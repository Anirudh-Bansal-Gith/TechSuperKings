
from models import Complaint, ComplaintAttachment
from storage import upload_file, delete_file


def save_complaint(db, llm_output, uploaded_files):

    output = llm_output.model_dump(mode="json")

    uploaded_keys = []

    try:
        # Save complaint record first
        complaint = Complaint(**output)

        db.add(complaint)
        db.flush()

        # Upload every attachment
        attachment_results = []

        for file in uploaded_files:

            info = upload_file(file, complaint.id)

            uploaded_keys.append(info["storage_key"])

            attachment = ComplaintAttachment(
                complaint_id=complaint.id,
                storage_key=info["storage_key"],
                mime_type=info["mime_type"],
                file_size=info["file_size"]
            )

            db.add(attachment)
            attachment_results.append(info)

        # Commit database records
        db.commit()

        return {
            **output,
            "complaint_id": complaint.id,
            "attachments": attachment_results
        }

    except Exception:
        db.rollback()

        # Delete files if database persistence fails
        for key in uploaded_keys:
            try:
                delete_file(key)
            except Exception:
                pass

        raise
