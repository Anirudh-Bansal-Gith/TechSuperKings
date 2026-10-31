import os
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPEN_ROUTER_KEY")

# Existing classification model
classification_llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    model="openrouter/free",
)

# Dedicated vision model
vision_llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
    model="nvidia/nemotron-3.5-super-vl:free",
    temperature=0,
    max_tokens=2000,
)