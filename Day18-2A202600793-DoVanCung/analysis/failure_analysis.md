# Failure Analysis — Lab 18: Production RAG

**Người thực hiện:** Đỗ Văn Cung  
**Mã SV:** 2A202600793  
**Chạy pipeline:** local fallback, 22/06/2026

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|---|---:|---:|---:|
| Faithfulness | 0.0000 | 0.0000 | 0.0000 |
| Answer Relevancy | 0.0000 | 0.0000 | 0.0000 |
| Context Precision | 0.0000 | 0.0000 | 0.0000 |
| Context Recall | 0.0000 | 0.0000 | 0.0000 |

Các con số trên **không phải chất lượng thực tế**: môi trường chạy thiếu `datasets`/RAGAS và `OPENAI_API_KEY`, nên hàm đánh giá trả fallback 0. Pipeline vẫn chạy đủ 20 câu hỏi, lưu report và xác định các lỗi retrieval/phiên bản dưới đây. Cần chạy lại sau khi cài dependencies và cấu hình key để lấy metric có ý nghĩa.

## Bottom-5 Failures

### #1 — Phép năm hiện hành
- **Question:** Nhân viên được nghỉ bao nhiêu ngày phép năm?
- **Expected:** 15 ngày theo bản 2024 hiện hành, không phải 12 ngày của bản 2023.
- **Got:** Fallback lexical trả section “nghỉ phép không lương” trong lần chạy local.
- **Worst metric:** Context recall / version handling.
- **Error Tree:** Output sai → Context sai → query “phép năm” trùng nhiều chính sách → tài liệu v2023/v2024 không được ưu tiên theo hiệu lực.
- **Root cause:** Metadata chưa có trường `effective_date`/`status`; fallback dense chỉ dùng overlap từ vựng.
- **Suggested fix:** Trích version, effective date và `supersedes` vào metadata; boost phiên bản hiện hành và filter bản bị thay thế.

### #2 — Thâm niên phép năm
- **Question:** Thâm niên bao nhiêu năm thì được cộng thêm ngày phép?
- **Expected:** Từ 3 năm, cộng 1 ngày cho mỗi 3 năm (v2024).
- **Got:** Context cũ v2023 (5 năm) có thể được xếp cao hơn khi dùng lexical fallback.
- **Worst metric:** Context precision.
- **Error Tree:** Output sai → context chứa chính sách cũ → reranker fallback không hiểu quan hệ “hiện hành/thay thế”.
- **Root cause:** Hai tài liệu gần như cùng từ khóa nhưng không có rule version-aware retrieval.
- **Suggested fix:** Đưa dòng trạng thái phiên bản vào enrichment context, dùng metadata filter trước RRF và kiểm thử regression cho các câu hỏi version.

### #3 — Lương thử việc Junior
- **Question:** Lương thử việc của Junior mức cao nhất là bao nhiêu?
- **Expected:** 85% của 20.000.000 VNĐ, tức 17.000.000 VNĐ/tháng.
- **Got:** Pipeline local trả context thay vì một câu trả lời tính toán cuối cùng.
- **Worst metric:** Answer relevancy.
- **Error Tree:** Context đúng? → có bảng lương và chính sách thử việc → Output chưa tổng hợp phép tính → answer không trực tiếp.
- **Root cause:** Không có LLM generation khi thiếu API key; fallback trả nguyên chunk đầu tiên.
- **Suggested fix:** Cài API key cho grounded generation; bổ sung post-processing số học có test đơn vị cho câu hỏi multi-hop/numeric.

### #4 — Tạm ứng quá hạn
- **Question:** Nhân viên tạm ứng 15 triệu, sau 20 ngày mới thanh toán sẽ thế nào?
- **Expected:** Quá hạn 15 ngày, bị phí 2%/tháng trên số chưa hoàn ứng và chưa được duyệt tạm ứng mới.
- **Got:** Context chính sách có thể đúng nhưng câu trả lời fallback không diễn giải điều kiện và hậu quả.
- **Worst metric:** Answer relevancy.
- **Error Tree:** Context đúng → query không cần rewrite → generator fallback chỉ copy context → thiếu kết luận áp dụng cho tình huống.
- **Root cause:** Thiếu bước answer synthesis khi offline.
- **Suggested fix:** Dùng template trả lời có cấu trúc “kết luận – căn cứ – điều kiện”; dùng LLM khi có key và kiểm tra answer coverage.

### #5 — Thẩm quyền mua laptop 30 triệu
- **Question:** Mua laptop 30 triệu cần ai phê duyệt?
- **Expected:** Giám đốc phòng ban; đồng thời cần CNTT xác nhận cấu hình kỹ thuật.
- **Got:** Retrieval có thể chỉ chọn bảng ngưỡng hoặc chỉ chọn lưu ý CNTT, không đảm bảo cả hai điều kiện.
- **Worst metric:** Context recall.
- **Error Tree:** Cần multi-hop → evidence nằm ở hai section → chunk/retrieval có thể trả thiếu một section → output thiếu điều kiện.
- **Root cause:** Hierarchical children được retrieve độc lập, nhưng chưa map child về parent để mở rộng context trước generation.
- **Suggested fix:** Khi child được chọn, fetch parent/section liên quan; tăng top-k trước rerank và thêm test multi-hop.

## Case Study

**Question chọn phân tích:** “Nhân viên được nghỉ bao nhiêu ngày phép năm?”

1. **Output đúng?** Không trong local fallback: cần trả 15 ngày và nêu v2024 là bản hiện hành.
2. **Context đúng?** Không ổn định: có nhiều chunk cùng nhắc “phép năm”, gồm không lương và bản 2023.
3. **Query rewrite OK?** Chưa; cần thêm ý định “chính sách hiện hành”.
4. **Fix ở bước:** metadata enrichment → hybrid retrieval/RRF → rerank có version-aware prompt → mở rộng context parent.

**Nếu có thêm 1 giờ:** cài Qdrant, `datasets`, RAGAS, cache model BGE/reranker và chạy lại evaluation bằng OpenAI để thay thế số fallback 0.0 bằng số đo thật.
