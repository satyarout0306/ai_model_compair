"""Run benchmarks against employee ticket data using different Ollama models."""

import json
import time
from pathlib import Path
from typing import Optional
import argparse
from datetime import datetime

from core.generator import generate_structured, GenerationResult
from schemas import EmployeeTicket
from benchmark.load_data import load_benchmark_dataset


def run_benchmark(
    models: list[str],
    test_cases: list[dict],
    max_retries: int = 3,
    output_dir: Optional[str] = None,
) -> dict:
    """
    Run benchmark across multiple models and test cases.
    
    Args:
        models: List of Ollama model names to benchmark
        test_cases: List of test cases (from load_benchmark_dataset)
        max_retries: Max retry attempts per case
        output_dir: Directory to save results
    
    Returns:
        Dictionary with benchmark results
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "models_tested": models,
        "total_test_cases": len(test_cases),
        "max_retries": max_retries,
        "results_by_model": {},
    }
    
    for model in models:
        print(f"\n{'='*60}")
        print(f"Benchmarking model: {model}")
        print(f"{'='*60}")
        
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
            }
        }
        
        total_attempts = 0
        total_latency = 0
        first_try_successes = 0
        
        for case_idx, case in enumerate(test_cases, 1):
            print(f"\nCase {case_idx}/{len(test_cases)}: {case['ticket_id']}")
            print(f"  Category: {case['ground_truth']['issue_category']}")
            
            # Generate structured output
            result = generate_structured(
                model=model,
                user_input=case["input_text"],
                schema=EmployeeTicket,
                max_retries=max_retries,
            )
            
            # Check if matches ground truth
            is_correct = False
            if result.success and result.parsed:
                is_correct = (
                    result.parsed.issue_category == case["ground_truth"]["issue_category"] and
                    result.parsed.priority == case["ground_truth"]["priority"] and
                    result.parsed.sentiment == case["ground_truth"]["sentiment"]
                )
            
            # Record result
            case_result = {
                "ticket_id": case['ticket_id'],
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
            else:
                model_results["summary"]["failed"] += 1
            
            total_attempts += result.attempts
            total_latency += result.latency_seconds
            
            status = "✓" if result.success else "✗"
            print(f"  {status} Attempts: {result.attempts} | Latency: {result.latency_seconds:.2f}s")
            if not result.success:
                print(f"    Error: {result.final_error[:100]}")
        
        # Calculate summary stats
        if model_results["summary"]["successful"] > 0:
            model_results["summary"]["avg_attempts"] = total_attempts / model_results["summary"]["successful"]
        model_results["summary"]["avg_latency_seconds"] = total_latency / len(test_cases)
        model_results["summary"]["first_try_success_rate"] = (
            first_try_successes / len(test_cases) * 100 if test_cases else 0
        )
        
        results["results_by_model"][model] = model_results
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"Summary for {model}:")
        print(f"  Successful: {model_results['summary']['successful']}/{model_results['summary']['total_cases']}")
        print(f"  First-try success rate: {model_results['summary']['first_try_success_rate']:.1f}%")
        print(f"  Avg attempts: {model_results['summary']['avg_attempts']:.2f}")
        print(f"  Avg latency: {model_results['summary']['avg_latency_seconds']:.2f}s")
    
    # Save results
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        results_file = output_path / f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.write_text(json.dumps(results, indent=2, default=str))
        print(f"\n✓ Results saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Ollama models on employee ticket extraction")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["llama2-7b-chat"],
        help="Ollama models to benchmark (default: llama2-7b-chat)"
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
        help="Directory to save results (default: benchmark/results)"
    )
    parser.add_argument(
        "--csv-path",
        type=str,
        help="Path to Historical_ticket_data.csv (optional, uses default if not provided)"
    )
    parser.add_argument(
        "--conversations-dir",
        type=str,
        help="Path to Conversation folder (optional, uses default if not provided)"
    )
    
    args = parser.parse_args()
    
    # Load test data
    print("Loading test data...")
    test_cases = load_benchmark_dataset(
        csv_path=args.csv_path,
        conversations_dir=args.conversations_dir,
        use_default=(not args.csv_path and not args.conversations_dir)
    )
    print(f"✓ Loaded {len(test_cases)} test cases")
    
    # Run benchmark
    results = run_benchmark(
        models=args.models,
        test_cases=test_cases,
        max_retries=args.max_retries,
        output_dir=args.output_dir,
    )
