
from graph import graph
from database import SessionLocal, engine, Base
from models import Complaint, ComplaintAttachment
from persistence import save_complaint

Base.metadata.create_all(bind=engine)


def process_complaint(complaint_text, uploaded_files=None):

    uploaded_files = uploaded_files or []

    attachments = []

    for file in uploaded_files:

        # Ignore null entries
        if file is None:
            continue

        mime_type = file.content_type

        if not mime_type:
            raise ValueError(
                f"MIME type missing for file: {file.filename}"
            )

        # Read the file without consuming its stream permanently
        file.file.seek(0)
        file_data = file.file.read()
        file.file.seek(0)

        if not file_data:
            raise ValueError(
                f"Empty file uploaded: {file.filename}"
            )

        attachments.append({
            "data": file_data,
            "mime_type": mime_type,
            "filename": file.filename
        })

    # Send all attachments to the graph
    result = graph.invoke({
        "complaint_text": complaint_text or "",
        "attachments": attachments
    })

    llm_output = result["structured_output"]

    # Save complaint and original files
    db = SessionLocal()

    try:
        final_output = save_complaint(
            db,
            llm_output,
            [f for f in uploaded_files if f is not None]
        )

        return final_output

    finally:
        db.close()
