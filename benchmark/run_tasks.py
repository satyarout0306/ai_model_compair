"""Benchmark runner supporting multiple task difficulties."""

import json
import time
from pathlib import Path
from typing import Optional
import argparse
from datetime import datetime

from core.generator import generate_structured, GenerationResult
from benchmark.load_data import load_employee_tickets_from_csv
from benchmark.tasks import TaskDifficulty, get_task_by_difficulty, list_tasks


def run_difficulty_benchmark(
    models: list[str],
    difficulty: TaskDifficulty,
    test_cases: list[dict],
    max_retries: int = 3,
    output_dir: Optional[str] = None,
) -> dict:
    """
    Run benchmark for a specific difficulty level.
    
    Args:
        models: List of Ollama model names
        difficulty: TaskDifficulty level (SIMPLE, MEDIUM, HARD)
        test_cases: Loaded test cases
        max_retries: Max retry attempts
        output_dir: Results directory
    
    Returns:
        Benchmark results dictionary
    """
    task = get_task_by_difficulty(difficulty)
    if not task:
        raise ValueError(f"Unknown task difficulty: {difficulty}")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "difficulty": difficulty.value,
        "task_name": task["name"],
        "task_description": task["description"],
        "models_tested": models,
        "total_test_cases": len(test_cases),
        "max_retries": max_retries,
        "results_by_model": {},
    }
    
    print(f"\n{'='*70}")
    print(f"TASK: {task['name']} ({difficulty.value.upper()})")
    print(f"Description: {task['description']}")
    print(f"Test Cases: {len(test_cases)}")
    print(f"{'='*70}\n")
    
    for model in models:
        print(f"\n{'─'*70}")
        print(f"Model: {model}")
        print(f"{'─'*70}")
        
        model_results = {
            "model": model,
            "test_cases": [],
            "summary": {
                "total_cases": len(test_cases),
                "successful": 0,
                "failed": 0,
                "avg_attempts": 0,
                "avg_latency_seconds": 0,
                "first_try_success_rate": 0,
                "accuracy": 0,
            }
        }
        
        total_attempts = 0
        total_latency = 0
        first_try_successes = 0
        correct_count = 0
        
        for case_idx, case in enumerate(test_cases, 1):
            # Prepare input and ground truth using task functions
            input_text = task["input_fn"](case["ground_truth"])
            ground_truth = task["ground_truth_fn"](case["ground_truth"])
            
            print(f"  [{case_idx}/{len(test_cases)}] {case['ground_truth']['ticket_id']} - {case['ground_truth']['issue_category'][:30]}", end=" ")
            
            # Generate structured output
            result = generate_structured(
                model=model,
                user_input=input_text,
                schema=task["schema"],
                max_retries=max_retries,
            )
            
            # Check accuracy
            is_correct = False
            if result.success and result.parsed:
                # Validate key fields match
                try:
                    parsed_dict = result.parsed.model_dump()
                    # Check if critical fields match
                    critical_fields = ["ticket_id", "priority", "resolution_status"]
                    is_correct = all(
                        parsed_dict.get(field) == ground_truth.get(field)
                        for field in critical_fields
                        if field in ground_truth
                    )
                except Exception as e:
                    is_correct = False
            
            # Record result
            case_result = {
                "ticket_id": case['ground_truth']['ticket_id'],
                "category": case['ground_truth']['issue_category'],
                "success": result.success,
                "correct": is_correct,
                "attempts": result.attempts,
                "latency_seconds": result.latency_seconds,
                "first_try": result.attempts == 1,
                "error": result.final_error,
            }
            model_results["test_cases"].append(case_result)
            
            # Update metrics
            if result.success:
                model_results["summary"]["successful"] += 1
                if result.attempts == 1:
                    first_try_successes += 1
                if is_correct:
                    correct_count += 1
            else:
                model_results["summary"]["failed"] += 1
            
            total_attempts += result.attempts
            total_latency += result.latency_seconds
            
            # Print status
            status = "✓" if result.success else "✗"
            attempts_str = f"{result.attempts}x" if result.attempts > 1 else "1x"
            print(f"{status} {attempts_str} {result.latency_seconds:.2f}s")
        
        # Calculate summary stats
        if model_results["summary"]["successful"] > 0:
            model_results["summary"]["avg_attempts"] = total_attempts / model_results["summary"]["successful"]
        model_results["summary"]["avg_latency_seconds"] = total_latency / len(test_cases)
        model_results["summary"]["first_try_success_rate"] = (
            first_try_successes / len(test_cases) * 100 if test_cases else 0
        )
        model_results["summary"]["accuracy"] = (
            correct_count / len(test_cases) * 100 if test_cases else 0
        )
        
        results["results_by_model"][model] = model_results
        
        # Print summary for this model
        print(f"\n  Summary:")
        print(f"    Success: {model_results['summary']['successful']}/{model_results['summary']['total_cases']}")
        print(f"    Accuracy: {model_results['summary']['accuracy']:.1f}%")
        print(f"    First-try: {model_results['summary']['first_try_success_rate']:.1f}%")
        print(f"    Avg attempts: {model_results['summary']['avg_attempts']:.2f}")
        print(f"    Avg latency: {model_results['summary']['avg_latency_seconds']:.2f}s")
    
    return results


