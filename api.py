from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from main import process_complaint
from schema import Schema, UserInfo
from fastapi import FastAPI, Form, File, UploadFile
from pydantic import BaseModel, Field
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/css", StaticFiles(directory="resources/css"), name="css")
app.mount("/script", StaticFiles(directory="resources/script"), name="script")

templates = Jinja2Templates(directory="resources/templates")


@app.post("/complaints")
def create_complaint(
    user_info: str = Form(...),
    complaint_text: str = Form(""),
    files: list[UploadFile] | None = File(default=None)
):

    user = UserInfo(**json.loads(user_info))

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


@app.get("/complaints")
def test_request_get(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="complaint_form.html",
        context={}
    )