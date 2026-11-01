
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from llms import classification_llm
from schema import Schema
from prompts import SYSTEM_INSTRUCTION
from image_processor import process_image
from audio_processor import process_audio


class ComplaintState(TypedDict, total=False):
    complaint_text: str
    attachments: list[dict]
    processed_text: str
    structured_output: Schema


structured_llm = classification_llm.with_structured_output(
    Schema,
    method="function_calling"
)

def process_attachments(state: ComplaintState):

    complaint_text = state.get("complaint_text", "")
    attachments = state.get("attachments", [])

    processed_text = f"Complaint:\n{complaint_text}"

    for attachment in attachments:

        mime_type = attachment["mime_type"]
        data = attachment["data"]

        if mime_type.startswith("image/"):

            description = process_image(
                image_bytes=data,
                mime_type=mime_type,
            )

            processed_text += (
                "\n\nImage description:\n" + description
            )

        elif mime_type.startswith("audio/"):

            transcript = process_audio(
                audio_bytes=data,
                filename=attachment["filename"],
            )

            processed_text += (
                "\n\nAudio transcript:\n" + transcript
            )

        else:
            raise ValueError(
                f"Unsupported attachment type: {mime_type}"
            )

    return {"processed_text": processed_text}


def classify_complaint(state: ComplaintState):

    response = structured_llm.invoke([
        SystemMessage(content=SYSTEM_INSTRUCTION),
        HumanMessage(content=state["processed_text"]),
    ])

    return {"structured_output": response}


builder = StateGraph(ComplaintState)

builder.add_node("process_attachments", process_attachments)
builder.add_node("classify_complaint", classify_complaint)

builder.add_edge(START, "process_attachments")
builder.add_edge("process_attachments", "classify_complaint")
builder.add_edge("classify_complaint", END)

graph = builder.compile()
