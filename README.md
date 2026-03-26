# 🚀 Business Idea Validator - AI Agent

An intelligent AI-powered business idea validation platform built with **FastAPI**, **Google Gemini**, and **Redis**. This project validates startup ideas and provides comprehensive analysis including market viability, risk assessment, competitive landscape, and actionable next steps.

## 🎯 Features

### Core Functionality
- **Intelligent Scoring**: AI-powered viability scores (0-10) based on market demand and feasibility
- **Market Analysis**: Identifies target markets and emerging trends
- **Risk Assessment**: Highlights critical risks and challenges
- **Opportunity Identification**: Discovers growth potential and unique advantages
- **Competitive Analysis**: Evaluates competitive landscape and differentiation
- **Action Planning**: Provides concrete first steps to validate ideas
- **Conversation Memory**: Context-aware responses using Redis

### Technical Highlights
- **Modern UI**: Responsive, dark-themed chat interface
- **RESTful API**: 6 well-designed endpoints with auto-documentation
- **Error Handling**: Graceful degradation when Redis unavailable
- **Production-Ready**: Containerized for Cloud Run deployment
- **Scalable**: Designed for horizontal scaling

## 📋 Architecture

```
┌─────────────────────────────────────────┐
│    Browser (HTML/CSS/JavaScript)        │
│       Dark Theme Chat Interface         │
└────────────────┬────────────────────────┘
                 │ HTTP REST API
                 ↓
┌─────────────────────────────────────────┐
│  FastAPI Backend (Python)               │
│  • Health monitoring                    │
│  • Conversation management              │
│  • Message processing                   │
│  • History retrieval                    │
└──────────┬─────────────────────┬────────┘
           │                     │
           ↓                     ↓
    Google Gemini API       Redis Database
    (gemini-2.5-           (Conversation
     flash-lite)            Memory)
```

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.104.1 |
| **ASGI Server** | Uvicorn | 0.24.0 |
| **LLM Integration** | Google Gemini API | Latest |
| **Data Validation** | Pydantic | 2.5.0+ |
| **Session Memory** | Redis | 5.0.0+ |
| **Environment** | python-dotenv | 1.0.0 |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key (from https://makersuite.google.com)
- Redis (optional, for conversation memory)

### Installation

#### 1. Clone and Enter Directory
```bash
cd Local-Business-Idea-Validator
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS/Linux
python3 -m venv env
source env/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup Environment Variables
```bash
# Copy example and edit
cp .env.example .env

# Add your Gemini API key
# Edit .env and set: API_KEY=your_api_key_here
```

#### 5. Start Redis (Optional)
```bash
# Docker (Recommended)
docker run -d -p 6379:6379 redis:latest

# Or macOS (Homebrew)
brew install redis && redis-server

# Or Linux (APT)
sudo apt-get install redis-server && redis-server
```

#### 6. Verify Setup
```bash
python verify_setup.py
```

#### 7. Run the Application
```bash
python main.py
```

#### 8. Access the UI
Open your browser to: **http://127.0.0.1:8000**

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Endpoints

#### 1. Health Check
```bash
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "redis_status": "Connected"
}
```

#### 2. Start Conversation
```bash
POST /conversation/start
```
**Response:**
```json
{
  "Conversation_Id": "uuid-string",
  "Status": "Started"
}
```

#### 3. Send Message (with Context)
```bash
POST /chat/message
Content-Type: application/json

{
  "idea": "Description of your business idea",
  "conversation_id": "uuid-from-start"
}
```

**Response:**
```json
{
  "score": 7.5,
  "verdict": "Promising",
  "market": "Target market analysis...",
  "risk": "Key risks...",
  "opportunities": "Growth potential...",
  "competition": "Competitive landscape...",
  "first_step": "Actionable next step...",
  "summary": "Overall assessment..."
}
```

#### 4. Get Conversation History
```bash
GET /chat/history/{conversation_id}
```

#### 5. Single Validation (No Memory)
```bash
POST /validate
Content-Type: application/json

{
  "idea": "Your business idea"
}
```

#### 6. Root Endpoint
```bash
GET /
```
Serves the frontend UI.

## 💡 Usage Examples

### Using the Web Interface
1. Open http://127.0.0.1:8000
2. Click "New Chat"
3. Describe your business idea (10-500 characters)
4. Press Ctrl+Enter or click "Send"
5. Review the comprehensive analysis

### Using cURL
```bash
# Start conversation
CONV_ID=$(curl -s -X POST http://localhost:8000/conversation/start | jq -r '.Conversation_Id')

# Send message
curl -X POST http://localhost:8000/chat/message \
  -H "Content-Type: application/json" \
  -d "{
    \"idea\": \"AI-powered inventory management for small retail stores\",
    \"conversation_id\": \"$CONV_ID\"
  }"
```

### Using Python
```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Start conversation
response = requests.post(f"{BASE_URL}/conversation/start")
conv_id = response.json()['Conversation_Id']

# Send message
payload = {
    "idea": "An AI chatbot for customer service",
    "conversation_id": conv_id
}

response = requests.post(f"{BASE_URL}/chat/message", json=payload)
result = response.json()

