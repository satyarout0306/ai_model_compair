"""Hard task schema: Full extraction with NLU and sentiment analysis."""

from pydantic import BaseModel, Field
from typing import Optional


class HardTicketExtraction(BaseModel):
    """
    Hard task: Full extraction with sentiment analysis from conversation.
    
    Difficulty: ⭐⭐⭐ (Hard - NLU Intensive)
    
    Expected accuracy: 60-75%
    Expected latency: 1.0-1.5s
    
    Tests model's ability to:
    - Extract all ticket metadata
    - Perform sentiment analysis from conversations
    - Identify key discussion points
    - Understand context and emotion
    - Extract implicit information from natural language
    - Handle multi-turn conversations
    """
    ticket_id: str = Field(..., description="Unique ticket identifier")
    issue_category: str = Field(..., description="Category of the issue")
    sentiment: str = Field(..., description="Customer sentiment (Frustrated, Confused, Annoyed, Satisfied, Neutral, etc.)")
    priority: str = Field(..., description="Priority level (Low, Medium, High, Critical)")
    solution: str = Field(..., description="Solution provided to resolve the issue")
    resolution_status: str = Field(..., description="Resolution status (Open, In Progress, Resolved, Closed)")
    date_of_resolution: Optional[str] = Field(None, description="Date when the ticket was resolved (if available)")
    key_points: list[str] = Field(default_factory=list, description="Key discussion points extracted from the conversation")
