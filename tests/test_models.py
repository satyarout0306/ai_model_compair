import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

import ollama
from ollama._types import ResponseError

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.generator import generate_structured
from benchmark.load_data import load_benchmark_dataset
from benchmark.tasks import TaskDifficulty, get_task_by_difficulty


class ModelBenchmarkTest:
    """Run and collect benchmark results for a single model."""
    
    def __init__(self, model_name: str, max_retries: int = 3):
        self.model_name = model_name
        self.max_retries = max_retries
        self.results = {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "difficulties": {}
        }
    
    def run_task(self, difficulty: TaskDifficulty, test_cases: List[dict]) -> Dict:
        """Run a single difficulty task and return results."""
        task = get_task_by_difficulty(difficulty)
        if not task:
            raise ValueError(f"Unknown task difficulty: {difficulty}")
        
        print(f"\n  Testing {self.model_name} on {difficulty.value.upper()} task...")
        
        task_results = {
            "difficulty": difficulty.value,
            "test_cases": [],
            "summary": {
                "total": len(test_cases),
                "successful": 0,
                "failed": 0,
                "correct": 0,
                "accuracy": 0.0,
                "first_try_rate": 0.0,
                "avg_attempts": 0.0,
                "avg_latency": 0.0,
            }
        }
        
        total_attempts = 0
        total_latency = 0.0
        first_try_count = 0
        correct_count = 0
        
        for idx, case in enumerate(test_cases, 1):
            # Prepare task inputs
            input_text = task["input_fn"](case["ground_truth"])
            ground_truth = task["ground_truth_fn"](case["ground_truth"])
            
            # Generate and validate
            result = generate_structured(
                model=self.model_name,
                user_input=input_text,
                schema=task["schema"],
                max_retries=self.max_retries,
            )
            
            # Check correctness
            is_correct = False
            if result.success and result.parsed:
                try:
                    parsed_dict = result.parsed.model_dump()
                    # Check critical fields
                    critical_fields = ["ticket_id", "priority", "resolution_status"]
                    is_correct = all(
                        parsed_dict.get(field) == ground_truth.get(field)
                        for field in critical_fields
                        if field in ground_truth
                    )
                except:
                    is_correct = False
            
            # Record result
            case_result = {
                "case": idx,
                "ticket_id": case["ground_truth"].get("ticket_id", ""),
                "success": result.success,
                "correct": is_correct,
                "attempts": result.attempts,
                "latency": result.latency_seconds,
            }
            task_results["test_cases"].append(case_result)
            
            # Update counters
            if result.success:
                task_results["summary"]["successful"] += 1
                if result.attempts == 1:
                    first_try_count += 1
                if is_correct:
                    correct_count += 1
            else:
                task_results["summary"]["failed"] += 1
            
            total_attempts += result.attempts
            total_latency += result.latency_seconds
            
            # Progress indicator
            status = "✓" if result.success else "✗"
            print(f"    [{idx}/{len(test_cases)}] {status}", end="", flush=True)
        
        # Calculate summary statistics
        total = len(test_cases)
        task_results["summary"]["correct"] = correct_count
        task_results["summary"]["accuracy"] = (correct_count / total * 100) if total > 0 else 0
        task_results["summary"]["first_try_rate"] = (first_try_count / total * 100) if total > 0 else 0
        
        if task_results["summary"]["successful"] > 0:
            task_results["summary"]["avg_attempts"] = total_attempts / task_results["summary"]["successful"]
        
        task_results["summary"]["avg_latency"] = total_latency / total if total > 0 else 0
        
        print()  # New line after progress
        self.results["difficulties"][difficulty.value] = task_results
        return task_results


class MultiModelComparison:
    """Run benchmarks for multiple models and generate comparison report."""
    
    def __init__(self, models: List[str], max_retries: int = 3):
        self.models = models
        self.max_retries = max_retries
        self.all_results = {
            "timestamp": datetime.now().isoformat(),
            "models": models,
            "results": {}
        }
    
    def run_all_models(self, test_cases: List[dict], difficulties: List[TaskDifficulty] = None):
        """Run benchmarks for all models across all difficulties."""
        if difficulties is None:
            difficulties = list(TaskDifficulty)
        
        print(f"\n{'='*70}")
        print(f"Running Benchmarks for {len(self.models)} Models")
        print(f"Models: {', '.join(self.models)}")
        print(f"Test Cases: {len(test_cases)}")
        print(f"Difficulties: {', '.join([d.value.upper() for d in difficulties])}")
        print(f"{'='*70}")
        
        for model in self.models:
            print(f"\n{'─'*70}")
            print(f"Model: {model}")
            print(f"{'─'*70}")
            
            tester = ModelBenchmarkTest(model, self.max_retries)
            
            for difficulty in difficulties:
                tester.run_task(difficulty, test_cases)
            
            self.all_results["results"][model] = tester.results
        
        return self.all_results
    
    def save_results(self, output_dir: str):
        """Save raw results to JSON."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results_file = output_path / f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.write_text(json.dumps(self.all_results, indent=2, default=str))
        
        print(f"\n✓ Results saved to: {results_file}")
        return results_file


def run_model_comparison_test(
    models: List[str] = None,
    csv_path: str = None,
    conversations_dir: str = None,
    output_dir: str = "benchmark/results",
    max_retries: int = 3,
):
    """Main test runner for model comparison."""
    if models is None:
        models = ["llama3.2:3b", "qwen2.5:7b", "phi3:mini"]
    
    # Check if Ollama is running and models are available
    print("\n" + "="*70)
    print("🔍 Checking Ollama Status and Models...")
    print("="*70)
    
    try:
        available_models = ollama.list()
        available_names = [m.model for m in available_models.models] if hasattr(available_models, 'models') else []
        
        print(f"✓ Ollama is running")
        print(f"✓ Available models: {', '.join(available_names) if available_names else 'None'}")
        
        missing_models = [m for m in models if m not in available_names]
        if missing_models:
            print(f"\n❌ Missing models: {', '.join(missing_models)}")
            print(f"\n💡 To fix this, run:")
            for model in missing_models:
                print(f"   ollama pull {model}")
            print(f"\n   Then verify with: ollama list")
            raise RuntimeError(f"Required models not found: {missing_models}")
    
    except ResponseError as e:
        print(f"❌ Cannot connect to Ollama!")
        print(f"\n💡 Start Ollama with: ollama serve")
        print(f"   (in a separate terminal)\n")
        raise ResponseError(
            f"Ollama connection failed. Make sure Ollama is running.\nOriginal error: {e}",
            500
        ) from e
    except Exception as e:
        if "ConnectionRefusedError" in str(type(e)):
            print(f"❌ Cannot connect to Ollama!")
            print(f"\n💡 Start Ollama with: ollama serve")
            raise RuntimeError("Ollama is not running. Start it with 'ollama serve' in another terminal.") from e
        raise
    
    # Load test data
    print("\n" + "="*70)
    print("📦 Loading Test Data...")
    print("="*70)
    test_cases = load_benchmark_dataset(
        csv_path=csv_path,
        conversations_dir=conversations_dir,
        use_default=True
    )
    print(f"✓ Loaded {len(test_cases)} test cases\n")
    
    # Run comparison
    try:
        comparison = MultiModelComparison(models, max_retries)
        comparison.run_all_models(test_cases)
        comparison.save_results(output_dir)
        return comparison
    except ResponseError as e:
        print(f"\n❌ Benchmark failed: {e}")
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    # Run default comparison test
    comparison = run_model_comparison_test()
