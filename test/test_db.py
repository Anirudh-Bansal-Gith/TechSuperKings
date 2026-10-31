from pathlib import Path
import sys

from fastapi import UploadFile
from starlette.datastructures import Headers

# Allow imports from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database import SessionLocal
from schema import Schema, Department
from persistence import save_complaint


IMAGE_PATH = PROJECT_ROOT / "road.jpeg"

db = SessionLocal()

try:
    with IMAGE_PATH.open("rb") as image_file:
        uploaded_file = UploadFile(
            file=image_file,
            filename=IMAGE_PATH.name,
            headers=Headers({"content-type": "image/jpeg"})
        )

        llm_output = Schema(
            query_description="A road is damaged and has potholes.",
            department=Department.PWD,
            importance_score=50
        )

        result = save_complaint(
            db=db,
            llm_output=llm_output,
            uploaded_files=[uploaded_file]
        )

        print("\nComplaint saved successfully!")
        print(result)

except Exception as e:
    print("\nFailed to save complaint:")
    print(type(e).__name__, e)
    raise

finally:
    db.close()