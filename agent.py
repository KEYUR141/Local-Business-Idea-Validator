
import json
import logging
import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from models import ValidationResponse
import google.generativeai as genai
# from redis_client import RedisConversationManager
from memory import InMemoryConversationManager as ConversationManager
logger = logging.getLogger(__name__)


class BusinessIdeaValidatorAgent:
    """Business Idea Validator using Google Gemini API with Service Account"""
    
    def __init__(self, api_key: str):
        """Initialize with service account credentials"""
        logger.info("Initializing Gemini validator with service account")
        
        # Load service account credentials
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
        self.conversation_manager = ConversationManager()

    
    def build_context_prompt(self,conversation_id:str, idea:str) -> str:
        try:
            context_str= ""

            if conversation_id and self.conversation_manager:
                history = self.conversation_manager.get_last_messages(conversation_id, count=8)

                if history:
                    context_str += "Previous Conversation History:\n"
                    for msg in history:
                        role = "User" if msg["role"] == "user" else "Assistant"
                        context_str += f"{role}:{msg['content']}\n"
                    context_str +="\n" 
            prompt = f"""
            {context_str}

            You are an experienced business consultant evaluating startup ideas.

            Given this business idea, provide a structured validation in VALID JSON format ONLY.

            BUSINESS IDEA: {idea}

            Return your analysis as a valid JSON object with EXACTLY these fields:
            {{
            "score": <number between 0.0 and 10.0>(The Score can be in decimal to provide a good statistics),
            "verdict": "<Options: 'Strong', 'Promising', 'Risky', 'Needs Work', 'Avoid'>",
            "market": "<specific target market description, 1-2 sentences>",
            "risk": "<single most critical risk or challenge, 1-2 sentences>",
            "opportunities": "<potential opportunities and advantages, 1-2 sentences>",
            "competition": "<honest competitive landscape assessment, 1-2 sentences>",
            "first_step": "<concrete, actionable first step doable this week, 1-2 sentences>",
            "summary": "<overall assessment in 2-3 plain sentences>"
            }}

            CRITICAL RULES:
            1. Return ONLY valid JSON. No markdown, no explanations, no text before or after.
            2. Score should be realistic (0-10), not inflated.
            3. Risk section must be honest about challenges.
            4. Summary must be readable to a non-technical person.

            Return the JSON object now:"""

            return prompt
        
        except Exception as e:
            logger.error(f"Error Building Prompt: {e}")
            raise ValueError("Failed to build prompt for validation")
        

    def validate_idea(self, idea: str, conversation_id:str =None) -> ValidationResponse:

        try:
            logger.info(f"Validating idea: {idea[:50]}...")
            prompt = self.build_context_prompt(conversation_id, idea)
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Remove markdown wrapping if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            # Parse JSON
            data = json.loads(text.strip())
            validation = ValidationResponse(**data)

            if conversation_id and self.conversation_manager:
                self.conversation_manager.add_message(conversation_id, role = "user", context = idea)
                self.conversation_manager.add_message(conversation_id, role="assistant", context = validation.summary)
            
            logger.info(f"Validation successful. Score: {validation.score}")
            return validation
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError("Received invalid JSON from model")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise ValueError(f"Validation error: {str(e)}")