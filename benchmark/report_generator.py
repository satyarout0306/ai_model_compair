"""Generate detailed comparison reports from benchmark results."""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import statistics


class ComparisonReportGenerator:
    """Generate comparison reports from benchmark results."""
    
    def __init__(self, results_json_path: str):
        """Load benchmark results from JSON file."""
        self.results_path = Path(results_json_path)
        with open(self.results_path) as f:
            self.results = json.load(f)
        self.models = self.results.get("models", [])
    
    def generate_summary_table(self) -> str:
        """Generate a summary comparison table."""
        report = "\n" + "="*100 + "\n"
        report += "BENCHMARK COMPARISON SUMMARY\n"
        report += "="*100 + "\n\n"
        
        # Collect metrics by model
        metrics = {}
        for model in self.models:
            model_data = self.results["results"].get(model, {})
            difficulties = model_data.get("difficulties", {})
            
            # Aggregate across all difficulties
            total_cases = 0
            total_successful = 0
            total_correct = 0
            total_attempts = 0
            total_latency = 0.0
            first_try_total = 0
            
            difficulty_count = 0
            for diff_key, diff_data in difficulties.items():
                summary = diff_data.get("summary", {})
                total_cases += summary.get("total", 0)
                total_successful += summary.get("successful", 0)
                total_correct += summary.get("correct", 0)
                avg_attempts = summary.get("avg_attempts", 0)
                avg_latency = summary.get("avg_latency", 0.0)
                first_try = int(summary.get("first_try_rate", 0) / 100 * summary.get("total", 0))
                
                if summary.get("successful", 0) > 0:
                    total_attempts += avg_attempts * summary.get("successful", 0)
                total_latency += avg_latency * summary.get("total", 0)
                first_try_total += first_try
                difficulty_count += 1
            
            # Calculate aggregates
            overall_accuracy = (total_correct / total_cases * 100) if total_cases > 0 else 0
            overall_success = (total_successful / total_cases * 100) if total_cases > 0 else 0
            overall_first_try = (first_try_total / total_cases * 100) if total_cases > 0 else 0
            avg_attempts_overall = total_attempts / total_successful if total_successful > 0 else 0
            avg_latency_overall = total_latency / total_cases if total_cases > 0 else 0
            
            metrics[model] = {
                "accuracy": overall_accuracy,
                "success_rate": overall_success,
                "first_try_rate": overall_first_try,
                "avg_attempts": avg_attempts_overall,
                "avg_latency": avg_latency_overall,
                "cases": total_cases,
            }
        
        # Print table header
        report += f"{'Model':<20} {'Accuracy':<12} {'Success':<12} {'1st Try':<12} {'Avg Attempts':<15} {'Latency (s)':<12}\n"
        report += "-" * 100 + "\n"
        
        # Sort by accuracy
        sorted_models = sorted(metrics.items(), key=lambda x: x[1]["accuracy"], reverse=True)
        
        for idx, (model, metric) in enumerate(sorted_models, 1):
            rank = f"#{idx}"
            report += f"{model:<20} {metric['accuracy']:<11.1f}% {metric['success_rate']:<11.1f}% {metric['first_try_rate']:<11.1f}% {metric['avg_attempts']:<14.2f} {metric['avg_latency']:<11.2f}\n"
        
        report += "-" * 100 + "\n\n"
        return report, metrics
    
    def generate_per_difficulty_report(self) -> str:
        """Generate detailed per-difficulty analysis."""
        report = "\n" + "="*100 + "\n"
        report += "PERFORMANCE BY DIFFICULTY LEVEL\n"
        report += "="*100 + "\n"
        
        difficulties = ["simple", "medium", "hard"]
        
        for difficulty in difficulties:
            report += f"\n{'─'*100}\n"
            report += f"DIFFICULTY: {difficulty.upper()}\n"
            report += f"{'─'*100}\n\n"
            
            # Collect metrics for this difficulty
            diff_metrics = {}
            for model in self.models:
                model_data = self.results["results"].get(model, {})
                diff_data = model_data.get("difficulties", {}).get(difficulty, {})
                summary = diff_data.get("summary", {})
                
                diff_metrics[model] = {
                    "accuracy": summary.get("accuracy", 0),
                    "success": summary.get("successful", 0),
                    "correct": summary.get("correct", 0),
                    "total": summary.get("total", 0),
                    "first_try": summary.get("first_try_rate", 0),
                    "avg_attempts": summary.get("avg_attempts", 0),
                    "avg_latency": summary.get("avg_latency", 0),
                }
            
            # Print table for this difficulty
            report += f"{'Model':<20} {'Accuracy':<12} {'Correct':<12} {'1st Try':<12} {'Avg Attempts':<15} {'Latency':<12}\n"
            report += "-" * 100 + "\n"
            
            sorted_models = sorted(diff_metrics.items(), key=lambda x: x[1]["accuracy"], reverse=True)
            for model, metric in sorted_models:
                correct_str = f"{metric['correct']}/{metric['total']}"
                report += f"{model:<20} {metric['accuracy']:<11.1f}% {correct_str:<12} {metric['first_try']:<11.1f}% {metric['avg_attempts']:<14.2f} {metric['avg_latency']:<11.2f}\n"
            
            report += "\n"
        
        return report
    
    def generate_model_profiles(self) -> str:
        """Generate detailed profile for each model."""
        report = "\n" + "="*100 + "\n"
        report += "DETAILED MODEL PROFILES\n"
        report += "="*100 + "\n"
        
        for model in self.models:
            report += f"\n{'─'*100}\n"
            report += f"MODEL: {model}\n"
            report += f"{'─'*100}\n\n"
            
            model_data = self.results["results"].get(model, {})
            difficulties = model_data.get("difficulties", {})
            
            report += "Performance by Difficulty:\n"
            report += f"{'Difficulty':<15} {'Accuracy':<12} {'Success':<12} {'Avg Latency':<12}\n"
            report += "-" * 60 + "\n"
            
            for diff_key, diff_data in difficulties.items():
                summary = diff_data.get("summary", {})
                report += f"{diff_key:<15} {summary.get('accuracy', 0):<11.1f}% {summary.get('successful', 0)}/{summary.get('total', 0):<10} {summary.get('avg_latency', 0):<11.2f}\n"
            
            # Calculate trend
            diff_keys = ["simple", "medium", "hard"]
            accuracies = []
            for diff_key in diff_keys:
                if diff_key in difficulties:
                    acc = difficulties[diff_key].get("summary", {}).get("accuracy", 0)
                    accuracies.append(acc)
            
            if len(accuracies) >= 2:
                trend = "↑" if accuracies[-1] > accuracies[0] else "↓" if accuracies[-1] < accuracies[0] else "→"
                change = accuracies[-1] - accuracies[0]
                report += f"\nTrend (Simple→Hard): {trend} ({change:+.1f}%)\n"
            
            report += "\n"
        
        return report
    
    def generate_rankings(self, metrics: Dict) -> str:
        """Generate model rankings by different criteria."""
        report = "\n" + "="*100 + "\n"
        report += "MODEL RANKINGS\n"
        report += "="*100 + "\n\n"
        
        # Rank by accuracy
        report += "🥇 OVERALL ACCURACY RANKING:\n"
        report += "-" * 60 + "\n"
        sorted_by_accuracy = sorted(metrics.items(), key=lambda x: x[1]["accuracy"], reverse=True)
        for idx, (model, metric) in enumerate(sorted_by_accuracy, 1):
            medals = ["🥇", "🥈", "🥉"]
            medal = medals[idx-1] if idx <= 3 else "  "
            report += f"{medal} {idx}. {model:<25} {metric['accuracy']:.1f}%\n"
        
        # Rank by speed (latency)
        report += "\n⚡ SPEED RANKING (Lowest Latency):\n"
        report += "-" * 60 + "\n"
        sorted_by_latency = sorted(metrics.items(), key=lambda x: x[1]["avg_latency"])
        for idx, (model, metric) in enumerate(sorted_by_latency, 1):
            medals = ["🥇", "🥈", "🥉"]
            medal = medals[idx-1] if idx <= 3 else "  "
            report += f"{medal} {idx}. {model:<25} {metric['avg_latency']:.2f}s\n"
        
        # Rank by reliability (first try rate)
        report += "\n🎯 RELIABILITY RANKING (1st Try Success):\n"
        report += "-" * 60 + "\n"
        sorted_by_first_try = sorted(metrics.items(), key=lambda x: x[1]["first_try_rate"], reverse=True)
        for idx, (model, metric) in enumerate(sorted_by_first_try, 1):
            medals = ["🥇", "🥈", "🥉"]
            medal = medals[idx-1] if idx <= 3 else "  "
            report += f"{medal} {idx}. {model:<25} {metric['first_try_rate']:.1f}%\n"
        
        report += "\n"
        return report
    
    def generate_full_report(self, output_file: str = None) -> str:
        """Generate complete comparison report."""
        report = "\n\n"
        report += "╔" + "═"*98 + "╗\n"
        report += "║" + " "*30 + "MODEL COMPARISON REPORT" + " "*45 + "║\n"
        report += "╚" + "═"*98 + "╝\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Results File: {self.results_path}\n"
        
        # Add summary table
        summary, metrics = self.generate_summary_table()
        report += summary
        
        # Add rankings
        report += self.generate_rankings(metrics)
        
        # Add per-difficulty analysis
        report += self.generate_per_difficulty_report()
        
        # Add detailed profiles
        report += self.generate_model_profiles()
        
        # Add footer
        report += "\n" + "="*100 + "\n"
        report += "END OF REPORT\n"
        report += "="*100 + "\n\n"
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
            print(f"✓ Report saved to: {output_path}\n")
        
        return report


def generate_comparison_report(results_json_path: str, output_file: str = None):
    """Convenient function to generate report from results JSON."""
    generator = ComparisonReportGenerator(results_json_path)
    report = generator.generate_full_report(output_file)
    print(report)
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <results_json_path> [output_file]")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_comparison_report(results_file, output_file)
