
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from graph import graph
from schema import Schema, Department


def run_graph(complaint_text="", attachments=None):
    return graph.invoke({
        "complaint_text": complaint_text,
        "attachments": attachments
    })


def test_text_only_complaint():

    complaint = (
        "Water supply in Sector 44, Chandigarh is very poor. "
        "Residents are facing difficulties due to irregular water supply."
    )

    result = run_graph(complaint)

    output = result["structured_output"]

    assert isinstance(output, Schema)
    assert isinstance(output.department, Department)
    assert -100 <= output.importance_score <= 100

    print("\nText-only result:")
    print(output.model_dump_json(indent=2))

    # Ensure the model actually analysed the supplied complaint
    assert "water" in output.query_description.lower()


def test_no_attachments():

    result = run_graph(
        "Street lights have not been working for a week."
    )

    assert isinstance(result["structured_output"], Schema)


def test_null_attachments():

    result = run_graph(
        "Garbage has not been collected.",
        attachments=None
    )

    assert isinstance(result["structured_output"], Schema)


def test_empty_attachments():

    result = run_graph(
        "There is a pothole on the main road.",
        attachments=[]
    )

    assert isinstance(result["structured_output"], Schema)


def test_null_attachment_entry():

    with pytest.raises(ValueError):
        run_graph(
            "There is a pothole.",
            attachments=[None]
        )


def test_empty_attachment_data():

    with pytest.raises(ValueError):
        run_graph(
            "There is a pothole.",
            attachments=[{
                "data": b"",
                "mime_type": "image/jpeg"
            }]
        )


def test_missing_mime_type():

    with pytest.raises(ValueError):
        run_graph(
            "There is a pothole.",
            attachments=[{
                "data": b"some data"
            }]
        )


def test_unsupported_attachment():

    with pytest.raises(ValueError):
        run_graph(
            "There is a complaint.",
            attachments=[{
                "data": b"some data",
                "mime_type": "application/pdf"
            }]
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
