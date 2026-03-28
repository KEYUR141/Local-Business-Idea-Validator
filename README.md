# Business Idea Validator — AI Agent

An AI-powered startup validation platform built with Google ADK and Gemini, deployed on GCP Cloud Run. Analyzes business ideas across market potential, risk, competition, financial viability, and geographical fit for the Indian market — returning structured reports through a conversational chat interface.

**Live Demo:** `https://business-idea-validator-du6h2ejera-el.a.run.app`

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google%20ADK-4285F4?style=flat&logo=google&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini%202.5%20Flash-8E75B2?style=flat&logo=google&logoColor=white)
![Cloud Run](https://img.shields.io/badge/Cloud%20Run-4285F4?style=flat&logo=googlecloud&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)

| Component | Technology |
|---|---|
| Agent Framework | Google ADK |
| LLM | Gemini 2.5 Flash |
| Backend | FastAPI + Uvicorn |
| Memory | In-Memory Session Manager |
| Deployment | GCP Cloud Run |
| Containerization | Docker |
| Data Validation | Pydantic v2 |

---

## Architecture

```
Browser (Chat UI)
        |
        | HTTP REST
        v
FastAPI Backend (Cloud Run)
        |
        +---> Google ADK Agent
        |           |
        |           v
        |     Gemini 2.5 Flash
        |
        +---> In-Memory Session Manager
                    |
                    v
              Conversation History
              (TTL per session)
```

The agent operates in two modes determined by session state:

- **Analysis Mode** — triggered on first message, returns a full structured JSON validation report
- **Follow-up Mode** — triggered on subsequent messages, returns a conversational consultant response grounded in the original analysis

---

## Features

**Core Agent Capabilities**

- Viability scoring (0–10 float) with honest, calibrated reasoning
- Market analysis across Indian Tier 1, Tier 2, and Tier 3 cities
- Risk, opportunity, and competitive landscape assessment
- Financial viability and scalability evaluation
- Actionable first step recommendations
- Geographical context: UPI ecosystem, Jio penetration, MSME schemes, Startup India

**Technical Highlights**

- Dual-mode prompt architecture — structured JSON analysis and natural conversation from a single agent
- Session state flag (`has_analysis`) for reliable mode switching without extra API calls
- Auto-labeled conversation history in the sidebar
- Graceful ADK fallback to direct Gemini if ADK initialization fails
- 6 REST endpoints with Swagger auto-documentation at `/docs`

---

## Project Structure

```
Local-Business-Idea-Validator/
├── main.py              # FastAPI app, endpoints, middleware
├── agent.py             # VentureCheck ADK agent, prompt engineering, dual-mode logic
├── adk_agent.py         # Standalone ADK agent definition and demo
├── memory.py            # In-memory conversation manager with session state
├── models.py            # Pydantic request/response schemas
├── redis_client.py      # Redis conversation manager (optional)
├── Dockerfile           # Container configuration
├── requirements.txt     # Dependencies
├── .env.example         # Environment variable template
└── UI_Pages/
    ├── index.html       # Chat interface structure
    ├── index.css        # Styling
    └── index.js         # Client logic, auto-conversation creation, sidebar
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service and memory status |
| POST | `/conversation/start` | Create a new conversation session |
| POST | `/chat/message` | Send message, get validation or follow-up |
| GET | `/chat/history/{id}` | Retrieve full conversation history |
| DELETE | `/conversation/{id}` | Delete a conversation |
| POST | `/validate` | Single validation without session memory |
| GET | `/docs` | Swagger interactive API documentation |


## URL of the Project Deployed on the cloud run
- Note Same features are going to be implemnt in the project in few times
- Url:- https://business-idea-validator-626133859913.asia-south1.run.app


**Sample Request**

```bash
curl -X POST https://business-idea-validator-du6h2ejera-el.a.run.app/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A hyperlocal organic vegetable delivery app for Tier 2 cities",
    "conversation_id": "your-conversation-id",
    "input_type": "new_idea"
  }'
```

**Sample Response**

```json
{
  "title": "Hyperlocal Organic Veg Delivery — Tier 2",
  "score": 7.2,
  "verdict": "Promising",
  "market": "Health-conscious urban households in Tier 2 cities...",
  "risk": "Cold chain logistics and consistent supply from local farmers...",
  "opportunities": "Growing health awareness post-COVID and rising disposable income...",
  "competition": "BigBasket and Blinkit dominate Tier 1 but have limited Tier 2 presence...",
  "first_step": "Partner with 2-3 local organic farms this week and run a WhatsApp pilot...",
  "summary": "This idea has real traction potential in underserved Tier 2 markets..."
}
```

---

## Screenshots


---

## Local Setup

**Prerequisites:** Python 3.11+, Google Gemini API key

```bash
# Clone and enter directory
cd Local-Business-Idea-Validator

# Create virtual environment
python -m venv env
env\Scripts\activate        # Windows
source env/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add: API_KEY=your_gemini_api_key_here

# Run
python main.py
```

Open `http://127.0.0.1:8000` in your browser.

---

## Cloud Run Deployment

```bash
gcloud run deploy business-idea-validator --source . --platform managed --region asia-south1 --allow-unauthenticated --set-env-vars API_KEY=your_key_here --port 8000
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_KEY` | Yes | Google Gemini API key from AI Studio |
| `REDIS_URL` | No | Redis connection URL for persistent memory |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

---


