import json
import asyncio
import os
from typing import List, Dict
import random

# Synthetic Dataset Generator - Day 14 Lab
class GoldenDatasetGenerator:
    """Tạo Golden Dataset với 50+ high-quality test cases"""
    
    def __init__(self):
        self.documents = {
            "policy_handbook.pdf": [
                "Chính sách phép năm được cấp 20 ngày/năm cho nhân viên full-time.",
                "Thời gian làm việc: 8:30 AM - 5:30 PM, thứ 2-6 hàng tuần.",
                "Lương tháng 13 được cấp vào cuối năm cho tất cả nhân viên.",
                "Bảo hiểm y tế bao gồm: bản thân, vợ/chồng, con em.",
                "Quy trình xin phép: yêu cầu trước 3 ngày làm việc.",
            ],
            "benefits_guide.pdf": [
                "Gói học tập: công ty hỗ trợ 50% học phí khóa học online.",
                "Gym membership: công ty thanh toán 70% chi phí hàng tháng.",
                "Allowance ăn trưa: 200k VND/tháng cho công ty cung cấp.",
                "Tea & coffee: miễn phí tại văn phòng.",
                "Annual team building: budget 5M VND/năm.",
            ],
            "remote_work_policy.pdf": [
                "Work from home được phép 2 ngày/tuần tùy project.",
                "Buổi họp online phải có camera bật.",
                "Time tracking: sử dụng Toggl Track hoặc Asana.",
                "Internet allowance: 500k VND/tháng cho WFH.",
                "Laptop & equipment: công ty cung cấp đầy đủ.",
            ],
            "pto_faq.pdf": [
                "Phép sinh nhật: +1 ngày ngoài quota thường.",
                "Phép hưởng sau 6 tháng: được tích lũy từ tháng đầu.",
                "Sick leave: không cần xin phép nếu <2 ngày liên tiếp.",
                "Emergency leave: được phê duyệt ngay, báo cáo hậu quả.",
                "Phép năm tối đa tích lũy: 10 ngày (sau đó mất).",
            ]
        }

    def generate_qa_pairs(self, num_cases: int = 50) -> List[Dict]:
        """Generate diverse test cases: easy, medium, hard, adversarial"""
        cases = []
        
        # Easy cases (15): straightforward factual questions
        easy_questions = [
            ("Công ty cho bao nhiêu ngày phép/năm?", "policy_handbook.pdf", "20"),
            ("Giờ làm việc bình thường là mấy giờ?", "policy_handbook.pdf", "8:30 AM - 5:30 PM"),
            ("Lương tháng 13 có được cấp không?", "policy_handbook.pdf", "Có"),
            ("Bảo hiểm y tế bao gồm ai?", "policy_handbook.pdf", "bản thân, vợ/chồng, con em"),
            ("Phải xin phép trước bao lâu?", "policy_handbook.pdf", "3 ngày"),
            ("Công ty hỗ trợ bao % học phí?", "benefits_guide.pdf", "50%"),
            ("Gym allowance là bao %?", "benefits_guide.pdf", "70%"),
            ("Allowance ăn trưa là bao nhiêu?", "benefits_guide.pdf", "200k VND"),
            ("WFH được bao nhiêu ngày/tuần?", "remote_work_policy.pdf", "2"),
            ("Allowance internet WFH là bao nhiêu?", "remote_work_policy.pdf", "500k"),
            ("Phép sinh nhật bao nhiêu ngày?", "pto_faq.pdf", "+1"),
            ("Sick leave <2 ngày có cần xin phép?", "pto_faq.pdf", "Không"),
            ("Phép tối đa tích lũy là bao nhiêu?", "pto_faq.pdf", "10 ngày"),
            ("Tea & coffee tại văn phòng có miễn phí?", "benefits_guide.pdf", "Có"),
            ("Budget team building/năm là bao nhiêu?", "benefits_guide.pdf", "5M VND"),
        ]
        
        # Medium cases (20): combining multiple docs
        medium_questions = [
            ("Nếu mình WFH, có được internet allowance không?", "remote_work_policy.pdf", "500k VND"),
            ("Tổng benefit ăn trưa + gym trong tháng bao nhiêu?", "benefits_guide.pdf", "70% gym + 200k ăn"),
            ("Phép hưởng bắt đầu từ khi nào?", "pto_faq.pdf", "6 tháng"),
            ("WFH có cần bật camera không?", "remote_work_policy.pdf", "Có (buổi họp)"),
            ("Laptop WFH do ai cung cấp?", "remote_work_policy.pdf", "công ty"),
            ("Kết hợp phép sinh nhật + phép thường được bao nhiêu?", "policy_handbook.pdf + pto_faq.pdf", "21"),
            ("Learning budget + gym budget/năm bao nhiêu?", "benefits_guide.pdf", "Tùy chi phí khóa học"),
            ("Time tracking tool nào để WFH?", "remote_work_policy.pdf", "Toggl Track hoặc Asana"),
            ("Sau bao lâu mới được hưởng phép?", "pto_faq.pdf", "6 tháng"),
            ("Overtime được thanh toán như thế nào?", "policy_handbook.pdf", "Không đề cập (không tìm thấy)"),
            ("Có được WFH 100% không?", "remote_work_policy.pdf", "Không, tối đa 2 ngày/tuần"),
            ("Emergency leave được xử lý thế nào?", "pto_faq.pdf", "được phê duyệt ngay, báo cáo hậu quả"),
            ("Phép bị mất nếu không dùng khi nào?", "pto_faq.pdf", "tích lũy quá 10 ngày"),
            ("Công ty có hỗ trợ học tập không?", "benefits_guide.pdf", "Có, 50%"),
            ("Sick leave kéo dài quá 2 ngày thì sao?", "pto_faq.pdf", "cần xin phép"),
            ("Annual team building budget là bao nhiêu?", "benefits_guide.pdf", "5M VND"),
            ("Internet allowance dành cho ai?", "remote_work_policy.pdf", "WFH"),
            ("Phép tối thiểu phải lấy là bao nhiêu?", "pto_faq.pdf", "Không quy định"),
            ("Lương tháng 13 có bị khấu không?", "policy_handbook.pdf", "Không đề cập"),
            ("Chứng chỉ học tập có được quy đổi tiền không?", "benefits_guide.pdf", "Không đề cập"),
        ]
        
        # Hard cases (10): inference + ambiguity
        hard_questions = [
            ("Nếu lấy sick leave 2 ngày rồi quay lại 1 ngày rồi lại sick 1 ngày, có bị tính liên tiếp không?", "pto_faq.pdf", "Không (không liên tiếp)"),
            ("Khi nào nên chọn WFH vs office để optimize benefit?", "remote_work_policy.pdf + benefits_guide.pdf", "Tùy prefer & project"),
            ("Team building budget có thể dùng cho cá nhân không?", "benefits_guide.pdf", "Không (team activity)"),
            ("Phép hưởng + phép tích lũy tối đa là bao nhiêu?", "pto_faq.pdf + policy_handbook.pdf", "30 (20+10)"),
            ("Đồng tính được hưởng benefit cho partner không?", "benefits_guide.pdf", "Cần xác nhận (hiện chỉ nêu vợ/chồng)"),
            ("WFH vào ngày Friday có được flexibility?", "remote_work_policy.pdf", "Không đề cập rõ"),
            ("Nếu resign giữa năm, lương tháng 13 được bao nhiêu?", "policy_handbook.pdf", "Không đề cập (tính tỷ lệ?)"),
            ("Online course được học trong giờ làm việc không?", "benefits_guide.pdf", "Không quy định"),
            ("Nếu company closed, WFH mandatory có được internet allowance tăng không?", "remote_work_policy.pdf", "Không quy định"),
            ("Multiple leaves được stack không (phép + sick + emergency)?", "pto_faq.pdf", "Không quy định rõ"),
        ]
        
        # Adversarial/Red Team cases (5): designed to fail/trick
        adversarial_questions = [
            ("Công ty cho bao nhiêu ngày phép?", "employee_handbook.pdf", "Tài liệu không tồn tại"),
            ("Lương tháng 14 có được cấp không?", "policy_handbook.pdf", "Không (không có tháng 14)"),
            ("CEO có giới hạn phép không?", "policy_handbook.pdf", "Không đề cập (khác nhân viên)"),
            ("Phép được trả tiền khi resign có không?", "policy_handbook.pdf", "Không nêu (tùy luật)"),
            ("Gender pay gap là bao nhiêu %?", "policy_handbook.pdf", "Không đề cập"),
        ]
        
        # Combine all
        all_questions = easy_questions + medium_questions + hard_questions + adversarial_questions
        
        for i, (q, doc, expected_ans) in enumerate(all_questions[:num_cases], 1):
            # Parse doc string - handle both single doc and multi-doc cases
            doc_list = [d.strip() for d in doc.split("+")]  # Split by + if present
            retrieved_docs = [d.replace(".pdf", "") for d in doc_list]  # Remove .pdf extension
            
            # Get contexts from documents - safely handle missing docs
            contexts = []
            for d in doc_list:
                doc_key = d if d.endswith(".pdf") else d + ".pdf"
                doc_contexts = self.documents.get(doc_key, ["Không tìm thấy tài liệu"])
                contexts.append(doc_contexts[min(i-1, len(doc_contexts)-1)])  # Use min to avoid index out of range
            
            case = {
                "id": f"case_{i:03d}",
                "question": q,
                "expected_answer": expected_ans,
                "expected_retrieval_ids": retrieved_docs,
                "contexts": contexts,
                "metadata": {
                    "difficulty": self._categorize_difficulty(i),
                    "source_docs": retrieved_docs,
                    "created_at": "2026-06-16"
                }
            }
            cases.append(case)
        
        return cases
    
    def _categorize_difficulty(self, idx: int) -> str:
        """Categorize test case difficulty based on index"""
        if idx <= 15:
            return "easy"
        elif idx <= 35:
            return "medium"
        elif idx <= 45:
            return "hard"
        else:
            return "adversarial"

async def main():
    generator = GoldenDatasetGenerator()
    qa_pairs = generator.generate_qa_pairs(50)
    
    os.makedirs("data", exist_ok=True)
    with open("data/golden_set.jsonl", "w", encoding="utf-8") as f:
        for pair in qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")
    
    print(f"✅ Generated {len(qa_pairs)} test cases")
    print(f"📊 Distribution: 15 easy, 20 medium, 10 hard, 5 adversarial")
    print(f"📁 Saved to: data/golden_set.jsonl")

if __name__ == "__main__":
    asyncio.run(main())
