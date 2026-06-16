import asyncio
from typing import Dict, Any
import random

class MultiModelJudge:
    """Multi-Judge Consensus Engine with Conflict Resolution"""
    
    def __init__(self, model_a: str = "gpt-4o", model_b: str = "claude-3.5"):
        self.model_a = model_a
        self.model_b = model_b
        self.rubrics = {
            "accuracy": "Score 1-5: Accuracy compared to ground truth",
            "faithfulness": "Score 1-5: Faithful to provided context",
            "completeness": "Score 1-5: Answer completeness"
        }

    async def _simulate_judge_a(self, question: str, answer: str, gt: str) -> float:
        """Simulate GPT-4o judge (slightly more generous)"""
        # Base score logic
        base_score = 4.0
        if gt.lower() not in answer.lower():
            base_score -= 1.5
        if len(answer) < 20:
            base_score -= 0.5
        # GPT-4o tends to be slightly more generous
        noise = random.uniform(-0.3, 0.5)
        return max(1.0, min(5.0, base_score + noise))

    async def _simulate_judge_b(self, question: str, answer: str, gt: str) -> float:
        """Simulate Claude judge (stricter)"""
        # Base score logic
        base_score = 3.5
        if gt.lower() not in answer.lower():
            base_score -= 1.5
        if len(answer) < 20:
            base_score -= 0.7
        # Claude tends to be stricter
        noise = random.uniform(-0.4, 0.3)
        return max(1.0, min(5.0, base_score + noise))

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Evaluate answer using 2 judges in parallel
        
        Args:
            question: User question
            answer: Agent's answer
            ground_truth: Expected answer
        
        Returns:
            Dict with final_score, agreement_rate, individual_scores
        """
        # Call 2 judges in parallel
        score_a, score_b = await asyncio.gather(
            self._simulate_judge_a(question, answer, ground_truth),
            self._simulate_judge_b(question, answer, ground_truth)
        )
        
        # Calculate agreement rate
        agreement = 1.0 - (abs(score_a - score_b) / 5.0)  # Normalize to 0-1
        
        # Conflict resolution: if difference > 1.0 point, use weighted average
        diff = abs(score_a - score_b)
        if diff > 1.0:
            # Weight GPT-4o slightly more (track record)
            final_score = score_a * 0.6 + score_b * 0.4
        else:
            final_score = (score_a + score_b) / 2.0
        
        return {
            "final_score": round(final_score, 2),
            "agreement_rate": round(agreement, 3),
            "individual_scores": {
                self.model_a: round(score_a, 2),
                self.model_b: round(score_b, 2)
            },
            "conflict_detected": diff > 1.0,
            "reasoning": f"Judge A: {score_a:.2f} | Judge B: {score_b:.2f} | Agreement: {agreement:.1%}"
        }

    async def check_position_bias(self, response_a: str, response_b: str) -> Dict[str, Any]:
        """
        Detect position bias: does judge prefer first/second position?
        
        Args:
            response_a: First response option
            response_b: Second response option
        
        Returns:
            Dict with bias metrics
        """
        # Round 1: A first, B second
        score1_a = await self._simulate_judge_a("test", response_a, response_b)
        score1_b = await self._simulate_judge_a("test", response_b, response_a)
        
        # Round 2: B first, A second (reversed)
        score2_b = await self._simulate_judge_a("test", response_b, response_a)
        score2_a = await self._simulate_judge_a("test", response_a, response_b)
        
        # Calculate bias
        bias_magnitude = abs((score1_a - score1_b) - (score2_a - score2_b))
        
        return {
            "position_bias_score": round(bias_magnitude, 3),
            "has_bias": bias_magnitude > 0.5,
            "notes": "Bias < 0.5 is acceptable"
        }
