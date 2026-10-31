
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from graph import structured_llm
from langchain_core.messages import SystemMessage, HumanMessage
from prompts import SYSTEM_INSTRUCTION

response = structured_llm.invoke([
    SystemMessage(content=SYSTEM_INSTRUCTION),
    HumanMessage(
        content="There are large potholes on the main road, making it dangerous for vehicles."
    )
])

print(response)
print(type(response))
print(response.model_dump())
