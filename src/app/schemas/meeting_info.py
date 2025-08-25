"""
Defines the Pydantic model for meeting information data.
"""
from typing import List
from pydantic import BaseModel

class MeetingInfo(BaseModel):
    """
    A Pydantic model to validate the structure of formatted meeting information.
    """
    trivia_question: str
    trivia_answer: str
    fun_fact: str
    trending_repos: List[str]
    summary: str

    class Config:
        """Pydantic model configuration."""
        populate_by_name = True
        protected_namespaces = ()
