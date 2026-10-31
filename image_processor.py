import base64

from langchain_core.messages import SystemMessage, HumanMessage

from llms import vision_llm
from prompts import IMAGE_DESCRIPTION_PROMPT


def process_image(image_bytes: bytes, mime_type: str) -> str:

    if not image_bytes:
        raise ValueError("Empty image received")

    if not mime_type.startswith("image/"):
        raise ValueError("Unsupported image MIME type")

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    image_url = f"data:{mime_type};base64,{encoded_image}"

    response = vision_llm.invoke([
        SystemMessage(content=IMAGE_DESCRIPTION_PROMPT),
        HumanMessage(content=[
            {
                "type": "text",
                "text": "Analyze this image."
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url
                }
            }
        ])
    ])

    print("STOP REASON:", response.response_metadata)
    print("RAW CONTENT:", response.content)

    return response.content.strip()

