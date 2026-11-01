# CivicDesk — Government Complaint Management System

**CivicDesk** is a full-stack application for managing public government complaints, from submission through tracking and admin oversight.

---

## Architecture

The system follows a pipeline:

1. **Frontend** — Streamlit UI for citizens to submit complaints and for admins to manage them
2. **API Layer** — FastAPI backend (`api.py`) handling complaint creation, status updates, and admin operations
3. **Processing Engine** — LangGraph-based workflow (`graph.py`) that:
   - Processes attachments (images, audio, video)
   - Classifies complaints using structured LLM output
   - Extracts department, query description, and importance score
4. **Persistence** — Turso (SQLite + libsql) database via SQLAlchemy; files stored on Backblaze B2

---

## Project Structure

```
FORGE26/
├── api.py                # FastAPI entry point
├── main.py               # Core complaint processing logic
├── graph.py              # LangGraph workflow
├── schema.py             # Pydantic models (Department enum, Schema, UserInfo)
├── models.py             # SQLAlchemy database models
├── database.py           # DB connection (Turso)
├── persistence.py        # Save complaint to DB + B2 upload
├── admin.py              # Admin API routes
├── tracking.py           # Complaint tracking API
├── storage.py            # B2 file upload utilities
├── llms.py               # LLM configuration (OpenRouter)
├── prompts.py            # System prompts for LLM classification
├── image_processor.py    # Vision LLM for image descriptions
├── audio_processor.py    # SarvamAI STT for audio transcription
├── video_processor.py    # FFmpeg-based video analysis
├── streamlit_app.py      # Admin dashboard UI
├── requirements.txt      # Python dependencies
└── resources/            # Static assets (CSS, JS, templates)
```

---

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment variables** — create a `.env` file with:
   ```
   OPEN_ROUTER_KEY=<your_openrouter_key>
   TURSO_DATABASE_URL=<your_turso_db_url>
   TURSO_AUTH_TOKEN=<your_turso_auth_token>
   B2_BUCKET_NAME=<your_b2_bucket>
   B2_ENDPOINT=<your_b2_endpoint>
   B2_KEY_ID=<your_b2_key_id>
   B2_APPLICATION_KEY=<your_b2_application_key>
   SARVAM_API_KEY=<your_saravam_api_key>
   ```

3. **Initialize the database:**
   ```bash
   uvicorn api:app --reload
   ```
   Visit `http://localhost:8000/docs` for auto-generated API docs.

4. **Run the admin dashboard:**
   ```bash
   streamlit run streamlit_app.py
   ```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST /complaints` | Submit a new complaint (text + attachments) |
| `GET /complaints` | List all complaints (admin) |
| `GET /complaints/{id}` | Get a single complaint |
| `PATCH /complaints/{id}` | Update complaint fields |
| `POST /complaints/{id}/remarks` | Add admin remark |
| `GET /track/{id}` | Track complaint status (citizen view) |
| `GET /admin/complaints` | List all complaints (admin) |
| `GET /admin/complaints/{id}` | Get full complaint with remarks |

---

## Workflow

1. Citizen submits a complaint via Streamlit with optional images/audio/video
2. `process_complaint()` in `main.py` handles:
   - Coordinate extraction from address
   - File processing (videos stored on disk, images/audio in memory)
   - LangGraph pipeline: `process_attachments` → `classify_complaint`
3. LLM extracts: `query_description`, `department`, `importance_score`
4. Complaint saved to Turso DB; files uploaded to B2
5. Admin can view, search, and update complaint status via Streamlit dashboard

---

## Dependencies

Key packages (see `requirements.txt`):

- `langchain-openai` / `langgraph` — LLM workflow orchestration
- `pydantic` / `sqlalchemy` — Data modeling and persistence
- `boto3` — Backblaze B2 storage
- `sarvamai` — Speech-to-text transcription
- `geopy` — Geocoding addresses
- `streamlit` — Admin UI

---

## Features

- ✅ Complaint submission with multimedia attachments
- ✅ Automated classification (department, importance score, description)
- ✅ Image analysis (via vision LLM)
- ✅ Audio/video transcription and analysis
- ✅ Geocoding of user-provided addresses
- ✅ Admin dashboard with search, filtering, and status updates
- ✅ Complaint tracking for citizens (by ID + phone)
- ✅ File storage on Backblaze B2 with DB metadata
- ✅ Rollback on save failure (files cleaned up)

---

## Notes

- The system uses **OpenRouter** for LLM access (models: `openrouter/free`, `nvidia/nemotron-3.5-super-vl:free`)
- Audio transcription via **SarvamAI**
- Database on **Turso** (libsql driver)
- File uploads validated (max 50MB, supported types only)