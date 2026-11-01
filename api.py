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


app.include_router(admin_router)
app.include_router(tracking_router)

@app.post("/complaints")
def create_complaint(
    user_info: str = Form(...),
    complaint_text: str = Form(""),
    files: list[UploadFile] | None = File(default=None),
):

    user = UserInfo(**json.loads(user_info))

    try:
        user_data = json.loads(user_details)

        if not isinstance(user_data, dict):
            raise ValueError("User details must be a JSON object.")

        user = UserInfo(**user_data)

        result = process_complaint(
            complaint_text,
            files,
            user.model_dump(exclude_none=True),
        )

        return result

    except (ValueError, TypeError) as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@app.get("/complaints")
def test_request_get(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="complaint_form.html",
        context={}
    )