# Lab 16 Benchmark Report

## Metadata

- Dataset: `hotpot_data.json`
- Source data: `hotpot_dev_distractor_v1.json`
- Converted examples: 150
- Evaluated records: 300 (`150 ReAct + 150 Reflexion`)
- Mode: `llm:gpt-5.4-nano`
- Output directory: `outputs/llm_hotpot_150`

## Implementation Summary

This submission implements a ReAct baseline and a Reflexion agent. ReAct answers
each question once. Reflexion first answers the question, asks an evaluator to
judge the answer against the gold answer, and if the answer is wrong, stores a
reflection strategy before retrying.

The implementation includes:

- Structured Pydantic schemas for examples, attempts, judge results,
  reflections, run records, and reports.
- Actor, evaluator, and reflector prompts.
- A deterministic mock runtime for local checks.
- A real OpenAI runtime using `gpt-5.4-nano`.
- Real token and latency measurement from LLM responses.
- JSONL traces for ReAct and Reflexion runs.
- JSON and Markdown benchmark reports.
- A basic local UI for running experiments and viewing past reports.

## Dataset

The full converted dataset is `data/hotpot_data.json`. It was converted from
the HotpotQA dev distractor file into the same schema as `data/hotpot_mini.json`:

```json
{
  "qid": "id",
  "difficulty": "medium",
  "question": "question text",
  "gold_answer": "answer text",
  "context": [
    {"title": "title", "text": "paragraph text"}
  ]
}
```

The raw dev distractor file labels all examples as `hard`, so the converted
dataset uses a balanced and shuffled label distribution for lab analysis:

| Difficulty | Count |
|---|---:|
| easy | 50 |
| medium | 50 |
| hard | 50 |

For development discipline, the dataset was also split into a development set
and a held-out test set:

| Split | Count | Difficulty distribution | Purpose |
|---|---:|---|---|
| `data/hotpot_dev.json` | 100 | easy 33, medium 34, hard 33 | Prompt/runtime tuning |
| `data/hotpot_test.json` | 50 | easy 17, medium 16, hard 17 | Final held-out evaluation |

There is no `qid` overlap between the two splits. The results below are the
full 150-example run already completed before the split was requested; the same
optimized runtime can be applied to the held-out test split with:

```powershell
python run_benchmark.py --dataset data/hotpot_test.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_test --key-prompt visible
```

## Results

| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| Correct | 116 / 150 | 149 / 150 | +33 |
| EM | 77.33% | 99.33% | +22.00 pp |
| Avg attempts | 1.0000 | 1.2267 | +0.2267 |
| Total tokens | 261,286 | 382,014 | +120,728 |
| Avg tokens | 1,741.91 | 2,546.76 | +804.85 |
| Total latency (ms) | 459,230 | 635,257 | +176,027 |
| Avg latency (ms) | 3,061.53 | 4,235.05 | +1,173.52 |

## Failure Modes

```json
{
  "wrong_final_answer": {
    "react": 34,
    "reflexion": 1
  },
  "none": {
    "react": 116,
    "reflexion": 149
  },
  "incomplete_multi_hop": {},
  "entity_drift": {}
}
```

The main observed failure mode was `wrong_final_answer`. ReAct produced 34 wrong
final answers, while Reflexion reduced this to 1. In this experiment,
`incomplete_multi_hop` and `entity_drift` did not remain as final Reflexion
failures, but they are still relevant analysis categories because many
Reflexion corrections are intended to prevent partial-hop answers and wrong
entity selection.

## Discussion

On 150 converted HotpotQA examples, Reflexion improved exact-match accuracy from
77.33% for the one-pass ReAct baseline to 99.33%, a gain of 22 percentage
points. ReAct missed 34 examples, mostly because the first answer selected a
wrong final entity or did not sufficiently verify the final hop. Reflexion used
evaluator feedback and reflection memory to retry failed examples, reducing
wrong-final-answer failures from 34 to 1.

The improvement came with a clear cost. Reflexion used 382,014 total tokens
compared with 261,286 for ReAct, an additional 120,728 tokens. Average latency
also increased from 3.06 seconds per question to 4.24 seconds per question. This
is expected because Reflexion may call the actor, evaluator, and reflector more
than once. However, the average attempt count was only 1.2267, so most questions
still completed in a single attempt while the harder cases benefited from
reflection.

Overall, the result supports the Reflexion hypothesis: adding evaluator-guided
self-reflection can substantially improve multi-hop QA accuracy, especially
when the baseline answer is close but misses the final entity or relation. The
main tradeoff is higher token usage and slower runtime.

## Extensions Implemented

- `structured_evaluator`
- `reflection_memory`
- `benchmark_report_json`
- `mock_mode_for_autograding`

## Reproduction

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the final LLM benchmark:

```powershell
python run_benchmark.py --dataset data/hotpot_data.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_hotpot_150 --key-prompt visible
```

Run the dev/test protocol:

```powershell
python run_benchmark.py --dataset data/hotpot_dev.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_dev --key-prompt visible
python run_benchmark.py --dataset data/hotpot_test.json --mode llm --model gpt-5.4-nano --out-dir outputs/llm_test --key-prompt visible
```

Run autograde:

```powershell
python autograde.py --report-path outputs/llm_hotpot_150/report.json
```
