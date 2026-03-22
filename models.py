from pydantic import BaseModel, Field


class BusinessIdeaInput(BaseModel):

    idea : str = Field(
        ...,
        min_length = 10,
        max_length = 500,
        title = "Business Idea",
        description=" Provide a brief Description of your business idea(10-500 or more Characters)",
 
)

class ValidationResponse(BaseModel):

    score: float = Field(
        ...,
        ge=0,
        le=10,
        description = """A score between 0 and 10 indicating that the business idea given by the user does stand in the actual world or not? In terms of market demand, competition, and feasibility. 
        A score of 0 indicates that the business idea is not viable, while a score of 10 indicates that the business idea is highly viable."""
        
    )

    market: str = Field(
        ...,
        description = """A brief analysis of the market demand for the business idea, including potential customer segments and trends."""
    )

    risk: str = Field(
        ...,
        description = """An assessment of the potential risks and challenges associated with the business idea, including competition, regulatory issues, and operational challenges."""
    )

    competition: str = Field(
        ...,
        description="Competitive analysis of the business idea, including an overview of existing competitors, their strengths and weaknesses, and how the proposed business idea differentiates itself in the market."
    )

    first_step: str = Field(
        ...,
        description="A recommended first step for the user to take in order to validate or implement their business idea, such as conducting market research, creating a prototype, or seeking feedback from potential customers."
    )

    summary: str = Field(
        ...,
        description="A concise summary of the overall assessment of the business idea, highlighting its strengths, weaknesses, and potential for success."
    )