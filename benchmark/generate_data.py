"""Generates synthetic test cases WITH ground truth, so the benchmark can score
field-level accuracy -- not just "did it produce valid JSON."

Approach: build a random Pydantic instance first (so we know the correct
answer), then render it into natural-language text a model has to extract
from. This gives you a real eval set instead of just a schema-conformance
check.

Usage:
    python -m benchmarks.generate_data --count 20
Writes benchmarks/generated_cases.json
"""

import argparse
import json
import random
from pathlib import Path

from faker import Faker

from schemas import Person, Invoice, LineItem, Ticket, Priority, Status

fake = Faker()

OCCUPATIONS = [
    "civil engineer", "data scientist", "high school teacher", "nurse",
    "graphic designer", "accountant", "software developer", "electrician",
    "marketing manager", "chef",
]

PRODUCTS = [
    "Widget A", "Widget B", "Steel Bracket", "USB Cable", "Office Chair",
    "Laptop Stand", "Printer Ink", "Packing Tape", "Safety Gloves", "LED Bulb",
]

BUG_TITLES = [
    "Login page crashes on mobile Safari",
    "Database connection pool exhausted under load",
    "Typo in footer copyright year",
    "Checkout button unresponsive on Firefox",
    "Email notifications delayed by several hours",
    "Dark mode toggle resets on page refresh",
]


# ---------- Ground-truth object generators ----------

def gen_person() -> Person:
    return Person(
        name=fake.name(),
        age=random.randint(18, 75),
        occupation=random.choice(OCCUPATIONS),
    )


def gen_invoice() -> Invoice:
    items = [
        LineItem(
            description=random.choice(PRODUCTS),
            quantity=random.randint(1, 10),
            unit_price=round(random.uniform(2, 200), 2),
        )
        for _ in range(random.randint(1, 4))
    ]
    total = round(sum(i.quantity * i.unit_price for i in items), 2)
    return Invoice(
        vendor=fake.company(),
        invoice_number=f"INV-{random.randint(1000, 9999)}",
        items=items,
        total=total,
    )


def gen_ticket() -> Ticket:
    status = random.choice(list(Status))
    resolved_note = (
        fake.sentence(nb_words=8) if status == Status.RESOLVED else None
    )
    return Ticket(
        title=random.choice(BUG_TITLES),
        priority=random.choice(list(Priority)),
        status=status,
        assignee=fake.first_name() if random.random() > 0.3 else None,
        resolved_note=resolved_note,
    )


# ---------- Render ground-truth object -> natural language text ----------

def render_person(p: Person) -> str:
    templates = [
        f"{p.name}, {p.age}, works as a {p.occupation}.",
        f"Meet {p.name}, a {p.age}-year-old {p.occupation}.",
        f"Applicant {p.name} (age {p.age}) listed their occupation as '{p.occupation}'.",
    ]
    return random.choice(templates)


def render_invoice(inv: Invoice) -> str:
    items_text = "; ".join(
        f"{i.quantity}x {i.description} @ ${i.unit_price:.2f}" for i in inv.items
    )
    return (
        f"Vendor: {inv.vendor}, Invoice #{inv.invoice_number}. "
        f"Items: {items_text}. Total should be the sum of all line items."
    )


def render_ticket(t: Ticket) -> str:
    assignee_text = f"assigned to {t.assignee}" if t.assignee else "currently unassigned"
    base = (
        f"Ticket: '{t.title}'. Priority: {t.priority.value}. "
        f"Status: {t.status.value}. {assignee_text}."
    )
    if t.status == Status.RESOLVED:
        base += f" Resolution note: {t.resolved_note}"
    return base


# ---------- Assemble dataset ----------

GENERATORS = {
    "simple_person": (gen_person, render_person),
    "medium_invoice": (gen_invoice, render_invoice),
    "hard_ticket": (gen_ticket, render_ticket),
}


def generate_dataset(count_per_task: int = 20, seed: int | None = 42) -> list[dict]:
    if seed is not None:
        random.seed(seed)
        Faker.seed(seed)

    cases = []
    for task_name, (gen_fn, render_fn) in GENERATORS.items():
        for i in range(count_per_task):
            obj = gen_fn()
            text = render_fn(obj)
            cases.append(
                {
                    "task": task_name,
                    "case_index": i,
                    "input_text": text,
                    "ground_truth": json.loads(obj.model_dump_json()),
                }
            )
    return cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20, help="cases per task")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    dataset = generate_dataset(count_per_task=args.count, seed=args.seed)
    out_path = Path(__file__).resolve().parent / "generated_cases.json"
    out_path.write_text(json.dumps(dataset, indent=2))
    print(f"Wrote {len(dataset)} cases ({args.count} per task x {len(GENERATORS)} tasks) to {out_path}")
