"""Generate visualization graphs for benchmark comparison reports using matplotlib."""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List
import numpy as np


class MetricsCalculator:
    """Calculate additional metrics like F1 score from benchmark results."""
    
    @staticmethod
    def calculate_f1_score(precision: float, recall: float) -> float:
        """Calculate F1 score from precision and recall."""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def calculate_model_metrics(model_data: Dict) -> Dict:
        """Calculate comprehensive metrics for a model."""
        difficulties = model_data.get("difficulties", {})
        
        total_correct = 0
        total_cases = 0
        total_latency = 0.0
        total_attempts = 0
        
        metrics = {
            "by_difficulty": {},
            "overall": {}
        }
        
        # Calculate per-difficulty metrics
        for diff_key, diff_data in difficulties.items():
            summary = diff_data.get("summary", {})
            total = summary.get("total", 1)
            successful = summary.get("successful", 0)
            correct = summary.get("correct", 0)
            
            # Precision: correct / successful
            precision = (correct / successful) if successful > 0 else 0
            # Recall: correct / total
            recall = correct / total if total > 0 else 0
            # F1 score
            f1 = MetricsCalculator.calculate_f1_score(precision, recall)
            
            metrics["by_difficulty"][diff_key] = {
                "accuracy": summary.get("accuracy", 0),
                "precision": precision * 100,
                "recall": recall * 100,
                "f1_score": f1 * 100,
                "latency": summary.get("avg_latency", 0),
                "first_try": summary.get("first_try_rate", 0),
                "success_rate": (successful / total * 100) if total > 0 else 0,
            }
            
            total_correct += correct
            total_cases += total
            total_latency += summary.get("avg_latency", 0) * total
            total_attempts += summary.get("avg_attempts", 0) * successful
        
        # Calculate overall metrics
        overall_recall = (total_correct / total_cases * 100) if total_cases > 0 else 0
        overall_precision = overall_recall  # Simplified: assuming similar distribution
        overall_f1 = MetricsCalculator.calculate_f1_score(
            overall_precision / 100, overall_recall / 100
        ) * 100
        
        metrics["overall"] = {
            "accuracy": overall_recall,
            "f1_score": overall_f1,
            "avg_latency": total_latency / total_cases if total_cases > 0 else 0,
            "total_cases": total_cases,
        }
        
        return metrics


