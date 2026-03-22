import os 
import logging 
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from models import ValidationResponse, BusinessIdeaInput
from agent import BusinessIdeaValidatorAgent

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title = "Business Idea Validator",
    description = "AI-powered validation of business ideas using Google Gemini API",
    version = "1.0.0"
)

api_key = os.getenv("Google_API_KEY")
if not api_key:
    logger.error("Google API Key not found in the environment.")

agent = BusinessIdeaValidatorAgent(api_key=api_key)

@app.get("/health")
async def health_check():
    try:
        return JSONResponse({
            "status":"healthy"
        })
    except Exception as e:
        logger.error(f"Health Check Failed: {e}")
        return JSONResponse({
            "Status":"Unhealty",
            "Error": str(e)
        })

app.post("/validate", response_model = ValidationResponse)
def validate_business_idea(request: BusinessIdeaInput) ->ValidationResponse:
    try:
        validation_result =agent.validate_idea(request.idea)

        logger.info(f"Validation Completed. Score: {validation_result.score}")
        return validation_result
    
    except ValueError as ve:
        logger.error(f"Validation Error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    
    except Exception as e:
        logger.error(f"Validation Failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate business idea")
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)