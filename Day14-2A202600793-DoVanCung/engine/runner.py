import asyncio
import time
from typing import List, Dict

class BenchmarkRunner:
    """Async Benchmark Runner with batch processing for rate limit management"""
    
    def __init__(self, agent, retrieval_evaluator, judge):
        self.agent = agent
        self.retrieval_evaluator = retrieval_evaluator
        self.judge = judge

    async def run_single_test(self, test_case: Dict) -> Dict:
        """Run single test case through pipeline"""
        start_time = time.perf_counter()
        
        # 1. Call Agent
        response = await self.agent.query(test_case["question"])
        agent_latency = time.perf_counter() - start_time
        
        # 2. Evaluate Retrieval Quality (Hit Rate + MRR)
        retrieval_scores = self.retrieval_evaluator.evaluate_single_case(test_case)
        
        # 3. Run Multi-Judge Consensus
        judge_result = await self.judge.evaluate_multi_judge(
            test_case["question"],
            response.get("answer", ""),
            test_case.get("expected_answer", "")
        )
        
        # Determine pass/fail
        status = "pass" if judge_result["final_score"] >= 3.0 else "fail"
        
        return {
            "case_id": test_case.get("id", "unknown"),
            "question": test_case["question"],
            "agent_response": response.get("answer", ""),
            "expected_answer": test_case.get("expected_answer", ""),
            "latency_seconds": round(agent_latency, 3),
            "retrieval": retrieval_scores,
            "judge": judge_result,
            "status": status,
            "difficulty": test_case.get("metadata", {}).get("difficulty", "unknown")
        }

    async def run_all(self, dataset: List[Dict], batch_size: int = 5) -> List[Dict]:
        """
        Run benchmarks in parallel with batch processing
        
        Args:
            dataset: List of test cases
            batch_size: Number of concurrent requests (to avoid rate limiting)
        
        Returns:
            List of test results
        """
        results = []
        total = len(dataset)
        
        print(f"🚀 Running {total} test cases with batch_size={batch_size}...")
        
        for batch_idx in range(0, total, batch_size):
            batch = dataset[batch_idx:batch_idx + batch_size]
            print(f"⏳ Processing batch {batch_idx // batch_size + 1}/{(total + batch_size - 1) // batch_size}...")
            
            # Run tests in parallel for this batch
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"⚠️ Error: {result}")
                else:
                    results.append(result)
            
            # Small delay between batches to avoid rate limiting
            if batch_idx + batch_size < total:
                await asyncio.sleep(0.5)
        
        return results

