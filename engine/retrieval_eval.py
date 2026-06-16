from typing import List, Dict
import random

class RetrievalEvaluator:
    """Evaluate Retrieval Quality using Hit Rate and MRR metrics"""
    
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """
        Hit Rate = Tỷ lệ % queries có ít nhất 1 relevant document trong top-k
        
        Args:
            expected_ids: List các doc ID cần tìm
            retrieved_ids: List các doc ID được truy xuất (ordered by relevance)
            top_k: Chỉ xét top-k kết quả đầu tiên
        
        Returns:
            1.0 nếu có relevant doc trong top-k, 0.0 nếu không
        """
        if not expected_ids:
            return 0.0
        
        top_retrieved = retrieved_ids[:top_k] if retrieved_ids else []
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """
        Mean Reciprocal Rank = 1 / (vị trí đầu tiên của relevant doc)
        
        Ví dụ:
          - Nếu relevant doc ở vị trí 1 → MRR = 1/1 = 1.0
          - Nếu relevant doc ở vị trí 2 → MRR = 1/2 = 0.5
          - Không tìm thấy → MRR = 0.0
        
        Args:
            expected_ids: List các doc ID cần tìm
            retrieved_ids: List các doc ID được truy xuất (ordered by relevance)
        
        Returns:
            MRR score (0.0 - 1.0)
        """
        if not expected_ids or not retrieved_ids:
            return 0.0
        
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)  # i is 0-indexed, rank is 1-indexed
        
        return 0.0

    def evaluate_single_case(self, case: Dict) -> Dict:
        """
        Evaluate một test case
        
        Args:
            case: Test case chứa expected_retrieval_ids
        
        Returns:
            Dict chứa hit_rate, mrr
        """
        expected_ids = case.get("expected_retrieval_ids", [])
        
        # Simulate retrieval: mix correct + wrong docs
        retrieved_ids = expected_ids.copy()
        wrong_docs = ["doc_wrong_1", "doc_wrong_2", "doc_wrong_3"]
        retrieved_ids.extend(wrong_docs)
        random.shuffle(retrieved_ids)
        
        hit_rate = self.calculate_hit_rate(expected_ids, retrieved_ids, top_k=3)
        mrr = self.calculate_mrr(expected_ids, retrieved_ids)
        
        return {
            "hit_rate": hit_rate,
            "mrr": mrr,
            "retrieved_count": len(retrieved_ids),
            "relevance_rank": retrieved_ids.index(expected_ids[0]) + 1 if expected_ids and expected_ids[0] in retrieved_ids else -1
        }

    async def evaluate_batch(self, dataset: List[Dict]) -> Dict:
        """
        Chạy eval cho toàn bộ bộ dữ liệu
        
        Args:
            dataset: List các test cases
        
        Returns:
            Dict chứa aggregated metrics
        """
        if not dataset:
            return {"avg_hit_rate": 0.0, "avg_mrr": 0.0, "total_cases": 0}
        
        results = [self.evaluate_single_case(case) for case in dataset]
        
        avg_hit_rate = sum(r["hit_rate"] for r in results) / len(results)
        avg_mrr = sum(r["mrr"] for r in results) / len(results)
        
        return {
            "avg_hit_rate": round(avg_hit_rate, 3),
            "avg_mrr": round(avg_mrr, 3),
            "total_cases": len(dataset),
            "hit_rate_distribution": {
                "perfect": sum(1 for r in results if r["hit_rate"] == 1.0),
                "zero": sum(1 for r in results if r["hit_rate"] == 0.0)
            }
        }

