# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Do Van Cung  
**MSSV:** 2A202600793  
**Nhóm:** Day07 AI - Vietnam Labor Law Retrieval  
**Ngày:** 2026-06-05

---

## 1. Warm-up (Cá nhân)

### Cosine Similarity

**High cosine similarity nghĩa là gì?**  
Hai text chunks có cosine similarity cao nghĩa là vector embedding của chúng cùng hướng trong không gian vector. Nói đơn giản, chúng có nội dung hoặc ý nghĩa gần nhau, dù không nhất thiết dùng đúng cùng từ.

**Ví dụ HIGH similarity:**
- Sentence A: Hợp đồng lao động ghi nhận việc làm có trả lương.
- Sentence B: Hợp đồng lao động là thỏa thuận về công việc và tiền lương.
- Tại sao tương đồng: Hai câu đều nói về bản chất của hợp đồng lao động.

**Ví dụ LOW similarity:**
- Sentence A: Tiền lương phải được trả đầy đủ và đúng hạn.
- Sentence B: Nội quy lao động quy định hình thức kỷ luật.
- Tại sao khác: Một câu nói về wage/payment, câu kia nói về discipline.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector, nên phù hợp để đo mức giống nhau về ngữ nghĩa. Euclidean distance bị ảnh hưởng nhiều bởi độ dài/magnitude của vector hơn, trong khi text embeddings thường cần so ý nghĩa hơn là độ lớn tuyệt đối.

### Chunking Math

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**  
Formula: `ceil((doc_length - overlap) / (chunk_size - overlap))`  
Tính: `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`  
Đáp án: **23 chunks**.

