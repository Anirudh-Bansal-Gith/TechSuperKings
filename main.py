import os
import tempfile

from graph import graph
from database import SessionLocal
from persistence import save_complaint


def process_complaint(
    complaint_text,
    uploaded_files=None,
    user_details=None
):
    uploaded_files = uploaded_files or []
    user_details = user_details or {}

    attachments = []
    temp_paths = []

    try:
        for file in uploaded_files:
            if file is None:
                continue

            mime_type = file.content_type

        if file is None:
            continue

            file.file.seek(0)

            # Videos: store on disk instead of loading into RAM
            if mime_type.startswith("video/"):
                suffix = os.path.splitext(file.filename or "")[1]

        file.file.seek(0)
        file_data = file.file.read()
        file.file.seek(0)

                temp_paths.append(temp_path)

        attachments.append({
            "data": file_data,
            "mime_type": mime_type,
            "filename": file.filename,
        })

    # Run complaint processing and classification
    result = graph.invoke({
        "complaint_text": complaint_text or "",
        "attachments": attachments,
    })

                        temp_file.write(chunk)

    db = SessionLocal()

    try:
        if llm_output.importance_score > 0:
            return save_complaint(
                db,
                llm_output,
                [file for file in uploaded_files if file is not None],
                user_details
            )

        return {
            "message": "Your complaint appears to be invalid or irrelevant.",
            "saved": False
        }

    finally:
        # Delete temporary video files regardless of success or failure
        for path in temp_paths:
            try:
                os.remove(path)
            except OSError:
                pass