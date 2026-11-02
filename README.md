# CivicDesk — AI-Powered Government Complaint Management System

**CivicDesk** is a full-stack, AI-powered government complaint management platform designed to simplify how citizens report public issues and how authorities manage, prioritize, and resolve them.

The platform accepts complaints in multiple formats, including text, images, audio, and video. Its AI processing pipeline analyzes submitted information, generates a concise complaint description, identifies the responsible government department, and assigns an importance score to help prioritize issues.

CivicDesk provides separate interfaces for citizens and administrators, with complaint tracking, administrative oversight, persistent storage, and multimedia processing.

---

## Live Applications

| Component | Description | Link |
|---|---|---|
| Citizen Portal | Submit complaints and access citizen-facing features | [Civic Pulse](https://civicpulseuser.streamlit.app/) |
| Admin Dashboard | View, search, manage, and update complaints | [CivicDesk Dashboard](https://civicdesk.streamlit.app/) |
| Backend API | FastAPI backend hosted on Render | [CivicDesk API](https://techsuperkings.onrender.com/) |
| API Documentation | Interactive API documentation | [Swagger UI](https://techsuperkings.onrender.com/docs) |

> **Note:** Application availability depends on the deployed services and their external dependencies.

---

## Key Features

### 1. Multimedia Complaint Submission
- Submit complaints using text descriptions.
- Upload supporting images and videos.
- Submit audio recordings.
- Process multiple attachments in a single complaint.
- Validate uploaded files based on supported formats and size restrictions.

### 2. AI-Powered Complaint Classification
The AI processing pipeline automatically extracts:

- **Complaint Description:** A concise summary of the reported issue.
- **Department:** The government department responsible for handling the complaint.
- **Importance Score:** A numerical score used to assess the significance and urgency of the complaint.

Structured LLM output ensures that classification results follow a predefined Pydantic schema.

### 3. Image Analysis
- Analyze uploaded images using a vision-capable Gemini model.
- Generate textual descriptions of visible issues.
- Use image descriptions as additional context during complaint classification.

### 4. Audio Processing
- Transcribe citizen-submitted audio using SarvamAI.
- Convert speech into text that can be used by the complaint-processing pipeline.

### 5. Video Analysis
- Process uploaded videos using FFmpeg.
- Extract and analyze video frames.
- Use visual descriptions as additional evidence for complaint classification.

### 6. Location Processing
- Accept location coordinates from the complaint submission.
- Perform reverse geocoding using Geopy and Nominatim.
- Associate a human-readable location with the complaint.

### 7. Complaint Tracking
- Allow citizens to track submitted complaints using their complaint ID and phone number.
- Retrieve complaint status and relevant tracking information.

### 8. Administrative Dashboard
Administrators can:
- View submitted complaints.
- Search and filter complaint records.
- Inspect complaint descriptions, departments, and importance scores.
- Update complaint status.
- Add administrative remarks.
- Review complaint information and associated attachments.

### 9. Persistent Storage
- Store complaint records in Turso, using SQLite through libSQL.
- Use SQLAlchemy for database operations and ORM-based data management.
- Store uploaded files in Backblaze B2.
- Maintain attachment metadata alongside complaint records.
- Handle cleanup when persistence operations fail.

---

## System Architecture

CivicDesk follows a modular architecture that separates the user interfaces, API layer, AI processing workflow, and persistence layer.

```text
                  CITIZENS
                     |
                     v
              Citizen Portal
                     |
                     v
                FastAPI
                 (api.py)
                     |
                     v
             Complaint Handler
                 (main.py)
                     |
                     v
              LangGraph Workflow
                 (graph.py)
                     |
          +----------+----------+
          |          |          |
          v          v          v
        Image      Audio       Video
      Processor  Processor   Processor
          |          |          |
          v          v          v
       Gemini    SarvamAI    FFmpeg +
       Vision       STT     Frame Analysis
          |          |          |
          +----------+----------+
                     |
                     v
           Complaint Classification
                     |
                     v
              Structured Output
                     |
                     v
              Persistence Layer
              (persistence.py)
                     |
              +------+------+
              |             |
              v             v
           Turso DB      Backblaze B2
              |
              v
        Admin Dashboard
```

### Architecture Components

| Layer | Technology | Responsibility |
|---|---|---|
| Citizen Interface | Streamlit | Citizen-facing complaint submission and tracking |
| Admin Interface | Streamlit | Administrative complaint management |
| API Layer | FastAPI | Handles incoming requests and backend operations |
| Workflow Orchestration | LangGraph | Coordinates attachment processing and classification |
| AI / LLM | Gemini | Complaint classification and visual analysis |
| Speech Recognition | SarvamAI | Audio transcription |
| Video Processing | FFmpeg | Video frame extraction and processing |
| Database | Turso | Persistent complaint storage |
| ORM | SQLAlchemy | Database models and operations |
| Object Storage | Backblaze B2 | Uploaded attachment storage |
| Geocoding | Geopy / Nominatim | Reverse geocoding of coordinates |

---

## Complaint Processing Workflow

A complaint passes through the following stages:

### Step 1 — Complaint Submission

A citizen submits a complaint through the citizen portal.

The submission can contain:
- Complaint title and description.
- Location information.
- Optional image attachments.
- Optional audio recordings.
- Optional video attachments.

### Step 2 — Backend Processing

The FastAPI endpoint receives the complaint and forwards the information to `process_complaint()` in `main.py`.

The backend:
- Extracts the submitted coordinates.
- Performs reverse geocoding.
- Prepares uploaded files for processing.
- Stores large video files temporarily on disk to avoid unnecessarily loading them entirely into memory.

### Step 3 — Attachment Processing

The complaint is passed to the LangGraph workflow.

The `process_attachments` node processes the available attachments:

- Images are analyzed using the vision model.
- Audio is transcribed using SarvamAI.
- Videos are processed to extract and analyze relevant frames.

The resulting descriptions and transcriptions provide additional context for classification.

### Step 4 — Complaint Classification

The `classify_complaint` node uses an LLM to analyze the complaint text and attachment-derived information.

The model returns structured output containing:

```python
{
    "query_description": "...",
    "department": "...",
    "importance_score": 0
}
```

The output is validated against the Pydantic schema defined in `schema.py`.

### Step 5 — Validation and Persistence

The backend evaluates the classification result.

Relevant complaints are persisted using the persistence layer.

The persistence process:
- Creates the complaint database record.
- Uploads attachments to Backblaze B2.
- Stores attachment metadata.
- Associates the uploaded files with the complaint.

If persistence fails, the storage layer includes cleanup handling to avoid leaving unnecessary uploaded files behind.

### Step 6 — Citizen Tracking and Administration

After successful submission:
- The citizen receives the complaint details and complaint ID.
- The complaint can be tracked through the citizen-facing interface.
- Administrators can inspect and manage the complaint through the admin dashboard.

---

## Project Structure

```text
FORGE26/
│
├── api.py                  # FastAPI application entry point
├── main.py                 # Main complaint processing logic
├── graph.py                # LangGraph workflow definition
│
├── schema.py               # Pydantic schemas and department enum
├── models.py               # SQLAlchemy database models
├── database.py             # Turso database configuration
├── persistence.py          # Complaint persistence and B2 integration
│
├── admin.py                 # Administrative API routes
├── tracking.py              # Citizen complaint tracking routes
│
├── storage.py               # Backblaze B2 storage utilities
├── llms.py                  # LLM initialization and configuration
├── prompts.py               # Classification prompts
│
├── image_processor.py       # Image analysis using vision LLM
├── audio_processor.py       # Audio transcription using SarvamAI
├── video_processor.py       # Video processing and frame analysis
│
├── streamlit_app.py         # Admin dashboard
├── user_tracking.py         # Citizen-facing application entry point
│
├── requirements.txt         # Python dependencies
│
└── resources/
    ├── css/
    ├── script/
    └── templates/
```

---

## Technology Stack

### Backend
- **Python** — Core application development.
- **FastAPI** — REST API development.
- **LangGraph** — Multi-step AI workflow orchestration.
- **Pydantic** — Data validation and structured LLM outputs.
- **SQLAlchemy** — Database ORM.

### Artificial Intelligence
- **Google Gemini** — Text classification and vision-based analysis.
- **SarvamAI** — Speech-to-text transcription.

### Multimedia Processing
- **FFmpeg** — Video frame extraction and processing.
- **Python file handling** — Uploaded file processing and temporary storage.

### Database and Storage
- **Turso** — Hosted SQLite database.
- **libSQL** — Database connectivity.
- **Backblaze B2** — Object storage for multimedia attachments.

### Frontend
- **Streamlit** — Citizen portal and administrative dashboard.

### Deployment
- **Streamlit Community Cloud** — Frontend deployment.
- **Render** — FastAPI backend hosting.

---

## Installation and Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Anirudh-Bansal-Gith/TechSuperKings.git
cd TechSuperKings
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

```env
# Gemini
GEMINI_API_KEY_869=your_gemini_api_key

# Turso Database
TURSO_DATABASE_URL=your_turso_database_url
TURSO_AUTH_TOKEN=your_turso_auth_token

# Backblaze B2
B2_BUCKET_NAME=your_bucket_name
B2_ENDPOINT=your_b2_endpoint
B2_KEY_ID=your_b2_key_id
B2_APPLICATION_KEY=your_b2_application_key

# SarvamAI
SARVAM_API_KEY=your_sarvam_api_key
```

Use the variable names expected by your application configuration. Never commit `.env` files or expose API keys in the repository.

### 5. Start the FastAPI backend

```bash
uvicorn api:app --reload
```

The backend will be available at:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### 6. Run the Admin Dashboard

In another terminal:

```bash
streamlit run streamlit_app.py
```

### 7. Run the Citizen Application

```bash
streamlit run user_tracking.py
```

The citizen application and admin dashboard can run independently while communicating with the configured backend API.

---

## API Endpoints

The backend exposes endpoints for complaint submission, tracking, and administrative management.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/complaints` | Submit a complaint with text and attachments |
| GET | `/complaints` | Complaint-related GET endpoint |
| GET | `/track/{id}` | Retrieve complaint tracking information |
| GET | `/admin/complaints` | Retrieve complaints for administrators |
| GET | `/admin/complaints/{id}` | Retrieve an individual complaint with its details |
| PATCH | `/admin/complaints/{id}` | Update complaint information or status |
| POST | `/admin/complaints/{id}/remarks` | Add an administrative remark |

For the exact request and response schemas, use the interactive Swagger documentation:

[https://techsuperkings.onrender.com/docs](https://techsuperkings.onrender.com/docs)

---

## Data and Validation

CivicDesk uses structured data models to maintain consistency across the application.

### Complaint Classification Schema

The classification schema contains:

| Field | Description |
|---|---|
| `query_description` | AI-generated complaint summary |
| `department` | Responsible government department |
| `importance_score` | Numerical importance score |

### Department Classification

The Pydantic department enum includes government service categories such as:

- Agriculture and Farmers Welfare
- Education
- Electricity and Power
- Health and Family Welfare
- Home Affairs and Police
- Housing and Urban Development
- Public Works Department
- Public Health Engineering
- Road Transport and Highways
- Water Resources and Irrigation
- Social Welfare
- Urban Local Bodies
- Other government services

The complete list is maintained in `schema.py`.

---

## Deployment

CivicDesk uses separate deployment services for its frontend applications and backend API.

| Service | Hosting Platform |
|---|---|
| Citizen Portal | Streamlit Community Cloud |
| Admin Dashboard | Streamlit Community Cloud |
| Backend API | Render |
| Database | Turso |
| File Storage | Backblaze B2 |

The frontend applications communicate with the deployed FastAPI backend. The backend handles AI processing, database operations, and file storage.

---

## Future Improvements

Potential areas for further development include:

- Automated complaint status notifications.
- More advanced complaint prioritization.
- Improved duplicate complaint detection.
- Geographic complaint visualization and hotspot analysis.
- Analytics for identifying recurring public infrastructure issues.
- Better monitoring and retry mechanisms for external AI services.
- More comprehensive complaint resolution workflows.

---

## Team

**Project:** CivicDesk — Government Complaint Management System  
**Team:** TechSuperKings  
**Event:** NxtWave Launchpad FORGE ’26 Gen AI Buildathon

---

## Links

- [Citizen Portal](https://civicpulseuser.streamlit.app/)
- [Admin Dashboard](https://civicdesk.streamlit.app/)
- [Backend API](https://techsuperkings.onrender.com/)
- [API Documentation](https://techsuperkings.onrender.com/docs)
- [GitHub Repository](https://github.com/Anirudh-Bansal-Gith/TechSuperKings)

---

**CivicDesk — Making public grievance reporting and management more accessible, structured, and intelligent.**