**Nếu overlap tăng lên 100 thì sao?**  
Tính: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`, nên số chunk tăng lên **25 chunks**. Overlap nhiều hơn giúp giữ ngữ cảnh giữa hai chunk liền kề, nhưng cũng làm tăng số chunk và chi phí retrieval.

---

## 2. Document Selection - Nhóm

### Domain & Lý Do Chọn

**Domain:** Luật lao động Việt Nam cơ bản.

**Tại sao nhóm chọn domain này?**  
Luật lao động là một domain legal nhỏ nhưng có cấu trúc rõ: hợp đồng, thử việc, tiền lương, thời giờ làm việc, làm thêm giờ, nghỉ phép, chấm dứt hợp đồng và kỷ luật/an toàn lao động. Mỗi chủ đề có từ khóa và metadata riêng, nên phù hợp để test retrieval, metadata filtering và RAG grounding. Dataset được nhóm thu thập từ nguồn luật/cổng thông tin pháp luật, sau đó làm sạch thành các file Markdown ngắn để đưa vào vector store.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | `01_hop_dong_lao_dong.md` | Bộ luật Lao động 2019, Cổng thông tin điện tử Chính phủ | 1763 | `category=contract`, `language=vi` |
| 2 | `02_thu_viec.md` | Bộ luật Lao động 2019, Cổng thông tin điện tử Chính phủ | 1776 | `category=probation`, `language=vi` |
| 3 | `03_tien_luong.md` | Bộ luật Lao động 2019 + Nghị định 145/2020/NĐ-CP | 1801 | `category=wage`, `language=vi` |
| 4 | `04_thoi_gio_lam_viec_nghi_ngoi.md` | Bộ luật Lao động 2019 + Thư viện Pháp luật | 1800 | `category=working_time`, `language=vi` |
| 5 | `05_lam_them_gio.md` | Bộ luật Lao động 2019 + Nghị định 145/2020/NĐ-CP | 1790 | `category=overtime`, `language=vi` |
| 6 | `06_nghi_phep_ngay_le.md` | Bộ luật Lao động 2019, Cổng thông tin điện tử Chính phủ | 1742 | `category=leave`, `language=vi` |
| 7 | `07_cham_dut_hop_dong.md` | Bộ luật Lao động 2019, Cổng thông tin điện tử Chính phủ | 1949 | `category=termination`, `language=vi` |
| 8 | `08_ky_luat_an_toan_lao_dong.md` | Bộ luật Lao động 2019 + Nghị định 145/2020/NĐ-CP | 1872 | `category=discipline_safety`, `language=vi` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | string | `data/05_lam_them_gio.md` | Truy vết chunk về tài liệu gốc để kiểm chứng câu trả lời. |
| `category` | string | `overtime`, `wage`, `termination` | Lọc trước khi search để giảm nhiễu giữa các chủ đề pháp lý gần nhau. |
| `language` | string | `vi` | Xác định ngôn ngữ của bộ tài liệu, hữu ích nếu sau này thêm tài liệu tiếng Anh. |
| `strategy` | string | `recursive` | Ghi lại chunking strategy đã dùng khi so sánh kết quả giữa thành viên. |

---

## 3. Chunking Strategy - Cá nhân chọn, nhóm so sánh

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu legal với `chunk_size=500`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `01_hop_dong_lao_dong.md` | FixedSizeChunker | 4 | 478.2 | Medium, có thể cắt ngang câu/quy định |
| `01_hop_dong_lao_dong.md` | SentenceChunker | 3 | 585.3 | High, giữ câu nhưng chunk có thể dài |
| `01_hop_dong_lao_dong.md` | RecursiveChunker | 5 | 350.8 | High, giữ paragraph/câu tốt |
| `02_thu_viec.md` | FixedSizeChunker | 4 | 481.5 | Medium |
| `02_thu_viec.md` | SentenceChunker | 5 | 353.4 | High |
| `02_thu_viec.md` | RecursiveChunker | 5 | 353.4 | High |
| `03_tien_luong.md` | FixedSizeChunker | 4 | 487.8 | Medium |
| `03_tien_luong.md` | SentenceChunker | 4 | 448.2 | High |
| `03_tien_luong.md` | RecursiveChunker | 5 | 358.4 | High |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**  
Tôi chọn `RecursiveChunker` vì strategy này thử chia văn bản theo separator ưu tiên: đoạn văn, dòng mới, câu, khoảng trắng, rồi cuối cùng mới cắt theo kích thước cố định. Nếu một phần văn bản vẫn quá dài, hàm `_split` tiếp tục chia bằng separator nhỏ hơn. Cách này giúp chunk không vượt quá `chunk_size` nhưng vẫn cố giữ cấu trúc tự nhiên của tài liệu.

**Tại sao tôi chọn strategy này cho domain nhóm?**  
Với tài liệu legal, coherence quan trọng hơn việc tạo chunk thật nhỏ. Một quy định pháp lý thường gồm điều kiện, giới hạn và ngoại lệ; nếu cắt ngang đoạn thì agent có thể trả lời thiếu ý. `RecursiveChunker` cân bằng tốt hơn: chunk vừa phải, vẫn giữ paragraph/câu để retrieval có đủ ngữ cảnh.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| `01_hop_dong_lao_dong.md` | FixedSizeChunker | 4 | 478.2 | Đơn giản nhưng có nguy cơ cắt ngang ý pháp lý |
| `01_hop_dong_lao_dong.md` | RecursiveChunker | 5 | 350.8 | Chunk dễ đọc hơn, giữ cấu trúc tốt hơn |
| `02_thu_viec.md` | SentenceChunker | 5 | 353.4 | Giữ câu tốt nhưng phụ thuộc dấu câu |
| `02_thu_viec.md` | RecursiveChunker | 5 | 353.4 | Kết quả tương đương, linh hoạt hơn khi có paragraph dài |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker + metadata filter | 10 / 10 | Giữ cấu trúc legal topic, dùng `category` để giảm nhiễu | Phụ thuộc separator rõ trong tài liệu |
| Phạm Đình Phúc | RecursiveChunker + legal keyword embedding fallback | 10 / 10 | Benchmark tái lập tốt khi chưa có OpenAI key | Keyword embedding không hiểu semantic sâu |
| Baseline nhóm | FixedSizeChunker | Reference | Đơn giản, độ dài chunk ổn định | Dễ cắt ngang điều kiện/ngoại lệ pháp lý |
| Baseline nhóm | SentenceChunker | Reference | Giữ nguyên câu | Có thể tách điều kiện và kết luận sang chunk khác |

**Strategy nào tốt nhất cho domain này? Tại sao?**  
Với bộ tài liệu luật lao động, `RecursiveChunker` là lựa chọn phù hợp nhất vì tài liệu có paragraph và câu dài. Strategy này giữ được ngữ cảnh pháp lý tốt hơn fixed-size, đồng thời không chia quá vụn như sentence-only chunking. Metadata filter theo `category` là phần rất quan trọng vì nhiều tài liệu đều lặp lại các cụm như “người lao động”, “người sử dụng lao động”, “thời giờ”, “tiền lương”.

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
42 passed
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

5 benchmark queries dưới đây là bộ query nhóm thống nhất cho domain luật lao động. Tôi chạy trên implementation cá nhân trong package `src`, dùng `RecursiveChunker(chunk_size=500)`, `EmbeddingStore`, và metadata filter theo `category`. Vì chưa dùng OpenAI key thật, benchmark dùng một keyword embedding tiếng Việt cục bộ để kết quả tái lập được; tiêu chí chính vẫn là top-3 có chunk relevant.

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Hợp đồng lao động có những loại nào và nội dung cần có gì? | Có hợp đồng không xác định thời hạn và xác định thời hạn; nội dung thường gồm công việc, địa điểm, lương, thời giờ, bảo hiểm và điều kiện lao động. |
| 2 | Thời gian thử việc tối đa cho công việc cần trình độ cao đẳng trở lên là bao lâu? | Thời gian thử việc cho công việc cần trình độ cao đẳng trở lên thường không quá 60 ngày. |
| 3 | Người sử dụng lao động phải trả lương cho người lao động như thế nào? | Phải trả lương trực tiếp, đầy đủ, đúng hạn và minh bạch về cách tính, bảng lương, khấu trừ nếu có. |
| 4 | Thời giờ làm việc bình thường tối đa mỗi ngày và mỗi tuần là bao nhiêu? | Không quá 8 giờ/ngày và 48 giờ/tuần; nếu tính theo tuần có thể tối đa 10 giờ/ngày nhưng vẫn không quá 48 giờ/tuần. |
| 5 | Làm thêm giờ cần điều kiện gì và giới hạn theo tháng năm ra sao? | Cần sự đồng ý của người lao động và phải trong giới hạn như 40 giờ/tháng, 200 giờ/năm trừ một số trường hợp đặc biệt. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Hợp đồng lao động có những loại nào và nội dung cần có gì? | `data/01_hop_dong_lao_dong.md`: định nghĩa, hình thức và nội dung hợp đồng | 0.6903 | Yes | Trả lời dựa trên context hợp đồng lao động |
| 2 | Thời gian thử việc tối đa cho công việc cần trình độ cao đẳng trở lên là bao lâu? | `data/02_thu_viec.md`: thử việc bao lâu, lương thử việc, kết thúc thử việc | 0.0976 | Yes | Trả lời dựa trên context thử việc |
| 3 | Người sử dụng lao động phải trả lương cho người lao động như thế nào? | `data/03_tien_luong.md`: cách tính lương, bảng kê lương, lương làm thêm | 0.4851 | Yes | Trả lời dựa trên context tiền lương |
| 4 | Thời giờ làm việc bình thường tối đa mỗi ngày và mỗi tuần là bao nhiêu? | `data/04_thoi_gio_lam_viec_nghi_ngoi.md`: thời giờ làm việc, nghỉ giữa giờ, nghỉ hằng tuần | 0.0937 | Yes | Trả lời dựa trên context thời giờ làm việc |
| 5 | Làm thêm giờ cần điều kiện gì và giới hạn theo tháng năm ra sao? | `data/05_lam_them_gio.md`: làm thêm giờ, làm đêm, giới hạn overtime | 0.0000 | Yes | Trả lời dựa trên context làm thêm giờ |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5  
**Retrieval quality score:** 10 / 10 theo rubric top-3 relevant.

### Metadata Filter Check

Khi không dùng metadata filter, một số query dễ bị lệch sang tài liệu khác vì các tài liệu legal lặp nhiều từ giống nhau:

| Query category | Top-1 không filter | Top-1 có filter |
|----------------|--------------------|-----------------|
| `contract` | `data/01_hop_dong_lao_dong.md` | `data/01_hop_dong_lao_dong.md` |
| `probation` | `data/07_cham_dut_hop_dong.md` | `data/02_thu_viec.md` |
| `wage` | `data/01_hop_dong_lao_dong.md` | `data/03_tien_luong.md` |
| `working_time` | `data/07_cham_dut_hop_dong.md` | `data/04_thoi_gio_lam_viec_nghi_ngoi.md` |
| `overtime` | `data/01_hop_dong_lao_dong.md` | `data/05_lam_them_gio.md` |

Metadata filtering giúp tăng precision rõ ràng, đặc biệt với các query có từ khóa chung như “người lao động”, “làm việc”, “giờ”, “lương”.

---

## 7. What I Learned

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
Từ report và data của Phạm Đình Phúc, tôi học được cách thiết kế một bộ dữ liệu legal nhỏ nhưng có cấu trúc rõ ràng theo category. Việc gắn `category`, `source`, `language` giúp retrieval dễ kiểm chứng hơn và giúp `search_with_filter()` phát huy tác dụng.

**Điều hay nhất tôi học được từ nhóm khác qua demo:**  
Điểm quan trọng là retrieval không chỉ phụ thuộc code chạy đúng, mà còn phụ thuộc data strategy. Nếu tài liệu có source rõ, metadata tốt và chunk giữ được ngữ cảnh, agent answer sẽ grounded hơn nhiều.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Tôi sẽ thu thập thêm nguồn chính thức cho từng điều khoản và lưu thêm metadata `legal_basis`, `article`, hoặc `effective_date` để filter chính xác hơn. Tôi cũng sẽ chạy lại benchmark bằng `text-embedding-3-small` hoặc local sentence-transformer thay vì mock/keyword embedding, vì legal queries thường có nhiều cách diễn đạt khác nhau.

### Failure Analysis

**Failure case tiềm ẩn:** Query về “thời giờ làm việc” và “làm thêm giờ” dễ bị lẫn nhau nếu không filter metadata, vì cả hai đều có từ khóa “giờ”, “làm”, “người lao động”.  
**Nguyên nhân:** Keyword overlap cao giữa các tài liệu legal; nếu chunk quá rộng hoặc không có metadata, vector search có thể chọn nhầm chủ đề gần.  
**Cải thiện:** Dùng metadata filter theo `category`, chunk theo paragraph bằng `RecursiveChunker`, và bổ sung semantic embedding thật để hiểu ý nghĩa thay vì chỉ dựa vào keyword.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **99 / 100** |
