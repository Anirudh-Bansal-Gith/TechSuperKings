
import os
import base64
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from schema import Schema
from prompts import SYSTEM_INSTRUCTION

load_dotenv()

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_KEY"),
    model="openrouter/free"
)

structured_llm = llm.with_structured_output(
    Schema,
    method="json_schema",
    strict=True
)


class ComplaintState(TypedDict, total=False):
    complaint_text: str
    attachments: list
    structured_output: Schema


def classify_complaint(state: ComplaintState):

    content = [
        {
            "type": "text",
            "text": state.get("complaint_text") or ""
        }
    ]

    attachments = state.get("attachments") or []

    for attachment in attachments:

        # Ignore null attachment entries
        if attachment is None:
            continue

        mime_type = attachment.get("mime_type")
        file_data = attachment.get("data")

        if not mime_type:
            raise ValueError("Attachment MIME type is missing")

        if not file_data:
            raise ValueError("Attachment data is empty or missing")

        mime_type = mime_type.lower().split(";")[0].strip()

        encoded_data = base64.b64encode(
            file_data
        ).decode("utf-8")

        if mime_type.startswith("image/"):

            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{encoded_data}"
                }
            })

        elif mime_type.startswith("audio/"):

            audio_format = mime_type.split("/")[-1]

            format_mapping = {
                "mpeg": "mp3",
                "x-wav": "wav",
                "wave": "wav",
                "mp4": "m4a",
                "x-m4a": "m4a"
            }

            audio_format = format_mapping.get(
                audio_format,
                audio_format
            )

            content.append({
                "type": "input_audio",
                "input_audio": {
                    "data": encoded_data,
                    "format": audio_format
                }
            })

        elif mime_type.startswith("video/"):

            content.append({
                "type": "video_url",
                "video_url": {
                    "url": f"data:{mime_type};base64,{encoded_data}"
                }
            })

        else:
            raise ValueError(
                f"Unsupported attachment MIME type: {mime_type}"
            )

    messages = [
        SystemMessage(content=SYSTEM_INSTRUCTION),
        HumanMessage(content=content)
    ]

    response = structured_llm.invoke(messages)

    return {"structured_output": response}


builder = StateGraph(ComplaintState)

builder.add_node("classify_complaint", classify_complaint)

builder.add_edge(START, "classify_complaint")
builder.add_edge("classify_complaint", END)

graph = builder.compile()
