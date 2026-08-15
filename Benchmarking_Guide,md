# Model Comparison Benchmarking Guide

Complete benchmarking framework for comparing Ollama models on structured JSON extraction from employee ticket conversations.

## 📋 Overview

This framework allows you to:
- ✅ Benchmark multiple LLM models simultaneously
- ✅ Test across 3 difficulty levels (Simple, Medium, Hard)
- ✅ Extract tickets from real conversation data
- ✅ Generate detailed comparison reports
- ✅ Analyze performance across accuracy, speed, reliability metrics

## 🚀 Quick Start

### 1. Ensure Ollama Models are Downloaded

```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama pull phi3:mini
```

### 2. Run Full Pipeline (Recommended)

```bash
cd /Users/satyarout/Documents/My_Code/AI_projects/Model_Compair/ai_model_compair

python3 benchmark_cli.py full \
  --models llama3.2:3b qwen2.5:7b phi3:mini \
  --output benchmark/results \
  --max-retries 3
```

This will:
1. Run benchmarks across all 3 models
2. Test each model on 3 difficulty levels
3. Generate a detailed comparison report
4. Save all results as JSON

## 📊 Commands

### Run Benchmarks Only

```bash
python3 benchmark_cli.py run \
  --models llama3.2:3b qwen2.5:7b phi3:mini \
  --output benchmark/results \
  --max-retries 3
```

**Options:**
- `--models`: Space-separated model names (default: llama3.2:3b qwen2.5:7b phi3:mini)
- `--output`: Results directory (default: benchmark/results)
- `--max-retries`: Retry attempts per test case (default: 3)
- `--csv-path`: Custom CSV path (optional)
- `--conversations-dir`: Custom conversations path (optional)

### Generate Report from Results

```bash
python3 benchmark_cli.py report benchmark/results/benchmark_results_*.json \
  --output benchmark/results/comparison_report.txt
```

## 📈 Task Difficulty Levels

### SIMPLE ⭐
Extract basic ticket information:
- Ticket ID
- Priority Level
- Resolution Status

**Use case:** Quick validation, basic parsing ability

### MEDIUM ⭐⭐
Extract structured metadata + solution:
- Ticket ID
- Issue Category
- Priority
- Resolution Status
- Solution Description

**Use case:** Comprehension of structured data

### HARD ⭐⭐⭐
Full extraction with sentiment analysis:
- All metadata fields
- Customer Sentiment (from conversation)
- Key conversation points
- Complex field extraction

**Use case:** NLU, context understanding, real-world scenarios

## 📊 Metrics

For each model and difficulty level, the report includes:

| Metric | Description |
|--------|-------------|
| **Accuracy** | % of extractions matching ground truth |
| **Success Rate** | % of valid JSON outputs |
| **1st Try Rate** | % correct on first attempt (no retries) |
| **Avg Attempts** | Average retries needed for success |
| **Latency** | Processing time per ticket (seconds) |

## 📁 Output Files

After running benchmarks, you'll get:

```
benchmark/results/
├── benchmark_results_20260813_142530.json       # Raw results
└── comparison_report_20260813_142530.txt        # Human-readable report
```

### Report Contents

1. **Summary Comparison Table** - Overall metrics for all models
2. **Model Rankings** - Ranked by:
   - Accuracy 🥇
   - Speed (Latency) ⚡
   - Reliability (1st Try) 🎯
3. **Per-Difficulty Analysis** - Breakdown by task complexity
4. **Detailed Model Profiles** - Individual model performance trends

## 🔧 Advanced Usage

### Custom Test Data

```bash
python3 benchmark_cli.py run \
  --models llama3.2:3b qwen2.5:7b \
  --csv-path /path/to/your/tickets.csv \
  --conversations-dir /path/to/conversations
```

### Different Model List

```bash
python3 benchmark_cli.py full \
  --models mistral:7b llama2:13b neural-chat
```

### Increase Reliability Testing

```bash
python3 benchmark_cli.py full \
  --models llama3.2:3b qwen2.5:7b phi3:mini \
  --max-retries 5  # More retries for tougher cases
```

## 📝 Data Format

### CSV Structure
```
Ticket ID, Issue Category, Sentiment, Priority, Solution, Resolution Status, Date of Resolution
TECH_001, Software Installation Failure, Frustrated, High, Disable antivirus and retry, Resolved, 2025-03-17
```

### Conversation Files
Located in: `test_data/employee_ticket/Conversation/Conversation/`

Natural language dialogue between customer and agent for each issue category.

