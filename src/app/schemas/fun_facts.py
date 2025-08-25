"""
Defines the Pydantic model for fun facts data.
"""
from pydantic import BaseModel, Field

class FunFact(BaseModel):
    """
    A Pydantic model to validate the structure of a fun fact.
    """
    id: str
    text: str
    source: str
    source_url: str = Field(..., alias="source_url")
    language: str
    permalink: str

    class Config:
        """Pydantic model configuration."""
        populate_by_name = True
        protected_namespaces = ()
