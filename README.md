# FORGE26 - Government Complaint Classification System

A FastAPI-based backend system that processes and classifies public complaints with support for text, images, videos, and audio attachments. The system uses LangGraph for workflow orchestration, LangChain for LLM integration, and stores data in Turso DB with original attachments in Backblaze B2.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Design Principles](#design-principles)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multi-modal complaint submission**: Accept complaints as text with optional images, videos, and audio files
- **Intelligent classification**: Automatically categorizes complaints into government departments with importance scoring (-100 to 100)
- **Image analysis**: Extracts detailed, factual descriptions from complaint images
- **Video processing**: Scene detection, timestamped frame analysis, and audio transcription from videos
- **Audio transcription**: Multilingual audio transcription using Sarvam AI
- **Geolocation**: Reverse geocoding to convert coordinates to human-readable addresses
- **Evidence preservation**: Original attachments stored separately in object storage
- **Structured output**: Pydantic-validated classification results

## Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | [FastAPI](https://fastapi.dev/) |
| Workflow Orchestration | [LangGraph](https://www.langchain.com/langgraph) |
| LLM Integration | [LangChain](https://www.langchain.com/) |
| LLM Providers | [OpenRouter](https://www.openrouter.ai/), [Google Gemini](https://ai.google.dev/) |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) |
| Database | [SQLAlchemy](https://www.sqlalchemy.org/) + [Turso](https://turso.tech/) (libSQL) |
| Object Storage | [Backblaze B2](https://www.backblaze.com/cloud-storage) |
| Media Processing | [FFmpeg](https://ffmpeg.org/) |
| Audio Transcription | [Sarvam AI](https://www.sarvam.ai/) |
| Testing | [pytest](https://docs.pytest.org/) |

## Architecture

### Workflow

```text
User Submission (Text + Attachments + User Details)
                        ↓
                      main.py
                        ↓
                      graph.py (LangGraph)
                        ↓
                process_attachments()
                ├── Image → image_processor.py → Description
                ├── Audio → audio_processor.py → Transcript
                └── Video → video_processor.py → Transcript + Timestamped Visual Analysis
                        ↓
                    classify_complaint()
                        ↓
                    Structured Pydantic Output
                    (query_description, department, importance_score)
                        ↓
                      persistence.py
                ├── Turso DB (metadata/records)
                └── Backblaze B2 (original attachments)
```

**Key Principle**: Media processors convert attachments into textual representations for classification. Original attachments are always preserved in storage as evidence.

## Project Structure

```text
FORGE26/
├── main.py              # API entry point and complaint processing logic
├── graph.py             # LangGraph workflow orchestration
├── schema.py            # Pydantic schemas and department enum
├── prompts.py           # LLM system prompts
├── llms.py              # LLM configurations (vision, classification)
├── database.py          # Database setup and session management
├── models.py            # SQLAlchemy ORM models
├── persistence.py       # Data persistence logic
├── storage.py           # Backblaze B2 upload/download
├── tracking.py          # Request tracking
├── user_tracking.py     # User analytics
├── api.py               # Additional API routes
├── admin.py             # Admin functionality
├── streamlit_app.py     # Streamlit dashboard
├── make_table.py        # Database table creation utility
├── image_processor.py   # Image description extraction
├── video_processor.py   # Video scene detection and analysis
├── audio_processor.py   # Audio transcription via Sarvam AI
├── requirements.txt     # Python dependencies
└── test/                # Test suite
```

### Module Responsibilities

| Module | Description |
|---|---|
| `main.py` | Handles complaint submission, geolocation, attachment preparation, and coordination |
| `graph.py` | Defines LangGraph state machine for attachment processing and classification |
| `schema.py` | Defines `Schema` (query_description, department, importance_score) and valid departments |
| `image_processor.py` | Converts images to factual, detailed descriptions using vision LLM |
| `video_processor.py` | Extracts audio, detects scenes, analyzes frames with timestamps, combines results |
| `audio_processor.py` | Transcribes audio using Sarvam AI's `saaras:v4` model |
| `storage.py` | Manages uploads to Backblaze B2 S3-compatible storage |
| `persistence.py` | Saves complaint records and attachment metadata to database |
| `models.py` | Defines database schema (Complaint, Attachment models) |

## Setup

### Prerequisites

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installed and in PATH
- API keys for OpenRouter/Google Gemini, Sarvam AI, Turso DB, Backblaze B2

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd FORGE26
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables** (see [Environment Variables](#environment-variables))
```bash
cp .env.example .env  # If exists, or create .env manually
```

5. **Initialize database**
```bash
python make_table.py
```

6. **Run the API server**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# LLM Configuration
OPENROUTER_API_KEY=your_openrouter_key
GOOGLE_API_KEY=your_google_gemini_key

# Audio Transcription
SARVAM_API_KEY=your_sarvam_key

# Database (Turso)
TURSO_DATABASE_URL=libsql://your-db.turso.io
TURSO_AUTH_TOKEN=your_turso_token

# Object Storage (Backblaze B2)
B2_ENDPOINT_URL=https://s3.us-west-000.backblazeb2.com
B2_KEY_ID=your_b2_key_id
B2_APPLICATION_KEY=your_b2_app_key
B2_BUCKET_NAME=your_bucket_name
```

## Usage

### Running the API

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Using Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

## API Endpoints

Key endpoints (see `main.py` for full details):

- `POST /complaint` - Submit a complaint with text and attachments
- `GET /complaints` - Retrieve complaints
- Admin endpoints available via `admin.py`

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest -v

# Run specific test file
python -m pytest test/test.py -v -s

# Run with coverage
python -m pytest --cov=. -v
```

### Test Coverage

Existing tests cover:
- Text-only complaints
- Missing/empty attachment collections
- Null or empty attachment entries
- Missing MIME types
- Unsupported attachment types

**Note**: Tests should avoid live LLM calls. Mock LLM responses when testing processing logic.

## Design Principles

1. **Separation of concerns**: Media understanding is separate from complaint classification. Each processor has a single responsibility.
2. **Evidence preservation**: Original attachments are never replaced by extracted text/descriptions.
3. **Factual extraction**: Processors describe observations factually without assuming causes, identities, or intentions.
4. **Modularity**: Components are independent and easily testable.
5. **Robust error handling**: Processing failures are handled gracefully without breaking the workflow.
6. **Efficient processing**: Video processing uses scene detection and frame sampling to avoid processing every frame.

## Contributing

### Guidelines

- Keep processing logic separate from API and database logic
- Don't duplicate existing functionality
- Validate inputs and handle errors explicitly
- Add tests for new functionality
- Never commit API keys, credentials, or `.env` files
- Coordinate before modifying shared modules
- Follow existing code style and patterns

### Areas to Contribute

- **Media Processing**: Improve image/video/audio processors, add support for new formats
- **Backend/Integration**: Enhance LangGraph workflow, optimize file handling
- **Database/Persistence**: Improve schema, add queries, optimize storage
- **Testing**: Add more comprehensive test coverage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
