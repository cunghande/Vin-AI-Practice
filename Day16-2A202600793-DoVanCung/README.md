# Lab 16 - Reflexion Agent

This project implements and evaluates a ReAct baseline and a Reflexion agent on
multi-hop HotpotQA-style question answering.

The final submitted run uses a real OpenAI LLM runtime with `gpt-5.4-nano` on
150 converted HotpotQA examples.

## What Is Implemented

- Complete Pydantic schemas for dataset examples, judge results, reflection
  entries, run traces, and report payloads.
- ReAct agent with one answer attempt.
- Reflexion agent with evaluator feedback, reflection memory, and retry logic.
- Mock runtime for deterministic local testing and autograding.
- OpenAI runtime for real LLM calls through the Responses API.
- Real token and latency collection from LLM responses.
- Benchmark report generation in JSON, Markdown, and JSONL traces.
- HotpotQA converter for raw `hotpot_dev_distractor_v1` data.
- Basic local web UI for running benchmarks and viewing past reports.

## Main Files

| Path | Purpose |
|---|---|
| `src/reflexion_lab/agents.py` | ReAct and Reflexion loop |
| `src/reflexion_lab/runtimes.py` | Mock runtime and OpenAI LLM runtime |
| `src/reflexion_lab/schemas.py` | Pydantic data schemas |
| `src/reflexion_lab/prompts.py` | Actor, evaluator, and reflector prompts |
| `src/reflexion_lab/reporting.py` | Summary metrics and report generation |
| `scripts/convert_hotpot.py` | Converts raw HotpotQA to project format |
| `run_benchmark.py` | CLI benchmark runner |
| `ui_app.py` | Basic local UI |
| `autograde.py` | Provided autograder |
| `data/hotpot_data.json` | Final 150-example dataset |
| `data/hotpot_dev.json` | 100-example development split for prompt/runtime tuning |
| `data/hotpot_test.json` | 50-example held-out test split for final evaluation |
| `report.json` | Final report JSON copied to the project root for submission |
| `REPORT.md` | Final report Markdown copied to the project root for submission |
| `outputs/llm_hotpot_150/report.json` | Final submitted LLM report |
| `outputs/llm_hotpot_150/report.md` | Human-readable final report |

## Setup

```powershell
python -m pip install -r requirements.txt
```

The project can run without an API key in mock mode.

For LLM mode, the program can ask for the OpenAI API key in the terminal. The
key does not need to be stored in `.env`.

## Dataset

The full converted dataset is:

```text
data/hotpot_data.json
```

It contains 150 examples converted from:

```text
data/hotpot_dev_distractor_v1.json/hotpot_dev_distractor_v1.json
```

The converted schema matches `data/hotpot_mini.json`:

```json
{
  "qid": "example_id",
  "difficulty": "medium",
  "question": "Question text",
  "gold_answer": "Answer",
  "context": [
    {"title": "Article title", "text": "Article text"}
  ]
}
```

The source dev distractor file labels all examples as `hard`, so the submitted
`hotpot_data.json` uses a balanced, shuffled label distribution:

```text
easy: 50
medium: 50
hard: 50
```

For a cleaner experiment protocol, the full dataset is split into:

| Split | Count | Difficulty distribution | Purpose |
|---|---:|---|---|
| `data/hotpot_dev.json` | 100 | easy 33, medium 34, hard 33 | Tune prompts, attempts, and runtime behavior |
| `data/hotpot_test.json` | 50 | easy 17, medium 16, hard 17 | Held-out final evaluation |

The dev and test splits have no overlapping `qid` values.

To regenerate the dataset:

```powershell
python scripts\convert_hotpot.py --source data\hotpot_dev_distractor_v1.json\hotpot_dev_distractor_v1.json --output data\hotpot_data.json --limit 150 --difficulty-strategy balanced --seed 42
```

To regenerate the dev/test split:

```powershell
python scripts\split_hotpot.py --source data\hotpot_data.json --dev-output data\hotpot_dev.json --test-output data\hotpot_test.json --dev-size 100 --seed 42
```

## Run Benchmarks

Mock run:

```powershell
python run_benchmark.py --dataset data/hotpot_data.json --mode mock --out-dir outputs/mock_hotpot_150
```

Small LLM smoke test:

```powershell
python run_benchmark.py --dataset data/hotpot_data.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_smoke --limit 2 --key-prompt visible
```

Development run for prompt/runtime tuning:

```powershell
python run_benchmark.py --dataset data/hotpot_dev.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_dev --key-prompt visible
```

Held-out test run after tuning:

```powershell
python run_benchmark.py --dataset data/hotpot_test.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_test --key-prompt visible
```

Full-data LLM run, used for the current full-set report:

```powershell
python run_benchmark.py --dataset data/hotpot_data.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_hotpot_150 --key-prompt visible
```

Notes:

- `--key-prompt hidden` is safer because the API key is not displayed.
- `--key-prompt visible` is easier for pasting in some Windows terminals, but
  the key is visible on screen.
- The key is passed to the local process as an environment variable and is not
  written to project files.

## UI

Start the basic UI:

```powershell
python ui_app.py
```

Open:

```text
http://127.0.0.1:8765
```

The UI supports:

- selecting a dataset,
- running mock or LLM benchmark,
- entering API key for LLM mode,
- viewing EM, correctness, attempts, token usage, and latency,
- inspecting previous reports from `outputs/`.

## Final Result

Current full-set report path:

```text
report.json
```

The same report is also available at:

```text
outputs/llm_hotpot_150/report.json
```

If using the held-out test protocol, run the test command above and submit:

```text
outputs/llm_test/report.json
```

or copy it to the root submission path:

```powershell
Copy-Item outputs\llm_test\report.json report.json
Copy-Item outputs\llm_test\report.md REPORT.md
```

Experiment:

- Dataset: `hotpot_data.json`
- Number of questions: 150
- Total records: 300 because both ReAct and Reflexion are evaluated
- Mode: `llm:gpt-5.4-nano`

Summary:

| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| Correct | 116 / 150 | 149 / 150 | +33 |
| EM | 77.33% | 99.33% | +22.00 pp |
| Avg attempts | 1.0000 | 1.2267 | +0.2267 |
| Total tokens | 261,286 | 382,014 | +120,728 |
| Avg tokens | 1,741.91 | 2,546.76 | +804.85 |
| Total latency | 459,230 ms | 635,257 ms | +176,027 ms |
| Avg latency | 3,061.53 ms | 4,235.05 ms | +1,173.52 ms |

Interpretation:

Reflexion improved answer accuracy substantially: exact-match accuracy rose from
77.33% to 99.33%. The gain came from retrying failed first attempts with
reflection memory. This cost additional tokens and latency, but the average
attempt count only increased from 1.0 to 1.2267, meaning most questions still
finished on the first attempt while difficult examples benefited from feedback.

## Autograde

Run:

```powershell
python autograde.py --report-path outputs/llm_hotpot_150/report.json
```

or, using the root submission copy:

```powershell
python autograde.py --report-path report.json
```

Expected result after the final report update:

```text
Auto-grade total: 100/100
```

Manual review is still required for code quality and reasoning depth.

## Verification Commands

Commands used during development:

```powershell
python -m pytest -q
python -m compileall -q src run_benchmark.py scripts autograde.py ui_app.py
python run_benchmark.py --dataset data\hotpot_data.json --mode mock --out-dir outputs\final_test_check --limit 2
```

Current tests pass:

```text
1 passed
```
