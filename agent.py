# import json
# import logging 
# import google.genai as genai
# from models import ValidationResponse

# logger = logging.getLogger(__name__)

# class BusinessIdeaValidatorAgent:

#     def __init__(self, api_key: str):
#         self.client = genai.Client(api_key=api_key)
#         self.model_name = "gemini-1.5-flash"


#     def build_prompt(self, idea:str) -> str:
#         prompt = f"""You are an experienced business consultant evaluating startup ideas.

#         Given this business idea, provide a structured validation in VALID JSON format ONLY.

#         BUSINESS IDEA: {idea}

#         Return your analysis as a valid JSON object with EXACTLY these fields:
#         {{
#         "score": <number between 0.0 and 10.0>,
#         "market": "<specific target market description, 1-2 sentences>",
#         "risk": "<single most critical risk or challenge, 1-2 sentences>",
#         "competition": "<honest competitive landscape assessment, 1-2 sentences>",
#         "first_step": "<concrete, actionable first step doable this week, 1-2 sentences>",
#         "summary": "<overall assessment in 2-3 plain sentences>"
#         }}

#         CRITICAL RULES:
#         1. Return ONLY valid JSON. No markdown, no explanations, no text before or after.
#         2. Score should be realistic (0-10), not inflated.
#         3. Risk section must be honest about challenges.
#         4. Summary must be readable to a non-technical person.

#         Return the JSON object now:"""
        
#         return prompt
    
#     def validate_idea(self, idea:str) -> ValidationResponse:
#         prompt = self.build_prompt(idea)

#         try:
#             logger.info("Sending prompt to Gemini model for validation.")

#             response = self.client.generate_content(model=self.model_name, contents=prompt)
#             response_text = response.text.strip()

#             response_json = self._extract_json(response_text)

#             response_data = json.loads(response_json)
#             validation = ValidationResponse(**response_data)

#             logger.info(f"Validation Successful. Score: {validation.score}")
#             return validation
        
#         except json.JSONDecodeError as e:
#             logger.error(f"Failed to parse Json: {e}")
#             raise ValueError("Received invalid JSON from model")
#         except Exception as e:
#             logger.error(f"Validation Failed: {e}")
#             raise ValueError("An error occurred during validation")
        


#     def _extract_json(self, text:str) -> str:
#         try:
#             if "```json" in text:
#                 text = text.split("```json")[1].split("```")[0].strip()
            
#             elif "```" in text:
#                 text = text.split("```")[1].split("```")[0].strip()
            
#             return text.strip()
        
#         except Exception as e:
#             logger.error(f"Error extracting JSON: {e}")
#             raise ValueError("Could not extract JSON from model response")


import json
import logging
import requests
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from models import ValidationResponse
import google.generativeai as genai

logger = logging.getLogger(__name__)


class BusinessIdeaValidatorAgent:
    """Business Idea Validator using Google Gemini API with Service Account"""
    
    def __init__(self, api_key: str):
        """Initialize with service account credentials"""
        logger.info("Initializing Gemini validator with service account")
        
        # Load service account credentials
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")


    
    
    def validate_idea(self, idea: str) -> ValidationResponse:
        """Validate a business idea using Gemini"""
        
        prompt = f"""You are an experienced business consultant evaluating startup ideas.

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
        
        try:
            logger.info(f"Validating idea: {idea[:50]}...")
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
            
            logger.info(f"Validation successful. Score: {validation.score}")
            return validation
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise ValueError("Received invalid JSON from model")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise ValueError(f"Validation error: {str(e)}")