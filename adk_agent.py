

import os
import logging
from dotenv import load_dotenv

try:
    from google.adk.agents import LlmAgent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    logging.warning("Google ADK not installed. Install with: pip install google-adk")

load_dotenv()
logger = logging.getLogger(__name__)

# VentureCheck Persona (same as in agent.py)
VENTURECHECK_INSTRUCTION = """You are VentureCheck, a senior business consultant specializing in Indian 
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
- Consider Tier 3 / Rural: Low infrastructure, MSME-friendly govt schemes
- Note APAC relevance where applicable
- Factor in: UPI ecosystem, Jio-driven internet, GST compliance, MSME schemes
"""


def create_adk_agent():
   
    if not ADK_AVAILABLE:
        logger.error("Google ADK not available. Cannot create ADK agent.")
        return None
    
    try:
        adk_agent = LlmAgent(
            name="venture_check_validator",
            model="gemini-2.5-flash",
            description="AI-powered validation of business ideas for Indian startups and entrepreneurs",
            instruction=VENTURECHECK_INSTRUCTION
        )
        logger.info("ADK Agent created successfully")
        return adk_agent
    except Exception as e:
        logger.error(f"Failed to create ADK Agent: {e}")
        return None


def create_adk_runner():
   
    if not ADK_AVAILABLE:
        return None
    
    try:
        runner = Runner(
            app_name="business_idea_validator",
            session_service=InMemorySessionService()
        )
        logger.info("ADK Runner created successfully")
        return runner
    except Exception as e:
        logger.error(f"Failed to create ADK Runner: {e}")
        return None


# For demonstration: Show how to use ADK directly
if __name__ == "__main__" and ADK_AVAILABLE:
    """
    Standalone ADK Agent Demo
    This demonstrates how the agent works with Google ADK framework
    """
    logger.info("Starting ADK Agent Demo")
    
    agent = create_adk_agent()
    if agent:
        logger.info(f"Agent Name: {agent.name}")
        logger.info(f"Model: {agent.model}")
        logger.info("ADK Agent ready for business idea validation")
