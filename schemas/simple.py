"""Simple task schema: Basic ticket information extraction."""

from pydantic import BaseModel, Field


class SimpleTicketInfo(BaseModel):
    """
    Simple task: Extract basic ticket information.
    
    Difficulty: ⭐ (Easy)
    
    Expected accuracy: 85-95%
    Expected latency: 0.5-0.8s
    
    Tests model's ability to extract:
    - Unique ticket identifier
    - Priority level classification
    - Resolution status tracking
    """
    ticket_id: str = Field(..., description="Unique ticket identifier")
    priority: str = Field(..., description="Priority level (Low, Medium, High, Critical)")
    resolution_status: str = Field(..., description="Status (Open, Resolved, In Progress, Closed)")
