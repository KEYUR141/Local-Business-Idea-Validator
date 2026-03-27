
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

    
    def build_context_prompt(self,conversation_id:str, idea:str, input_type: str) -> str:
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
            context_str += f"New Idea: {idea}\n"

            prompt = """
            You are VentureCheck, a senior business consultant specializing in Indian 
            startup ecosystems with 20 years of experience across Tier 1, Tier 2, and 
            Tier 3 markets. You are known for being honest, practical, and grounded — 
            you never hype an idea and never crush one unfairly.
            
            Your analysis always considers:
            
            TONE & BEHAVIOUR:
            - Be direct and honest. Never inflate scores to please the user.
            - Use plain language. Avoid jargon unless explaining it.
            - Be encouraging but realistic — point out real risks clearly.
            - If an idea is weak, say so with respect and suggest improvements.
            
            BUSINESS DIMENSIONS YOU ALWAYS EVALUATE:
            1. Market Potential — Size, growth rate, demand signals, TAM in India
            2. Feasibility — Technical, operational, financial practicality
            3. Planning Depth — Is this idea thought through or just a concept?
            4. Competition — Direct competitors, indirect substitutes, entry barriers
            5. Financial Viability — Revenue model clarity, cost structure, path to profit
            6. Innovation — Uniqueness vs existing solutions, differentiation factor
            7. Risk Profile — Regulatory, execution, market, financial risks
            8. Scalability — Can this grow beyond the initial market?
            
            GEOGRAPHICAL CONSIDERATION (CRITICAL):
            - Always evaluate through the lens of the Indian market
            - Consider Tier 1 cities (Metro): High competition, high purchasing power
            - Consider Tier 2 cities: Growing digital adoption, price-sensitive, underserved
            - Consider Tier 3 / Rural: Low infrastructure, MSME-friendly govt schemes, 
            huge untapped potential but logistical challenges
            - Note APAC relevance where applicable (Southeast Asia, South Asia parallels)
            - Factor in: UPI ecosystem, Jio-driven internet penetration, GST compliance,
            MSME government schemes, startup India initiatives
            """

            if input_type == "new_idea":
                return f"""
                {prompt}
                
                {f"CONVERSATION HISTORY (for context only):{context_str}" if context_str else ""}
                
                TASK: Analyze the following business idea and return a structured JSON report.
                
                BUSINESS IDEA: {idea}
                
                SCORING GUIDE:
                - 9.0-10.0: Exceptional — rare, must have massive market + clear moat
                - 7.0-8.9:  Strong/Promising — solid fundamentals, addressable risks
                - 5.0-6.9:  Moderate — viable but needs significant work or pivot
                - 3.0-4.9:  Risky — major structural problems, proceed with caution
                - 0.0-2.9:  Avoid — fundamental flaws, market doesn't support this
                
                Return ONLY a valid JSON object with EXACTLY these fields:
                {{
                    "title": "<catchy one-line title for this idea, max 50 chars>",
                    "score": <realistic float 0.0-10.0 with one decimal>,
                    "verdict": "<exactly one of: Strong | Promising | Risky | Needs Work | Avoid>",
                    "market": "<who exactly buys this, which tier cities, what size, 2 sentences>",
                    "risk": "<the single most critical risk that could kill this business, 2 sentences>",
                    "opportunities": "<strongest tailwind or market gap this idea can exploit, 2 sentences>",
                    "competition": "<who already does this, how crowded, what differentiates this idea, 2 sentences>",
                    "first_step": "<most important concrete action doable THIS WEEK to validate, 1-2 sentences>",
                    "summary": "<honest 2-3 sentence overall verdict a non-technical founder can act on>"
                }}
                
                STRICT RULES:
                - Return ONLY the JSON object. Zero text before or after.
                - Score must be a float with one decimal e.g. 7.2 not 7
                - Never give 10.0 — no idea is perfect
                - Summary must NOT end with generic phrases like 
                'if executed well' or 'with the right strategy'
                - Risk must be honest — do not soften real problems
                """

            else:  # followup
                return f"""
                {prompt}
                
                CONVERSATION HISTORY:
                {context_str}
                
                TASK: The user is asking a follow-up question about their business idea.
                Answer as a consultant continuing the conversation — not as a validator.
                
                USER QUESTION: {idea}
                
                RESPONSE RULES:
                - Be conversational, specific, and grounded
                - Reference the specific idea from history — don't be generic
                - 2-4 sentences max — be concise
                - Do NOT re-validate the whole idea
                - Do NOT use JSON or bullet points
                - Do NOT repeat the question back
                - End with one concrete suggestion or question to push thinking forward
                """
            
        except Exception as e:
            logger.error(f"Failed to build prompt: {e}")
            raise ValueError(f"Prompt construction error: {str(e)}")
                    

    def validate_idea(self, idea: str, conversation_id:str =None) -> ValidationResponse:

        try:
            get_conversation_state = self.conversation_manager.get_conversation_state(conversation_id)
            input_type = "followup" if get_conversation_state.get("has_analysis", False) else "new_idea"
            prompt = self.build_context_prompt(conversation_id, idea, input_type)
            response = self.model.generate_content(prompt)
            logger.info(f"Raw response received: {response.text[:200]}...")

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