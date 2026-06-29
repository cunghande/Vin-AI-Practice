# Individual Reflection — Lab 18

**Tên:** Đỗ Văn Cung  
**Mã SV:** 2A202600793  
**Module phụ trách:** M1–M5 (bài cá nhân)

## 1. Mapping bài giảng vào code

| Lecture concept | Module | Hàm/class | Observation |
|---|---|---|---|
| Semantic chunking | M1 | `chunk_semantic()` | Dùng embedding khi model đã cache; fallback theo paragraph giữ pipeline chạy offline. |
| Parent-child retrieval | M1 | `chunk_hierarchical()` | Child có `parent_id`; có thể dùng child để tìm và parent để mở rộng context. |
| BM25 + Dense fusion | M2 | `BM25Search`, `DenseSearch`, `reciprocal_rank_fusion()` | RRF hợp nhất hai danh sách, không so sánh trực tiếp hai thang điểm khác nhau. |
| Cross-encoder reranking | M3 | `CrossEncoderReranker.rerank()` | Rerank top-k sau retrieval giúp giảm noise; có lexical fallback khi chưa cache model. |
| RAGAS | M4 | `evaluate_ragas()` | Tách bốn kiểu lỗi: hallucination, thiếu context, context nhiễu và câu trả lời lạc đề. |
| Contextual embeddings | M5 | `_enrich_single_call()` | Một call tạo summary, hypothetical questions, context và metadata để giảm chi phí. |

## 2. Khó khăn và cách giải quyết

- **Lỗi:** `ModuleNotFoundError: No module named 'qdrant_client'` và `No module named 'datasets'`.
  - **Debug:** xác nhận pipeline dừng tại dense index/RAGAS import.
  - **Giải quyết:** dùng fallback lexical cục bộ có cùng interface, đồng thời giữ nhánh Qdrant/RAGAS thật khi dependency đã cài.
- **Lỗi:** `UnicodeEncodeError: 'charmap' codec can't encode character` khi PowerShell dùng cp1252 in emoji/Vietnamese.
  - **Giải quyết:** cấu hình stdout với `errors="backslashreplace"` để log không làm chết pipeline.
- **Kiến thức cần bổ sung:** version-aware retrieval. Hai bản policy có từ khóa giống nhau không thể giải quyết hoàn toàn chỉ bằng embedding/RRF.

## 3. Nếu làm lại

- Chạy full stack từ đầu với Docker Qdrant, model cache và OpenAI key để lấy RAGAS thật.
- Đưa `effective_date`, `version`, `supersedes`, `status` vào metadata ngay khi ingest.
- Thêm test regression riêng cho câu hỏi phủ định, multi-hop, numeric và phiên bản hiện hành.

## 4. Action plan cho project

### Hiện tại
- Pipeline đã có chunking, hybrid retrieval, reranking, enrichment và evaluation wrapper.
- Known issues: model/API/dependencies chưa sẵn trong môi trường; version conflict cần metadata filter.

### Plan áp dụng
1. [ ] Chunking: giữ parent 2048/child 256 và retrieve child, mở rộng parent khi trả lời.
2. [ ] Search: dùng BM25 + BGE-M3 + RRF, boost tài liệu có `status=current`.
3. [ ] Reranking: dùng `BAAI/bge-reranker-v2-m3` cho top-20 thành top-3.
4. [ ] Evaluation: chạy RAGAS bốn metric trên test set, theo dõi bottom-5 mỗi lần thay đổi.
5. [ ] Enrichment: dùng combined mode một call/chunk, extract version/effective date vào metadata.

### Timeline
- **Tuần 1:** cài full dependencies, OCR PDF scan, tạo metadata phiên bản.
- **Tuần 2:** đo RAGAS baseline/production và sửa top failure.
- **Tuần 3:** tối ưu latency, cache embedding và viết regression tests.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1–5) |
|---|---:|
| Hiểu bài giảng | 4 |
| Code quality | 4 |
| Problem solving | 4 |
