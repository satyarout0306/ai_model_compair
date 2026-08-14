"""Define different difficulty levels of ticket extraction tasks.

This module uses schemas from schemas/ (simple.py, medium.py, hard.py) and pairs
them with input formatting functions and ground truth extraction functions.
"""

from enum import Enum
from typing import Optional
from schemas.simple import SimpleTicketInfo
from schemas.medium import MediumTicketAnalysis
from schemas.hard import HardTicketExtraction


class TaskDifficulty(str, Enum):
    """Task difficulty levels."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    HARD = "hard"


# ============ SIMPLE TASK ============
# Extract basic ticket metadata from structured text
# Schema: SimpleTicketInfo (from schemas/simple.py)


def simple_task_input(ticket_data: dict) -> str:
    """Format input for simple task."""
    return f"""Extract the basic ticket information:

Ticket ID: {ticket_data['ticket_id']}
Priority: {ticket_data['priority']}
Resolution Status: {ticket_data['resolution_status']}

Extract: ticket_id, priority, resolution_status
"""

def simple_task_ground_truth(ticket_data: dict) -> dict:
    """Ground truth for simple task."""
    return {
        "ticket_id": ticket_data["ticket_id"],
        "priority": ticket_data["priority"],
        "resolution_status": ticket_data["resolution_status"],
    }


# ============ MEDIUM TASK ============
# Extract ticket info + analyze conversation content
# Schema: MediumTicketAnalysis (from schemas/medium.py)


def medium_task_input(ticket_data: dict) -> str:
    """Format input for medium task."""
    return f"""Analyze this support ticket and extract key information:

TICKET METADATA:
- ID: {ticket_data['ticket_id']}
- Category: {ticket_data['issue_category']}
- Priority: {ticket_data['priority']}
- Status: {ticket_data['resolution_status']}
- Solution: {ticket_data['solution']}

Extract all fields in the specified format.
"""

def medium_task_ground_truth(ticket_data: dict) -> dict:
    """Ground truth for medium task."""
    return {
        "ticket_id": ticket_data["ticket_id"],
        "issue_category": ticket_data["issue_category"],
        "priority": ticket_data["priority"],
        "resolution_status": ticket_data["resolution_status"],
        "solution": ticket_data["solution"],
    }


# ============ HARD TASK ============
# Full extraction with sentiment analysis from conversation
# Schema: HardTicketExtraction (from schemas/hard.py)


def hard_task_input(ticket_data: dict, conversation: str = "") -> str:
    """Format input for hard task with full conversation."""
    return f"""Analyze this support conversation and extract all ticket information:

TICKET CONTEXT:
- ID: {ticket_data['ticket_id']}
- Category: {ticket_data['issue_category']}
- Sentiment: {ticket_data['sentiment']}
- Priority: {ticket_data['priority']}
- Resolution Date: {ticket_data.get('date_of_resolution', 'N/A')}

CONVERSATION:
{conversation}

Extract:
1. All ticket metadata
2. Key points from the conversation
3. Sentiment analysis
4. Complete solution provided

Ensure accuracy for all fields.
"""

def hard_task_ground_truth(ticket_data: dict, key_points: list[str] = None) -> dict:
    """Ground truth for hard task."""
    return {
        "ticket_id": ticket_data["ticket_id"],
        "issue_category": ticket_data["issue_category"],
        "sentiment": ticket_data["sentiment"],
        "priority": ticket_data["priority"],
        "solution": ticket_data["solution"],
        "resolution_status": ticket_data["resolution_status"],
        "date_of_resolution": ticket_data.get("date_of_resolution"),
        "key_points": key_points or [],
    }


# ============ TASK REGISTRY ============

TASKS = {
    TaskDifficulty.SIMPLE: {
        "name": "Simple Ticket Extraction",
        "description": "Extract basic ticket ID, priority, and status",
        "schema": SimpleTicketInfo,
        "input_fn": simple_task_input,
        "ground_truth_fn": simple_task_ground_truth,
        "difficulty": 1,
    },
    TaskDifficulty.MEDIUM: {
        "name": "Medium Ticket Analysis",
        "description": "Extract ticket metadata and solution from structured data",
        "schema": MediumTicketAnalysis,
        "input_fn": medium_task_input,
        "ground_truth_fn": medium_task_ground_truth,
        "difficulty": 2,
    },
    TaskDifficulty.HARD: {
        "name": "Hard Ticket Extraction",
        "description": "Full extraction with sentiment analysis from natural conversation",
        "schema": HardTicketExtraction,
        "input_fn": hard_task_input,
        "ground_truth_fn": hard_task_ground_truth,
        "difficulty": 3,
    },
}


def get_task_by_difficulty(difficulty: TaskDifficulty) -> dict:
    """Get task configuration by difficulty level."""
    return TASKS.get(difficulty)


def list_tasks() -> list[str]:
    """List all available tasks."""
    return [f"{diff.value.upper()}: {TASKS[diff]['name']}" for diff in TaskDifficulty]
