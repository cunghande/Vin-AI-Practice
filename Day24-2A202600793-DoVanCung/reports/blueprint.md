# CI/CD Blueprint: RAG Eval + Guardrail Stack

**Sinh viên:** Đỗ Văn Cung  
**Ngày:** 2026-06-30

---

## Guard Stack Architecture

```
User Input
    │
    ▼ (~14.27ms P50)
[Presidio PII Scan]
    │ block if: VN_CCCD / VN_PHONE / EMAIL detected
    │ action:   return 400 + "PII detected in query"
    ▼ (~0.05ms P50)
[NeMo Input Rail]
    │ block if: off-topic / jailbreak / prompt injection
    │ action:   return 503 + refuse message
    ▼
[RAG Pipeline (Day 18)]
    │ M1 Chunk → M2 Search → M3 Rerank → GPT-4o-mini
    ▼
[NeMo Output Rail]
    │ flag if:  PII in response / sensitive content
    │ action:   replace with safe response
    ▼
User Response
```

---

## Latency Budget

*(Điền từ kết quả Task 12 — measure_p95_latency())*

| Layer | P50 (ms) | P95 (ms) | P99 (ms) | Budget |
|---|---|---|---|---|
| Presidio PII | 14.27 | 392.33 | 392.33 | <10ms |
| NeMo Input Rail | 0.05 | 3879.36 | 3879.36 | <300ms |
| RAG Pipeline | 1200.00 | 1800.00 | 2000.00 | <2000ms |
| NeMo Output Rail | 0.05 | 300.00 | 500.00 | <300ms |
| **Total Guard** | 15.75 | **4271.69** | 4271.69 | **<500ms** |

**Budget OK?** [ ] Yes / [x] No  
**Comment:** P95 total guard latency (4271.69ms) vượt quá ngân sách cho phép (<500ms). Nguyên nhân chủ đạo là do NeMo Input Rail thực hiện API call đồng bộ tới mô hình Gemini từ xa đối với các truy vấn cần phân loại phức tạp (~3.8s P95). Để tối ưu, cần thay thế bộ phân loại LLM bằng mô hình phân loại cục bộ siêu nhẹ (như FastText hoặc DistilBERT) để giảm độ trễ xuống dưới 10ms và chạy song song quét PII với kiểm tra chủ đề.

---

## CI/CD Gates (phải pass trước khi merge to main)

```yaml
# .github/workflows/rag_eval.yml
- name: RAGAS Quality Gate
  run: python src/phase_a_ragas.py
  env:
    MIN_FAITHFULNESS: 0.75
    MIN_AVG_SCORE: 0.65

- name: Guardrail Gate
  run: pytest tests/test_phase_c.py -k "test_adversarial_suite_pass_rate"
  # phải ≥ 15/20 (75%)

- name: Latency Gate
  run: python -c "from src.phase_c_guard import measure_p95_latency; ..."
  # P95 total < 500ms
```

---

## Monitoring Dashboard (production)

| Metric | Alert Threshold | Action |
|---|---|---|
| RAGAS faithfulness (daily sample) | < 0.70 | Page on-call |
| Adversarial block rate | < 80% | Review new attack patterns |
| Guard P95 latency | > 600ms | Scale NeMo model |
| PII detected count | spike >10/hour | Security alert |

---

## Kết quả thực tế từ Lab

| | Kết quả |
|---|---|
| RAGAS avg_score (50q) | 0.7385 |
| Worst metric | context_precision |
| Dominant failure distribution | factual |
| Cohen's κ | -0.1538 |
| Adversarial pass rate | 16 / 20 |
| Guard P95 latency | 4271.69 ms |

---

## Nhận xét & Cải tiến

> 1. **Hoạt động tốt:** Presidio PII hoạt động cực kỳ nhanh với độ trễ P50 chỉ khoảng 14ms và độ chính xác cao đối với các định dạng CCCD, số điện thoại Việt Nam và email. Cơ chế kết hợp keyword và LLM classifier giúp chặn đứng hầu hết các cuộc tấn công jailbreak và off-topic (đạt 16/20 pass rate).
> 2. **Cần cải thiện:** Độ trễ P95 của NeMo Input Rail quá lớn (~3.8s) do phụ thuộc vào các API call đồng bộ tới mô hình Gemini từ xa. Cohen's κ đạt giá trị âm (-0.1538) cho thấy LLM Judge và nhãn gán của con người có độ đồng thuận thấp trên tập test, cho thấy LLM Judge cần được điều chỉnh prompt tốt hơn để align với tiêu chuẩn đánh giá của con người.
> 3. **Thay đổi khi deploy production:** Tôi sẽ thay thế LLM Classifier bằng một mô hình phân loại cục bộ cực nhẹ (như DistilBERT hoặc FastText) để giảm độ trễ của Input Guardrail xuống dưới 10ms. Đồng thời, tôi sẽ cấu hình caching cho các câu hỏi phổ biến và triển khai cơ chế chấm điểm chéo (consensus) giữa nhiều Judge để tăng độ tin cậy của LLM Judge.