class BenchmarkVisualizer:
    """Generate visualization graphs for benchmark comparison."""
    
    def __init__(self, results_json_path: str, output_dir: str = "benchmark/results"):
        """Initialize visualizer with results data."""
        with open(results_json_path) as f:
            self.results = json.load(f)
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.models = self.results.get("models", [])
        
        # Calculate metrics
        self.metrics = {}
        for model in self.models:
            model_data = self.results["results"].get(model, {})
            self.metrics[model] = MetricsCalculator.calculate_model_metrics(model_data)
        
        # Set style
        plt.style.use("seaborn-v0_8-darkgrid")
        self.colors = plt.cm.Set3(np.linspace(0, 1, len(self.models)))
    
    def plot_accuracy_comparison(self):
        """Plot overall accuracy comparison across models."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        models = list(self.metrics.keys())
        accuracies = [self.metrics[m]["overall"]["accuracy"] for m in models]
        
        bars = ax.bar(models, accuracies, color=self.colors, edgecolor="black", linewidth=1.5)
        
        # Add value labels on bars
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{acc:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel("Accuracy (%)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Model", fontsize=12, fontweight='bold')
        ax.set_title("Overall Accuracy Comparison", fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "01_accuracy_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
    
    def plot_f1_score_comparison(self):
        """Plot F1 scores across models."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        models = list(self.metrics.keys())
        f1_scores = [self.metrics[m]["overall"]["f1_score"] for m in models]
        
        bars = ax.bar(models, f1_scores, color=self.colors, edgecolor="black", linewidth=1.5)
        
        # Add value labels
        for bar, f1 in zip(bars, f1_scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{f1:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel("F1 Score (%)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Model", fontsize=12, fontweight='bold')
        ax.set_title("F1 Score Comparison", fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "02_f1_score_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
    
    def plot_difficulty_performance(self):
        """Plot performance across difficulty levels for each model."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        difficulties = ["simple", "medium", "hard"]
        x = np.arange(len(difficulties))
        width = 0.25
        
        for idx, model in enumerate(self.models):
            accuracies = []
            for diff in difficulties:
                acc = self.metrics[model]["by_difficulty"].get(diff, {}).get("accuracy", 0)
                accuracies.append(acc)
            
            offset = (idx - len(self.models)/2 + 0.5) * width
            ax.bar(x + offset, accuracies, width, label=model, color=self.colors[idx], edgecolor="black")
        
        ax.set_ylabel("Accuracy (%)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Difficulty Level", fontsize=12, fontweight='bold')
        ax.set_title("Performance by Difficulty Level", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(difficulties)
        ax.legend()
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "03_difficulty_performance.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
    
    def plot_latency_comparison(self):
        """Plot average latency across models."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        models = list(self.metrics.keys())
        latencies = [self.metrics[m]["overall"]["avg_latency"] for m in models]
        
        bars = ax.bar(models, latencies, color=self.colors, edgecolor="black", linewidth=1.5)
        
        # Add value labels
        for bar, lat in zip(bars, latencies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{lat:.2f}s', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylabel("Latency (seconds)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Model", fontsize=12, fontweight='bold')
        ax.set_title("Average Latency Comparison", fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "04_latency_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
    
    def plot_first_try_success_rate(self):
        """Plot first-try success rates across models and difficulties."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        difficulties = ["simple", "medium", "hard"]
        x = np.arange(len(difficulties))
        width = 0.25
        
        for idx, model in enumerate(self.models):
            first_try_rates = []
            for diff in difficulties:
                rate = self.metrics[model]["by_difficulty"].get(diff, {}).get("first_try", 0)
                first_try_rates.append(rate)
            
            offset = (idx - len(self.models)/2 + 0.5) * width
            ax.bar(x + offset, first_try_rates, width, label=model, color=self.colors[idx], edgecolor="black")
        
        ax.set_ylabel("Success Rate (%)", fontsize=12, fontweight='bold')
        ax.set_xlabel("Difficulty Level", fontsize=12, fontweight='bold')
        ax.set_title("First-Try Success Rate by Difficulty", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(difficulties)
        ax.legend()
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "05_first_try_success_rate.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
    
    def plot_metrics_heatmap(self):
        """Plot heatmap of all key metrics."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Collect metrics
        metric_names = ["Accuracy", "F1 Score", "Latency (s)", "1st Try (%)"]
        matrix = []
        
        for model in self.models:
            metrics = self.metrics[model]["overall"]
            row = [
                metrics["accuracy"],
                metrics["f1_score"],
                metrics["avg_latency"] * 10,  # Scale for visibility
                # First-try rate from simple difficulty
                self.metrics[model]["by_difficulty"].get("simple", {}).get("first_try", 0)
            ]
            matrix.append(row)
        
        matrix = np.array(matrix)
        
        # Normalize for heatmap
        matrix_normalized = matrix.copy()
        for i in range(matrix_normalized.shape[1]):
            col = matrix_normalized[:, i]
            if col.max() > 0:
                matrix_normalized[:, i] = (col / col.max()) * 100
        
        im = ax.imshow(matrix_normalized, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        
        ax.set_xticks(np.arange(len(metric_names)))
        ax.set_yticks(np.arange(len(self.models)))
        ax.set_xticklabels(metric_names)
        ax.set_yticklabels(self.models)
        
        # Rotate labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add text annotations
        for i in range(len(self.models)):
            for j in range(len(metric_names)):
                value = matrix[i, j]
                text = ax.text(j, i, f'{value:.1f}', ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_title("Performance Metrics Heatmap", fontsize=14, fontweight='bold')
        fig.colorbar(im, ax=ax, label="Normalized Score (%)")
        
        plt.tight_layout()
        output_file = self.output_dir / "06_metrics_heatmap.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
    
    def plot_overall_comparison_radar(self):
        """Plot radar chart comparing all models across key metrics."""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        categories = ['Accuracy', 'F1 Score', 'Speed\n(inverse)', 'Reliability']
        N = len(categories)
        
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        for idx, model in enumerate(self.models):
            metrics = self.metrics[model]["overall"]
            # Prepare values (normalize latency as inverse for "speed")
            values = [
                metrics["accuracy"],
                metrics["f1_score"],
                100 - min(metrics["avg_latency"] * 20, 100),  # Speed (inverse of latency)
                self.metrics[model]["by_difficulty"].get("simple", {}).get("first_try", 0)
            ]
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=model, color=self.colors[idx])
            ax.fill(angles, values, alpha=0.15, color=self.colors[idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=10)
        ax.set_ylim(0, 100)
        ax.set_title("Overall Model Comparison (Radar)", fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.grid(True)
        
        plt.tight_layout()
        output_file = self.output_dir / "07_radar_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved: {output_file}")
    
    def generate_all_plots(self):
        """Generate all visualization plots."""
        print("\n" + "="*70)
        print("📊 GENERATING VISUALIZATION GRAPHS")
        print("="*70 + "\n")
        
        try:
            self.plot_accuracy_comparison()
            self.plot_f1_score_comparison()
            self.plot_difficulty_performance()
            self.plot_latency_comparison()
            self.plot_first_try_success_rate()
            self.plot_metrics_heatmap()
            self.plot_overall_comparison_radar()
            
            print("\n" + "="*70)
            print(f"✅ All visualizations saved to: {self.output_dir}")
            print("="*70 + "\n")
            
            return True
        except Exception as e:
            print(f"\n❌ Error generating plots: {e}\n")
            import traceback
            traceback.print_exc()
            return False


def generate_visualizations(results_json_path: str, output_dir: str = None):
    """Convenient function to generate all visualizations."""
    if not Path(results_json_path).exists():
        print(f"❌ Results file not found: {results_json_path}")
        return False
    
    if output_dir is None:
        output_dir = Path(results_json_path).parent
    
    visualizer = BenchmarkVisualizer(results_json_path, output_dir)
    return visualizer.generate_all_plots()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python visualizer.py <results_json_path> [output_dir]")
        sys.exit(1)
    
    results_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = generate_visualizations(results_file, output_dir)
    sys.exit(0 if success else 1)
