# FORGE26 – Government Complaint Classification System

## 1. Project Overview

This project aims to build a backend system for processing and classifying public complaints.

Users can submit:
- Complaint text
- Images
- Videos
- Audio recordings (planned)

The system analyses the complaint and its attachments, then generates a structured classification containing:

- **Query description:** A description of the complaint.
- **Department:** The government department responsible for handling it.
- **Importance score:** A score ranging from -100 to 100.

The original complaint attachments are stored separately so they can be retained as supporting evidence.

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python |
| API | FastAPI |
| LLM integration | LangChain |
| LLM provider | OpenRouter |
| Workflow orchestration | LangGraph |
| Data validation | Pydantic |
| Database | SQLAlchemy + Turso |
| File storage | Backblaze B2 |
| Testing | pytest |

---

## 3. High-Level Architecture

The backend is divided into three main responsibilities:

1. Receiving and validating complaint submissions.
2. Processing complaint attachments and classifying complaints.
3. Persisting complaint data and original attachments.

### Complaint processing workflow

```text
                User Submission
                       |
                       v
                    main.py
                       |
                       v
                    graph.py
                       |
          +------------+------------+
          |            |            |
          v            v            v
    Image Processor  Video Processor  Audio Processor
          |            |            |
          v            v            v
    Image Description Video Description Transcript
          |            |            |
          +------------+------------+
                       |
                       v
              Combine Extracted Text
                       |
                       v
              Classification LLM
                       |
                       v
              Structured Pydantic Output
                       |
                       v
               Complaint Persistence
                       |
              +--------+--------+
              |                 |
              v                 v
          Turso DB          Backblaze B2
       Metadata/records    Original attachments
```

**Important:** The modality-specific processors convert attachments into textual representations. The classification LLM then works with the complaint text and extracted information.

The original attachments are not replaced by their descriptions or transcripts.

---

## 4. Project Structure

The following describes the current modules and the planned media-processing modules.

```text
project/
│
├── main.py
├── graph.py
├── schema.py
├── prompts.py
├── database.py
├── models.py
├── persistence.py
├── storage.py
│
├── image_processor.py       # Planned
├── video_processor.py       # Planned
├── audio_processor.py       # Planned
│
└── test/
    └── test.py
```

### Existing modules

| File | Responsibility |
|---|---|
| `main.py` | API entry point; receives complaint submissions and prepares inputs for processing. |
| `graph.py` | Orchestrates the complaint-processing and classification workflow using LangGraph. |
| `schema.py` | Defines the Pydantic schema and valid department values for classification output. |
| `prompts.py` | Contains instructions for the classification LLM. |
| `database.py` | Handles database configuration and connectivity. |
| `models.py` | Defines database models using SQLAlchemy. |
| `persistence.py` | Handles saving complaint records and related metadata. |
| `storage.py` | Handles uploading original attachments to Backblaze B2. |

### Planned processing modules

| File | Responsibility |
|---|---|
| `image_processor.py` | Converts images into detailed, factual visual descriptions. |
| `video_processor.py` | Analyses videos and produces chronological descriptions with timestamps. |
| `audio_processor.py` | Transcribes audio into text, with multilingual support. |

These processors should remain independent of the classification workflow. Their outputs should be textual representations that `graph.py` can combine.

---

## 5. Attachment Processing Design

### Image processing

**Input:** An image file.

**Output:** A detailed textual description of its visible contents.

The processor should:
- Describe relevant objects, structures and visible conditions.
- Preserve readable text, signs and numbers.
- Describe relevant spatial relationships.
- Avoid assuming causes, identities, intentions or responsibility.
- Clearly identify unclear or unobservable details.

### Video processing

**Input:** A video file.

**Output:** A chronological textual description of relevant events.

Proposed workflow:

1. Detect scene boundaries.
2. Select representative frames.
3. Analyse selected frames using a vision-capable LLM.
4. Combine observations into a coherent description.
5. Preserve timestamps for important events.

The implementation should avoid blindly processing every frame, particularly for large videos.

### Audio processing

**Input:** An audio file.

**Output:** A transcript of the spoken content.

This module will be developed separately and should support multiple languages.

---

## 6. Classification Output

The existing classification output is represented by a Pydantic schema.

Conceptually, it contains:

```python
class Schema(BaseModel):
    query_description: str
    department: Department
    importance_score: int
```

The importance score is constrained to the range `-100` to `100`.

The classification LLM should use:
- The original complaint text.
- Extracted image descriptions.
- Extracted video descriptions.
- Audio transcripts, once implemented.

It must not treat uncertain observations or assumptions as established facts.

---

## 7. File Storage and Persistence

There are two separate kinds of data:

### Database – Turso

Stores structured complaint information and related metadata.

### Object storage – Backblaze B2

Stores the original uploaded attachments.

**Do not replace original attachments with extracted text.** The extracted descriptions and transcripts are used for processing; the original files remain available as evidence.

Media processing and permanent attachment storage are separate responsibilities.

---

## 8. Testing

The project uses `pytest`.

Run tests from the project root:

```bash
python -m pytest test/test.py -v -s
```

Existing tests cover cases such as:
- Text-only complaints.
- Missing or empty attachment collections.
- Null or empty attachment entries.
- Missing MIME types.
- Unsupported attachment types.

New processors should have independent tests for their input validation, processing behaviour and output format.

Avoid making tests depend unnecessarily on live LLM calls. Where appropriate, mock the LLM response to test the surrounding processing logic.

---

## 9. Contribution Guidelines

The project is modular. Contributors should work within clearly separated responsibilities.

### Media processing contributor

Possible tasks:
- Implement `image_processor.py`.
- Implement `video_processor.py`.
- Design reliable prompts for factual extraction.
- Test processing on real-world complaint attachments.
- Evaluate whether important evidence is being missed.

### Backend / integration contributor

Possible tasks:
- Integrate processors into `graph.py`.
- Handle uploaded files efficiently in `main.py`.
- Ensure that multiple attachments are processed correctly.
- Handle processing failures without breaking unrelated parts of the workflow.

### Database / persistence contributor

Possible tasks:
- Work on complaint persistence.
- Maintain database relationships and attachment metadata.
- Ensure failed database operations do not leave inconsistent storage records.

Before modifying shared modules, coordinate with the person responsible for that module.

### General rules

1. Keep processing logic separate from API and database logic.
2. Do not duplicate existing functionality.
3. Keep function inputs and outputs clearly defined.
4. Validate inputs and handle errors explicitly.
5. Add tests for new functionality.
6. Do not commit API keys, credentials or `.env` files.
7. Avoid changing existing modules unless the change is required for your task.

---

## 10. Current Development Direction

The immediate focus is to build a reliable attachment-processing pipeline.

Planned order:

1. Implement and test image processing.
2. Implement video processing.
3. Integrate both into the existing LangGraph workflow.
4. Test complaints containing multiple attachments.
5. Develop multilingual audio transcription separately.
6. Evaluate the complete complaint-classification pipeline.

The existing classification and persistence systems should be preserved while these additions are developed.

---

## 11. Important Design Principle

**Separate media understanding from complaint classification.**

Each media processor is responsible for extracting useful information from its input. The classification system is responsible for interpreting the complaint and assigning the appropriate department and importance score.

This separation makes the system easier to test, maintain and extend to additional media types.
