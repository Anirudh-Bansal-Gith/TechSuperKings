
from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from main import process_complaint

app = FastAPI()


@app.post("/complaints")
def create_complaint(
    complaint_text: str = Form(""),
    files: list[UploadFile] | None = File(default=None)
):

    try:
        result = process_complaint(
            complaint_text,
            files
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