## 📊 Example Report Section

```
========================================
BENCHMARK COMPARISON SUMMARY
========================================

Model                Accuracy       Success         1st Try         Avg Attempts    Latency (s)
────────────────────────────────────────────────────────────────────────────────────────────
qwen2.5:7b           87.5%          93.8%           75.0%           1.23            0.85
llama3.2:3b          81.3%          87.5%           68.8%           1.38            0.92
phi3:mini            75.0%          81.3%           56.3%           1.65            0.71

🥇 OVERALL ACCURACY RANKING:
🥇 1. qwen2.5:7b               87.5%
🥈 2. llama3.2:3b             81.3%
🥉 3. phi3:mini               75.0%

⚡ SPEED RANKING (Lowest Latency):
🥇 1. phi3:mini               0.71s
🥈 2. qwen2.5:7b              0.85s
🥉 3. llama3.2:3b             0.92s
```

## 🐛 Troubleshooting

### Models Not Found
```bash
# Check if Ollama is running
ollama list

# Pull missing models
ollama pull llama3.2:3b
```

### Import Errors
```bash
# Ensure you're in the right directory
cd /Users/satyarout/Documents/My_Code/AI_projects/Model_Compair/ai_model_compair

# Use full Python path
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 benchmark_cli.py run
```

### JSON Parsing Errors
Check that your CSV file is properly formatted and conversations are accessible.

## 📚 File Structure

```
ai_model_compair/
├── benchmark/
│   ├── load_data.py              # Data loader for CSV/conversations
│   ├── tasks.py                  # Task difficulty definitions + input/ground truth functions
│   ├── run_tasks.py              # Multi-difficulty benchmark runner
│   ├── report_generator.py       # Report generation
│   ├── visualizer.py             # Matplotlib visualization graphs
│   ├── benchmark_cli.py          # Main CLI entry point (run/report/visualize/full)
│   └── results/                  # Output directory (JSON, reports, PNG files)
├── core/
│   ├── generator.py              # Core generate→validate→retry loop
│   └── prompts.py                # Prompt templates (schema injection)
├── schemas/
│   ├── __init__.py               # Base schemas (EmployeeTicket, Person, Invoice, Ticket)
│   ├── simple.py                 # SimpleTicketInfo schema (⭐ Easy)
│   ├── medium.py                 # MediumTicketAnalysis schema (⭐⭐ Medium)
│   └── hard.py                   # HardTicketExtraction schema (⭐⭐⭐ Hard)
├── tests/
│   └── test_models.py            # Model benchmark tests + MultiModelComparison
├── test_data/
│   └── employee_ticket/
│       ├── Historical_ticket_data.csv  # 16 test cases with ground truth
│       └── Conversation/Conversation/  # Conversation files by category
├── README.md                     # Project overview
├── QUICK_START.md                # Quick reference guide
├── BENCHMARKING_GUIDE.md         # This file (detailed documentation)
├── requirement.txt               # Python dependencies
└── benchmark_cli.py              # Unified CLI interface
```

### Schema Organization

Schemas are organized by difficulty level:

- **`schemas/simple.py`** → `SimpleTicketInfo`
  - Fields: ticket_id, priority, resolution_status
  - Difficulty: ⭐ (Easy)
  
- **`schemas/medium.py`** → `MediumTicketAnalysis`
  - Fields: ticket_id, issue_category, priority, resolution_status, solution
  - Difficulty: ⭐⭐ (Medium)
  
- **`schemas/hard.py`** → `HardTicketExtraction`
  - Fields: All above + sentiment, key_points, date_of_resolution
  - Difficulty: ⭐⭐⭐ (Hard - NLU Intensive)

These schemas are imported by `benchmark/tasks.py` and paired with input formatting and ground truth extraction functions.

## 🎯 Typical Workflow

1. **Prepare Data**
   - Ensure CSV and conversations are in `test_data/employee_ticket/`

2. **Run Benchmarks**
   ```bash
   python3 benchmark_cli.py full --models llama3.2:3b qwen2.5:7b phi3:mini
   ```

3. **Review Report**
   - Open `benchmark/results/comparison_report_*.txt`
   - Compare metrics across models

4. **Iterate**
   - Adjust models based on performance
   - Fine-tune prompts if needed
   - Re-run benchmarks to compare

## 📞 Support

For issues or questions, check:
- Terminal output for specific errors
- JSON results file for raw data
- Report file for formatted analysis

---

**Version:** 1.0  
**Last Updated:** 2026-08-13
