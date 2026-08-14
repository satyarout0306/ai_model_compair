"""Medium task schema: Full ticket analysis with solution extraction."""

from pydantic import BaseModel, Field


class MediumTicketAnalysis(BaseModel):
    """
    Medium task: Extract ticket info and analyze conversation.
    
    Difficulty: ⭐⭐ (Medium)
    
    Expected accuracy: 75-85%
    Expected latency: 0.7-1.2s
    
    Tests model's ability to:
    - Extract complete ticket metadata
    - Categorize issues accurately
    - Identify priority levels
    - Extract solution text from structured data
    - Track resolution status
    """
    ticket_id: str = Field(..., description="Unique ticket identifier")
    issue_category: str = Field(..., description="Category of the issue (Software Installation Failure, Payment Gateway Integration Failure, etc.)")
    priority: str = Field(..., description="Priority level (Low, Medium, High, Critical)")
    resolution_status: str = Field(..., description="Resolution status (Open, In Progress, Resolved, Closed)")
    solution: str = Field(..., description="Solution provided to resolve the issue")
