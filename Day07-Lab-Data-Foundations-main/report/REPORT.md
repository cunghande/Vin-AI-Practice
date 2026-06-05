# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Do Van Cung  
**Nhóm:** [NHÓM ĐIỀN]  
**Ngày:** 2026-06-05

---

## 1. Warm-up (Cá nhân)

### Cosine Similarity

**High cosine similarity nghĩa là gì?**  
Hai text chunks có cosine similarity cao nghĩa là vector embedding của chúng cùng hướng trong không gian vector. Nói đơn giản, chúng có nội dung hoặc ý nghĩa gần nhau, dù không nhất thiết dùng đúng cùng từ.

**Ví dụ HIGH similarity:**
- Sentence A: Python is used for data analysis and automation.
- Sentence B: Python helps developers analyze data and automate tasks.
- Tại sao tương đồng: Hai câu đều nói về Python, data analysis và automation.

**Ví dụ LOW similarity:**
- Sentence A: Vector databases store embeddings for similarity search.
- Sentence B: The weather forecast says it will rain tomorrow.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector, nên phù hợp để đo mức giống nhau về ngữ nghĩa. Euclidean distance bị ảnh hưởng nhiều bởi độ dài/magnitude của vector hơn, trong khi text embeddings thường cần so ý nghĩa hơn là độ lớn tuyệt đối.

### Chunking Math

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**  
Formula: `ceil((doc_length - overlap) / (chunk_size - overlap))`  
Tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11) = 23`  
Đáp án: **23 chunks**.

**Nếu overlap tăng lên 100 thì sao?**  
Tính: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25`, nên số chunk tăng lên **25 chunks**. Overlap nhiều hơn giúp giữ ngữ cảnh giữa hai chunk liền kề, nhưng cũng làm tăng số chunk và chi phí retrieval.

---

## 2. Document Selection - Nhóm

### Domain & Lý Do Chọn

**Domain:** [NHÓM ĐIỀN]

**Tại sao nhóm chọn domain này?**  
[NHÓM ĐIỀN: viết 2-3 câu giải thích vì sao chọn bộ tài liệu này.]

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 2 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 3 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 4 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 5 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | `data/python_intro.txt` | Biết chunk đến từ tài liệu nào để kiểm chứng câu trả lời. |
| category | string | `technical`, `support`, `policy` | Giúp lọc tài liệu theo nhóm nội dung trước khi search. |
| language | string | `en`, `vi` | Hữu ích khi query hoặc tài liệu có nhiều ngôn ngữ. |

---

## 3. Chunking Strategy - Cá nhân chọn, nhóm so sánh

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu mẫu với `chunk_size=500`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| python_intro.txt | FixedSizeChunker | 5 | 428.8 | Trung bình, có thể cắt ngang câu |
| python_intro.txt | SentenceChunker | 5 | 387.0 | Tốt, giữ nguyên ranh giới câu |
| python_intro.txt | RecursiveChunker | 5 | 387.0 | Tốt, ưu tiên đoạn/câu trước |
| vector_store_notes.md | FixedSizeChunker | 5 | 464.6 | Trung bình |
| vector_store_notes.md | SentenceChunker | 8 | 263.6 | Tốt nhưng chunk nhỏ hơn |
| vector_store_notes.md | RecursiveChunker | 7 | 301.4 | Tốt, cân bằng cấu trúc và độ dài |
| rag_system_design.md | FixedSizeChunker | 6 | 440.2 | Trung bình |
| rag_system_design.md | SentenceChunker | 5 | 476.0 | Tốt |
| rag_system_design.md | RecursiveChunker | 7 | 339.7 | Tốt, dễ giữ section/ngữ cảnh |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**  
Tôi chọn `RecursiveChunker` vì strategy này thử chia văn bản theo separator ưu tiên: đoạn văn, dòng mới, câu, khoảng trắng, rồi cuối cùng mới cắt theo kích thước cố định. Nếu một phần văn bản vẫn quá dài, hàm `_split` tiếp tục chia bằng separator nhỏ hơn. Cách này giúp chunk không vượt quá `chunk_size` nhưng vẫn cố giữ cấu trúc tự nhiên của tài liệu.

**Tại sao tôi chọn strategy này cho domain nhóm?**  
Với tài liệu dạng ghi chú kỹ thuật, FAQ, SOP hoặc policy, nội dung thường có đoạn, heading và câu rõ ràng. `RecursiveChunker` phù hợp vì nó ít cắt ngang ý hơn `FixedSizeChunker`, đồng thời linh hoạt hơn `SentenceChunker` khi gặp đoạn quá dài.

**Code snippet:**  
Không dùng custom strategy. Tôi dùng `RecursiveChunker(chunk_size=500)`.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| vector_store_notes.md | FixedSizeChunker | 5 | 464.6 | Baseline ổn nhưng có nguy cơ cắt ngang ý |
| vector_store_notes.md | RecursiveChunker | 7 | 301.4 | Chunk dễ đọc hơn, giữ cấu trúc tốt hơn |
| rag_system_design.md | SentenceChunker | 5 | 476.0 | Chunk dài hơn, nhiều ý trong một chunk |
| rag_system_design.md | RecursiveChunker | 7 | 339.7 | Cân bằng hơn cho retrieval top-k |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | [NHÓM ĐIỀN] | Giữ cấu trúc đoạn/câu, ít cắt ngang ý | Có thể tạo nhiều chunk hơn |
| [Tên] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| [Tên] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |

