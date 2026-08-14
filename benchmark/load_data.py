"""Load employee ticket test data from CSV and conversation files."""

import csv
import json
from pathlib import Path
from typing import Optional
import re

from schemas import EmployeeTicket, Priority, ResolutionStatus


def load_conversation_for_category(category: str, conversations_dir: Path) -> Optional[str]:
    """Load conversation text file for a given category."""
    # Try to find the conversation file
    for file in conversations_dir.glob(f"**/{category}.txt"):
        return file.read_text(encoding='utf-8')
    return None


def load_employee_tickets_from_csv(csv_path: str, conversations_dir: Optional[str] = None) -> list[dict]:
    """
    Load employee tickets from CSV and pair with conversations.
    
    Args:
        csv_path: Path to Historical_ticket_data.csv
        conversations_dir: Path to Conversation folder containing conversation txt files
    
    Returns:
        List of test cases with input_text and ground_truth
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    if conversations_dir:
        conversations_dir = Path(conversations_dir)
    
    cases = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader):
            # Clean up column names (remove extra spaces)
            cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
            
            # Parse the ticket
            ticket = EmployeeTicket(
                ticket_id=cleaned_row.get('Ticket ID', ''),
                issue_category=cleaned_row.get('Issue Category', ''),
                sentiment=cleaned_row.get('Sentiment', ''),
                priority=Priority(cleaned_row.get('Priority', 'Medium')),
                solution=cleaned_row.get('Solution', ''),
                resolution_status=ResolutionStatus('Resolved') if cleaned_row.get('Resolution Status', '').lower() == 'resolved' else ResolutionStatus('Open'),
                date_of_resolution=cleaned_row.get('Date of Resolution') or None,
            )
            
            # Load corresponding conversation if available
            conversation_text = ""
            if conversations_dir:
                conv = load_conversation_for_category(
                    ticket.issue_category, 
                    conversations_dir
                )
                if conv:
                    conversation_text = conv
            
            # Create input text combining category, sentiment, and conversation
            input_text = f"""Extract ticket information from this support conversation:

Category: {ticket.issue_category}
Customer Sentiment: {ticket.sentiment}

Conversation:
{conversation_text}

Please extract the following:
- Ticket ID
- Issue Category
- Customer Sentiment
- Priority Level
- Solution Provided
- Resolution Status
- Date of Resolution (if available)
"""
            
            cases.append({
                "task": "employee_tickets",
                "case_index": idx,
                "ticket_id": ticket.ticket_id,
                "input_text": input_text,
                "ground_truth": ticket.model_dump(),
            })
    
    return cases


def load_benchmark_dataset(
    csv_path: Optional[str] = None,
    conversations_dir: Optional[str] = None,
    use_default: bool = True
) -> list[dict]:
    """
    Load benchmark dataset from employee tickets.
    
    If no paths provided, uses default test_data location.
    """
    if use_default and (not csv_path or not conversations_dir):
        # Use default paths
        base_path = Path(__file__).resolve().parent.parent / "test_data" / "employee_ticket"
        csv_path = csv_path or str(base_path / "Historical_ticket_data.csv")
        conversations_dir = conversations_dir or str(base_path / "Conversation" / "Conversation")
    
    return load_employee_tickets_from_csv(csv_path, conversations_dir)


if __name__ == "__main__":
    # Test the loader
    cases = load_benchmark_dataset()
    print(f"Loaded {len(cases)} test cases")
    for case in cases[:2]:
        print(f"\nTicket: {case['ticket_id']}")
        print(f"Input length: {len(case['input_text'])} chars")
        print(f"Ground truth: {case['ground_truth']}")