print(f"Score: {result['score']}/{10}")
print(f"Verdict: {result['verdict']}")
print(f"Summary: {result['summary']}")
```

## 📁 Project Structure

```
Local-Business-Idea-Validator/
├── main.py                    # FastAPI application entry point
├── agent.py                   # Gemini AI agent implementation
├── models.py                  # Pydantic request/response schemas
├── redis_client.py            # Redis conversation manager
├── verify_setup.py            # System verification script
├── requirements.txt           # Python dependencies
├── .env                       # API key configuration (create this)
├── .env.example              # Example environment file
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── SETUP_AND_RUN.md          # Detailed setup guide
├── PROJECT_STATUS.md         # Project status and checklist
└── UI_Pages/
    ├── index.html            # Frontend structure
    ├── index.css             # Styling and animations
    └── index.js              # Client-side logic

```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
API_KEY=AIza_your_gemini_api_key_here

# Optional
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
```

### Redis Configuration
Edit `redis_client.py` if Redis is on different host/port:
```python
redis_url = "redis://your-host:6379/0"
```

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t business-validator:latest .
```

### Run Locally
```bash
docker run -p 8000:8000 \
  -e API_KEY=your_key_here \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  business-validator:latest
```

### Deploy to Cloud Run
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/your-project/business-validator

# Deploy to Cloud Run
gcloud run deploy business-validator \
  --image gcr.io/your-project/business-validator \
  --platform managed \
  --set-env-vars API_KEY=your_key_here
```

## 🧪 Testing

### Run Verification Script
```bash
python verify_setup.py
```

### Test Endpoints with Swagger UI
1. Navigate to http://127.0.0.1:8000/docs
2. Try out each endpoint interactively
3. View request/response formats

### Load Testing
```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:8000/health
```

## 🐛 Troubleshooting

### "API_KEY not found" Error
**Solution:** Ensure `.env` file exists in project root with valid API key

### Redis Connection Error
**Solution:** App works without Redis. To enable:
1. Install Redis
2. Start Redis server
3. Restart the app

### Port 8000 Already in Use
**Solution:** Modify `main.py`:
```python
uvicorn.run(app, host="127.0.0.1", port=8001)
```

### CORS Issues
The app has CORS enabled for all origins. If issues persist:
- Check browser console for error details
- Ensure frontend is accessing correct backend URL
- Verify API_KEY is set correctly

## 📊 Performance

- **Response Time**: 2-5 seconds (Gemini API latency)
- **Concurrent Users**: 100+ (with Redis)
- **Message Storage**: Unlimited (with 24-hour TTL)
- **API Rate Limits**: Based on Google Gemini plan

## 🔒 Security

- API keys stored in `.env` (never committed)
- CORS enabled but can be restricted
- Input validation with Pydantic
- SQL injection not applicable (no DB)
- XSS protection via template escaping

## 📈 Scaling

### Horizontal Scaling
1. Use load balancer (e.g., Cloud Load Balancer)
2. Deploy multiple app instances
3. Share Redis across instances
4. Use managed Redis (e.g., Cloud Memorystore)

### Optimization Tips
- Enable response caching
- Implement request batching
- Use Redis clustering
- monitor API quota usage

## 📝 License

This project is part of the Google GenAI Academy Track 1 submission.

## 🤝 Contributing

For bugs or feature requests, please raise an issue or submit a pull request.

## 📧 Support

For issues or questions:
1. Check the [SETUP_AND_RUN.md](SETUP_AND_RUN.md) guide
2. Review [PROJECT_STATUS.md](PROJECT_STATUS.md) for known issues
3. Run `verify_setup.py` to diagnose problems
4. Check application logs for error messages

## 🎓 Learning Resources

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Google Gemini API Docs](https://makersuite.google.com)
- [Redis Documentation](https://redis.io/docs/)
- [Cloud Run Deployment](https://cloud.google.com/run/docs)

---

**Status**: ✅ Production Ready  
**Last Updated**: 2024  
**Maintained By**: GenAI Academy Team

## 🎯 Next Steps

1. ✅ Run `python verify_setup.py`
2. ✅ Start Redis: `redis-server`
3. ✅ Run app: `python main.py`
4. ✅ Test at: http://127.0.0.1:8000
5. ⏳ Deploy to Cloud Run
6. ⏳ Generate PowerPoint slides
7. ⏳ Submit to GenAI Academy

#URL
https://business-idea-validator-du6h2ejera-el.a.run.app

**output**
	
Response body
Download
{
  "score": 7,
  "market": "Small and mid-sized businesses in tier 2 cities seeking professional product design services to enhance their market competitiveness and brand appeal.",
  "risk": "Building trust and demonstrating tangible ROI for smaller businesses with limited marketing budgets, potentially requiring a strong portfolio and clear value proposition.",
  "competition": "Competition will likely come from local freelance designers, smaller generalist agencies, and potentially in-house design capabilities of larger businesses, but a specialized focus on product design in these specific markets might offer differentiation.",
  "first_step": "Identify 3-5 tier 2 cities and begin researching existing businesses within those areas that could benefit from product design services, noting their current product offerings and branding.",
  "summary": "This idea addresses a clear need for professional product design in underserved tier 2 markets. Success hinges on effectively communicating value and building credibility with smaller businesses.  There's significant potential for growth if executed strategically."
}