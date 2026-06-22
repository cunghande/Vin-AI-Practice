# Group Report — Lab 18: Production RAG

**Người thực hiện:** Đỗ Văn Cung  
**Mã SV:** 2A202600793  
**Ngày:** 22/06/2026

## Module hoàn thành

| Module | Nội dung | Trạng thái | Tests |
|---|---|---|---:|
| M1 | Semantic, hierarchical, structure-aware chunking | Hoàn thành | 12/12 liên quan |
| M2 | Vietnamese BM25, dense/Qdrant và RRF | Hoàn thành, có offline fallback | 5/5 |
| M3 | CrossEncoder reranking, lexical fallback | Hoàn thành | 5/5 |
| M4 | RAGAS wrapper, report và Diagnostic Tree | Hoàn thành | 4/4 |
| M5 | Combined enrichment + bốn kỹ thuật riêng | Hoàn thành | 11/11 |

## Kết quả chạy

`python main.py` chạy thành công: đọc 26 tài liệu có text layer, tạo 117 child chunks và đánh giá 20 câu hỏi. Hai PDF scan được bỏ qua đúng chủ đích vì chưa OCR.

| Metric | Naive | Production | Δ |
|---|---:|---:|---:|
| Faithfulness | 0.0000 | 0.0000 | 0.0000 |
| Answer Relevancy | 0.0000 | 0.0000 | 0.0000 |
| Context Precision | 0.0000 | 0.0000 | 0.0000 |
| Context Recall | 0.0000 | 0.0000 | 0.0000 |

Các metric bằng 0 do môi trường thiếu `datasets`/RAGAS và API key, không phải kết quả đánh giá hợp lệ. Báo cáo chi tiết và cách khắc phục nằm trong `failure_analysis.md`.

## Key Findings

1. **Biggest improvement:** Pipeline production có retrieval theo child chunk, kết hợp BM25 + dense bằng RRF và reranking; kiến trúc đã tách các điểm tối ưu rõ ràng.
2. **Biggest challenge:** Corpus cố ý chứa policy cũ/mới, nên retrieval chỉ dựa từ khóa có thể trả v2023 thay vì v2024.
3. **Surprise finding:** Pipeline vẫn chạy được khi thiếu Qdrant/model/API nhờ fallback; nhưng fallback không thay thế được semantic ranking và grounded answer thực sự.

## Presentation Notes

1. Demo `python main.py`, sau đó mở `reports/ragas_report.json`.
2. Giải thích child retrieval → hybrid RRF → cross-encoder → answer/RAGAS.
3. Case study: phép năm hiện hành và lỗi version conflict.
4. Bước tiếp theo: cài dependencies, chạy Qdrant, cache BGE/CrossEncoder, cấu hình `OPENAI_API_KEY`, rồi đo lại RAGAS.
