import os 
import logging 
import uuid
import json
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from models import ValidationResponse, BusinessIdeaInput
from fastapi.middleware.cors import CORSMiddleware
from agent import BusinessIdeaValidatorAgent
# from redis_client import RedisConversationManager
from memory import InMemoryConversationManager as ConversationManager
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title = "Business Idea Validator",
    description = "AI-powered validation of business ideas using Google Gemini API",
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Mount static files
ui_path = Path(__file__).parent / "UI_Pages"
if ui_path.exists():
    app.mount("/static", StaticFiles(directory=str(ui_path)), name="static")
    logger.info(f"Static files mounted from {ui_path}")
else:
    logger.warning(f"UI_Pages directory not found at {ui_path}")


try:
    conversation_manager = ConversationManager()
    logger.info("Conversation Manager initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Conversation Manager: {e}")
    conversation_manager = None




api_key = os.getenv("API_KEY")
if not api_key:
    logger.info("API_KEY not found in environment variables")
    raise ValueError("API_KEY not found in environment variables")

agent = BusinessIdeaValidatorAgent(api_key=api_key)


@app.get("/health")
async def health_check():
    try:
        conversation_status = "Connected" if conversation_manager else "Not Connected"
        return JSONResponse({
            "status":"healthy",
            "conversation_status": conversation_status
        })
    except Exception as e:
        logger.error(f"Health Check Failed: {e}")
        return JSONResponse({
            "Status":"Unhealty",
            "Error": str(e)
        })

@app.post("/validate", response_model = ValidationResponse)
def validate_business_idea(request: BusinessIdeaInput) ->ValidationResponse:
    try:
        validation_result =agent.validate_idea(idea = request.idea, conversation_id=request.conversation_id)


        logger.info(f"Validation Completed. Score: {validation_result.score}")
        return validation_result
    
    except ValueError as ve:
        logger.error(f"Validation Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        logger.error(f"Validation Failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate business idea")
    
@app.post("/conversation/start")
async def start_conversation():

    if not conversation_manager:
        raise HTTPException(status_code = 500, detail="Conversation Manager not available")
    
    try:
        conversation_id = str(uuid.uuid4())
        conversation_manager.create_conversation(conversation_id)
        logger.info(f"Started new conversation with ID: {conversation_id}")

        return JSONResponse({
            "Conversation_Id": conversation_id,
            "Status": "Started"
        })
    
    except Exception as e:
        logger.error(f"Failed to start conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start conversation")

@app.get("/conversations")
async def list_conversations():
    if not conversation_manager:
        raise HTTPException(status_code=500, detail="Conversation Manager not available")
    
    try:
        conversations = conversation_manager.get_conversations_with_titles()
        return JSONResponse({
            "conversations": conversations
        })
    
    except Exception as e:
        logger.error(f"Failed to list conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to list conversations")

@app.post("/chat/message", response_model = ValidationResponse)
async def chat_message(request: BusinessIdeaInput) -> ValidationResponse:
    if not conversation_manager:
        raise HTTPException(status_code=500, detail="Conversation Manager not available")

    
    if not request.conversation_id:
        raise HTTPException(status_code=400, detail="Conversation ID is required for chat messages")
    
    try:
        if not conversation_manager.conversation_exists(request.conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        logger.info(f"Chat message in {request.conversation_id[:8]}...: {request.idea[:50]}...")

        # Store user message
        conversation_manager.add_message(request.conversation_id, "user", request.idea)

        # Get input_type from request, or auto-detect if not provided
        input_type = request.input_type
        if not input_type:
            input_type = "new_idea" if ("?" not in request.idea and len(request.idea) >= 30) else "followup"
        
        validated_result = agent.validate_idea(idea=request.idea, conversation_id=request.conversation_id, input_type=input_type)

        # Update conversation title with the validated title (first message only)
        conv_data = conversation_manager.conversations.get(request.conversation_id, {})
        if conv_data.get("title") == "Untitled":
            conversation_manager.conversations[request.conversation_id]["title"] = validated_result.title

        # Store validation result
        conversation_manager.add_message(request.conversation_id, "assistant", json.dumps({
            "title": validated_result.title,
            "score": validated_result.score,
            "verdict": validated_result.verdict,
            "market": validated_result.market,
            "risk": validated_result.risk,
            "opportunities": validated_result.opportunities,
            "competition": validated_result.competition,
            "first_step": validated_result.first_step,
            "summary": validated_result.summary
        }))

        logger.info(f"Chat message processed. Score: {validated_result.score}")
        return validated_result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Chat message processing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@app.delete("/conversation/{conversation_id}")
async def delete_converstion(conversation_id:str):
    try:
        if not conversation_manager:
            raise HTTPException(status_code=500, detail="Conversation Manager not available")
        
        if not conversation_manager.conversation_exists(conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation_manager.delete_conversation(conversation_id)
        logger.info(f"Deleted conversation with ID: {conversation_id}")
        return JSONResponse({
            "Conversation_Id": conversation_id,
            "Status": "Deleted"
        })
    
    except HTTPException as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(status_code=e.status_code, detail="Failed to delete conversation")


@app.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id:str):

    if not conversation_manager:
        raise HTTPException(status_code=500, detail="Conversation Manager not available")
    
    try:
        if not conversation_manager.conversation_exists(conversation_id):
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        history = conversation_manager.get_full_history(conversation_id)

        return JSONResponse({
            "Conversation_Id": conversation_id,
            "History": history
        })
    
    except HTTPException as e:
        logger.error(f"Failed to retrieve conversation history: {e}")
        raise HTTPException(status_code=e.status_code, detail="Failed to retrieve conversation history")


@app.get("/")
async def root():
    """Root endpoint - serves the UI"""
    ui_file = Path(__file__).parent / "UI_Pages" / "index.html"
    if ui_file.exists():
        return FileResponse(ui_file, media_type="text/html")
    return JSONResponse({
        "name": "Business Idea Validator",
        "version": "2.0.0",
        "description": "AI-powered validation of business ideas with conversation memory",
        "endpoints": {
            "health": "GET /health",
            "api_docs": "GET /docs",
            "single_validation": "POST /validate",
            "start_chat": "POST /conversation/start",
            "send_message": "POST /chat/message",
            "get_history": "GET /chat/history/{conversation_id}"
        }
    })

@app.get('/list_models/')
async def list_available_models():
    try:
        models = agent.list_models()
        return JSONResponse({
            "available_models": models
        })
    except Exception as e:
        logger.error(f"Failed to list available models: {e}")
        raise HTTPException(status_code=500, detail="Failed to list available models")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)