**Strategy nào tốt nhất cho domain này? Tại sao?**  
[NHÓM ĐIỀN sau khi cả nhóm chạy cùng 5 benchmark queries.]

---

## 4. My Approach - Cá nhân

### Chunking Functions

**`SentenceChunker.chunk` - approach:**  
Tôi dùng regex `(?<=[.!?])(?:\s+|\n+)` để tách câu sau các dấu `.`, `!`, `?` khi có khoảng trắng hoặc xuống dòng phía sau. Sau đó tôi gom tối đa `max_sentences_per_chunk` câu vào một chunk và strip khoảng trắng thừa. Edge case: nếu input rỗng thì trả về list rỗng, nếu không tách được câu thì trả về text đã strip.

**`RecursiveChunker.chunk` / `_split` - approach:**  
Tôi dùng thuật toán đệ quy: nếu text đã nhỏ hơn `chunk_size` thì trả về ngay, nếu chưa thì thử separator hiện tại. Khi phần nào vẫn quá dài, `_split` gọi lại chính nó với separator tiếp theo. Nếu hết separator hoặc gặp separator rỗng, code fallback sang `FixedSizeChunker` để đảm bảo vẫn chia được.

### EmbeddingStore

**`add_documents` + `search` - approach:**  
Store dùng in-memory list, mỗi record gồm `id`, `doc_id`, `content`, `metadata`, và `embedding`. Khi add document, tôi gọi embedding function trên content và lưu vector lại. Khi search, tôi embed query, tính dot product với từng record, sort theo score giảm dần rồi trả về top-k.

**`search_with_filter` + `delete_document` - approach:**  
`search_with_filter` lọc metadata trước, sau đó mới chạy similarity search trên các record còn lại. Cách này mô phỏng metadata pre-filtering trong vector database thật. `delete_document` xóa tất cả record có `doc_id` tương ứng trong metadata hoặc field `doc_id`, rồi trả về `True` nếu số lượng record giảm.

### KnowledgeBaseAgent

**`answer` - approach:**  
Agent nhận câu hỏi, gọi `store.search(question, top_k)` để lấy các chunk liên quan, rồi ghép chúng thành phần `Context` trong prompt. Prompt yêu cầu LLM chỉ trả lời dựa trên context; nếu context không đủ thì nói không có thông tin trong knowledge base. Cuối cùng agent gọi `llm_fn(prompt)` và trả về answer.

### Test Results

```text
pytest tests/ -v
42 passed in 0.33s
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions - Cá nhân

Embedding dùng trong lần chạy này là `MockEmbedder`, vì lab mặc định không cần API key thật.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a programming language for data analysis. | Python is used to write scripts and analyze data. | high | -0.2655 | Không |
| 2 | Vector stores rank documents by embedding similarity. | A database can search vectors using similarity scores. | high | -0.1234 | Không |
| 3 | RAG retrieves context before generating an answer. | The system finds relevant chunks and then answers the question. | high | -0.0389 | Không |
| 4 | Customers can request a refund within the policy window. | Neural networks learn patterns from training data. | low | 0.0728 | Tương đối |
| 5 | Chunk overlap preserves context between neighboring chunks. | The weather tomorrow may be rainy and cold. | low | -0.0109 | Tương đối |

**Kết quả nào bất ngờ nhất? Điều này nói gì về embeddings?**  
Điều bất ngờ nhất là các cặp câu có nghĩa gần nhau lại có score âm. Lý do là `MockEmbedder` trong lab chỉ tạo vector deterministic để test code, không phải semantic embedding thật. Nếu dùng `LocalEmbedder` hoặc `OpenAIEmbedder`, tôi kỳ vọng các cặp cùng chủ đề sẽ có cosine similarity cao hơn rõ ràng.

---

## 6. Results - Cá nhân

Phần này cần 5 benchmark queries chung của nhóm. Sau khi nhóm thống nhất query và gold answer, tôi sẽ chạy lại bằng implementation cá nhân với strategy `RecursiveChunker`.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 2 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 3 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 4 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |
| 5 | [NHÓM ĐIỀN] | [NHÓM ĐIỀN] |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | [NHÓM ĐIỀN] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] |
| 2 | [NHÓM ĐIỀN] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] |
| 3 | [NHÓM ĐIỀN] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] |
| 4 | [NHÓM ĐIỀN] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] |
| 5 | [NHÓM ĐIỀN] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] | [CHẠY SAU] |

**Bao nhiêu queries trả về chunk relevant trong top-3?** [CHẠY SAU] / 5

---

## 7. What I Learned

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
[NHÓM ĐIỀN sau khi so sánh strategy.]

**Điều hay nhất tôi học được từ nhóm khác qua demo:**  
[ĐIỀN SAU DEMO.]

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Tôi sẽ ưu tiên chọn tài liệu có cấu trúc rõ ràng như heading, FAQ pairs hoặc policy sections, vì retrieval phụ thuộc rất nhiều vào chất lượng chunk. Tôi cũng sẽ gắn metadata như `category`, `language`, `source` ngay từ đầu để test được `search_with_filter`.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | [NHÓM ĐIỀN] / 10 |
| Chunking strategy | Nhóm | [NHÓM ĐIỀN] / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | [CHẠY SAU] / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | [NHÓM ĐIỀN] / 5 |
| **Tổng** | | **[TÍNH SAU] / 100** |
