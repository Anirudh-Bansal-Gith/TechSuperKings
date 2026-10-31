
from graph import graph


def process_complaint(complaint_text, uploaded_files=None):

    uploaded_files = uploaded_files or []

    attachments = []

    for file in uploaded_files:

        if file is None:
            continue

        mime_type = file.content_type

        if not mime_type:
            raise ValueError(
                f"MIME type missing for file: {file.filename}"
            )

        # Read the uploaded file
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
            "filename": file.filename,
        })

    # Run complaint processing and classification
    result = graph.invoke({
        "complaint_text": complaint_text or "",
        "attachments": attachments,
    })

    llm_output = result["structured_output"]

    # Convert Pydantic output into a JSON-compatible dictionary
    return llm_output.model_dump(mode="json")
