"""
Defines the Pydantic model for tech trivia data.
"""
from typing import List
from pydantic import BaseModel, Field

class TechTriviaQuestion(BaseModel):
    """
    A Pydantic model to validate the structure of a tech trivia question.
    """
    category: str
    type: str
    difficulty: str
    question: str
    correct_answer: str
    incorrect_answers: List[str]

class TechTriviaResponse(BaseModel):
    """
    A Pydantic model to validate the structure of a tech trivia API response.
    """
    response_code: int = Field(..., alias="response_code")
    results: List[TechTriviaQuestion]

    class Config:
        """Pydantic model configuration."""
        populate_by_name = True
        protected_namespaces = ()
