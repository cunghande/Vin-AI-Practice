import asyncio
import json
import os
import time
from engine.runner import BenchmarkRunner
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import MultiModelJudge
from agent.main_agent import MainAgent

async def run_benchmark_with_results(agent_version: str) -> tuple:
    """Run complete benchmark pipeline"""
    print(f"🚀 Khởi động Benchmark cho {agent_version}...")

    # Check if dataset exists
    if not os.path.exists("data/golden_set.jsonl"):
        print("❌ Thiếu data/golden_set.jsonl. Hãy chạy 'python data/synthetic_gen.py' trước.")
        return None, None

    # Load dataset
    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("❌ File data/golden_set.jsonl rỗng. Hãy tạo ít nhất 1 test case.")
        return None, None

    print(f"📊 Loaded {len(dataset)} test cases")
    
    # Initialize components
    agent = MainAgent()
    retrieval_evaluator = RetrievalEvaluator()
    judge = MultiModelJudge()
    
    # Run benchmark
    runner = BenchmarkRunner(agent, retrieval_evaluator, judge)
    start_time = time.time()
    results = await runner.run_all(dataset, batch_size=5)
    elapsed_time = time.time() - start_time
    
    print(f"✅ Completed {len(results)} test cases in {elapsed_time:.2f}s")
    
    # Calculate metrics
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = total - passed
    
    retrieval_metrics = {
        "avg_hit_rate": sum(r["retrieval"]["hit_rate"] for r in results) / total,
        "avg_mrr": sum(r["retrieval"]["mrr"] for r in results) / total,
    }
    
    judge_metrics = {
        "avg_score": sum(r["judge"]["final_score"] for r in results) / total,
        "avg_agreement_rate": sum(r["judge"]["agreement_rate"] for r in results) / total,
        "conflict_cases": sum(1 for r in results if r["judge"].get("conflict_detected", False))
    }
    
    # Group by difficulty
    difficulty_breakdown = {}
    for difficulty in ["easy", "medium", "hard", "adversarial"]:
        cases = [r for r in results if r["difficulty"] == difficulty]
        if cases:
            difficulty_breakdown[difficulty] = {
                "total": len(cases),
                "passed": sum(1 for c in cases if c["status"] == "pass"),
                "avg_score": sum(c["judge"]["final_score"] for c in cases) / len(cases)
            }
    
    summary = {
        "metadata": {
            "version": agent_version,
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "elapsed_seconds": round(elapsed_time, 2),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "batch_size": 5
        },
        "metrics": {
            "hit_rate": round(retrieval_metrics["avg_hit_rate"], 3),
            "mrr": round(retrieval_metrics["avg_mrr"], 3),
            "avg_score": round(judge_metrics["avg_score"], 2),
            "agreement_rate": round(judge_metrics["avg_agreement_rate"], 3),
            "conflict_cases": judge_metrics["conflict_cases"]
        },
        "difficulty_breakdown": difficulty_breakdown
    }
    
    return results, summary

async def main():
    # Run V1 Baseline
    print("\n" + "="*60)
    print("PHASE 1: Baseline Agent (V1)")
    print("="*60)
    v1_results, v1_summary = await run_benchmark_with_results("Agent_V1_Baseline")
    
    if not v1_summary:
        print("❌ Failed to run benchmark. Check data/golden_set.jsonl")
        return

    # Simulate V2 with slight improvement
    print("\n" + "="*60)
    print("PHASE 2: Optimized Agent (V2)")
    print("="*60)
    v2_results, v2_summary = await run_benchmark_with_results("Agent_V2_Optimized")

    # Regression Analysis
    print("\n" + "="*60)
    print("PHASE 3: Regression Analysis & Release Gate Decision")
    print("="*60)
    
    v1_score = v1_summary["metrics"]["avg_score"]
    v2_score = v2_summary["metrics"]["avg_score"]
    v1_hr = v1_summary["metrics"]["hit_rate"]
    v2_hr = v2_summary["metrics"]["hit_rate"]
    
    delta_score = v2_score - v1_score
    delta_hr = v2_hr - v1_hr
    
    print(f"\n📊 Metrics Comparison:")
    print(f"  V1 Judge Score: {v1_score:.2f} → V2: {v2_score:.2f} (Δ {delta_score:+.2f})")
    print(f"  V1 Hit Rate: {v1_hr:.3f} → V2: {v2_hr:.3f} (Δ {delta_hr:+.3f})")
    print(f"  V1 Latency: {v1_summary['metadata']['elapsed_seconds']:.2f}s → V2: {v2_summary['metadata']['elapsed_seconds']:.2f}s")
    
    # Release Gate Logic
    SCORE_THRESHOLD = 0.2  # Min improvement required
    HR_THRESHOLD = -0.05   # Max degradation allowed
    
    print(f"\n🚪 Release Gate Criteria:")
    print(f"  ✓ Judge Score improvement: {delta_score:+.2f} >= {SCORE_THRESHOLD}? {delta_score >= SCORE_THRESHOLD}")
    print(f"  ✓ Hit Rate no regression: {delta_hr:+.3f} >= {HR_THRESHOLD}? {delta_hr >= HR_THRESHOLD}")
    
    can_release = (delta_score >= SCORE_THRESHOLD and delta_hr >= HR_THRESHOLD)
    
    if can_release:
        decision = "✅ APPROVE - Ready for production release"
    else:
        decision = "❌ BLOCK - Address regressions before release"
    
    print(f"\n🎯 DECISION: {decision}")

    # Save reports
    print("\n💾 Saving reports...")
    os.makedirs("reports", exist_ok=True)
    
    # Summary report
    v2_summary["regression"] = {
        "vs_v1": {
            "score_delta": round(delta_score, 2),
            "hit_rate_delta": round(delta_hr, 3),
            "decision": decision
        }
    }
    
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    
    # Detailed results
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(v2_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved: reports/summary.json")
    print(f"✅ Saved: reports/benchmark_results.json")

if __name__ == "__main__":
    asyncio.run(main())