def run_all_difficulties(
    models: list[str],
    test_cases: list[dict],
    max_retries: int = 3,
    output_dir: Optional[str] = None,
) -> dict:
    """Run benchmarks for all difficulty levels."""
    all_results = {
        "timestamp": datetime.now().isoformat(),
        "models": models,
        "total_test_cases": len(test_cases),
        "difficulties": {},
    }
    
    for difficulty in TaskDifficulty:
        results = run_difficulty_benchmark(
            models=models,
            difficulty=difficulty,
            test_cases=test_cases,
            max_retries=max_retries,
        )
        all_results["difficulties"][difficulty.value] = results
    
    # Save all results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        results_file = output_path / f"benchmark_all_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.write_text(json.dumps(all_results, indent=2, default=str))
        print(f"\n✓ All results saved to: {results_file}")
    
    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Ollama models on employee tickets (multi-difficulty)")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["llama2-7b-chat"],
        help="Ollama models to benchmark"
    )
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["simple", "medium", "hard", "all"],
        default="all",
        help="Task difficulty level (default: all)"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Max retries per test case (default: 3)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="benchmark/results",
        help="Results directory"
    )
    parser.add_argument(
        "--csv-path",
        type=str,
        help="Path to CSV file"
    )
    parser.add_argument(
        "--conversations-dir",
        type=str,
        help="Path to conversations folder"
    )
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="List all available tasks and exit"
    )
    
    args = parser.parse_args()
    
    # List tasks if requested
    if args.list_tasks:
        print("\nAvailable Tasks:")
        for task in list_tasks():
            print(f"  • {task}")
        exit(0)
    
    # Load test data
    print("Loading test data...")
    test_cases = load_employee_tickets_from_csv(
        csv_path=args.csv_path or str(
            Path(__file__).resolve().parent.parent / "test_data" / "employee_ticket" / "Historical_ticket_data.csv"
        ),
        conversations_dir=args.conversations_dir or str(
            Path(__file__).resolve().parent.parent / "test_data" / "employee_ticket" / "Conversation" / "Conversation"
        ),
    )
    print(f"✓ Loaded {len(test_cases)} test cases\n")
    
    # Run benchmark
    if args.difficulty == "all":
        results = run_all_difficulties(
            models=args.models,
            test_cases=test_cases,
            max_retries=args.max_retries,
            output_dir=args.output_dir,
        )
    else:
        results = run_difficulty_benchmark(
            models=args.models,
            difficulty=TaskDifficulty(args.difficulty),
            test_cases=test_cases,
            max_retries=args.max_retries,
            output_dir=args.output_dir,
        )
        
        # Save single difficulty results
        if args.output_dir:
            output_path = Path(args.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            results_file = output_path / f"benchmark_{args.difficulty}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_file.write_text(json.dumps(results, indent=2, default=str))
            print(f"\n✓ Results saved to: {results_file}")
