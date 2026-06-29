# BÁO CÁO LAB DAY 19: XÂY DỰNG HỆ THỐNG GRAPHRAG VỚI TECH COMPANY CORPUS

Báo cáo này trình bày các nội dung nghiên cứu lý thuyết về đồ thị tri thức, thiết kế hệ thống và kết quả đánh giá so sánh giữa **Flat RAG** và **GraphRAG**.

---

## 1. PHẦN 1: NGHIÊN CỨU LÝ THUYẾT (RESEARCH)

### 1.1. Entity Extraction: LLM phân biệt Node và Thuộc tính (Attribute) như thế nào?
Để LLM phân biệt chính xác giữa thực thể (Node) và thuộc tính (Attribute/Property), chúng ta sử dụng các kỹ thuật thiết kế prompt (Prompt Engineering) và Schema Definition:
- **Node (Thực thể):** Thường đại diện cho các đối tượng độc lập, có định danh duy nhất trong thế giới thực (ví dụ: Tên công ty "OpenAI", Tên người "Sam Altman", Quốc gia "U.S."). LLM được hướng dẫn nhận diện các danh từ riêng hoặc các chủ thể độc lập này làm Node.
- **Attribute (Thuộc tính):** Là các thông tin mô tả chi tiết cho Node (ví dụ: doanh thu, tỷ lệ phần trăm tăng trưởng, năm thành lập). 
- **Cách phân biệt:** Trong Prompt trích xuất, ta định nghĩa rõ cấu trúc dữ liệu mong muốn:
  - Nếu một thông tin có thể có quan hệ riêng hoặc tồn tại độc lập, nó sẽ là một Node (ví dụ: "Sam Altman" là một Node có mối quan hệ `FOUNDED_BY` với "OpenAI").
  - Nếu thông tin chỉ mang tính chất mô tả trị số hoặc trạng thái tĩnh của một Node, nó sẽ là Attribute hoặc Object trong quan hệ tĩnh (ví dụ: `(OpenAI, FOUNDED_IN, 2015)`).

### 1.2. Graph Construction: Tầm quan trọng của khử trùng lặp (Deduplication)
Khử trùng lặp (Deduplication/Entity Resolution) là bước cực kỳ quan trọng khi xây dựng đồ thị tri thức vì:
1. **Tránh bùng nổ số lượng Node trùng lặp:** Một thực thể có thể được nhắc đến dưới nhiều tên gọi khác nhau trong các tài liệu (ví dụ: "Tesla", "Tesla Inc.", "Tesla, Inc."). Nếu không khử trùng lặp, đồ thị sẽ tạo ra 3 node khác nhau, làm mất đi tính liên kết của dữ liệu.
2. **Bảo toàn kết nối (Connectivity):** Bản chất của đồ thị là kết nối thông tin đa bước (multi-hop). Nếu "Tesla" và "Tesla Inc." là 2 node riêng biệt, một truy vấn đi qua node này sẽ không thể duyệt sang thông tin ở node kia, khiến GraphRAG bị đứt gãy thông tin.
3. **Độ chính xác của thuật toán duyệt:** Các thuật toán tính toán độ trung tâm (Centrality), PageRank, hoặc duyệt BFS sẽ bị sai lệch nghiêm trọng nếu đồ thị bị phân mảnh bởi các node trùng lặp.

### 1.3. Query Answering: Sự khác biệt giữa duyệt đồ thị theo chiều rộng (BFS) và tìm kiếm Vector thông thường
- **Tìm kiếm Vector thông thường (Flat RAG):** 
  - Hoạt động bằng cách biểu diễn câu hỏi thành vector và tính toán độ tương đồng cosine với các vector đoạn văn bản (chunks) trong cơ sở dữ liệu vector.
  - Mang tính chất tìm kiếm cục bộ (local/flat). Nó không hiểu được mối quan hệ logic hoặc liên kết chuỗi giữa các đoạn văn nằm ở các file khác nhau.
- **Duyệt đồ thị theo chiều rộng (BFS - GraphRAG):**
  - Bắt đầu bằng việc định vị các thực thể trung tâm từ câu hỏi trong đồ thị tri thức (ví dụ: "VinFast").
  - Sau đó, thuật toán duyệt BFS sẽ mở rộng ra các node lân cận trong phạm vi 1-hop, 2-hop (ví dụ: tìm tất cả các node kết nối với "VinFast", rồi tìm tiếp các node kết nối với các node đó).
  - Giúp xâu chuỗi các sự kiện nằm rải rác ở nhiều tài liệu khác nhau (multi-hop reasoning) để tổng hợp thành một ngữ cảnh có cấu trúc chặt chẽ trước khi gửi cho LLM.

---

## 2. PHẦN 2: KẾT QUẢ ĐÁNH GIÁ & SO SÁNH (EVALUATION)

Dựa trên kết quả thực tế thu được trong file [evaluation_results.txt](file:///d:/LAB/Day19-2A202600793-DoVanCung/evaluation_results.txt), dưới đây là phân tích chi tiết hiệu năng giữa **Flat RAG** và **GraphRAG** trên 5 câu hỏi kiểm thử:

### Câu 1: Who are the founders of OpenAI and in what year was it established?
*   **Kết quả:** Cả hai hệ thống đều thông báo **không tìm thấy thông tin này** trong tài liệu của tập dữ liệu gốc (Tech Company Corpus) và sử dụng tri thức nền (General Knowledge) để cung cấp câu trả lời chính xác (Sam Altman, Elon Musk... thành lập năm 2015).
*   **Đánh giá:** Điều này cho thấy khả năng nhận diện ranh giới tri thức tốt của cả hai phương pháp khi không bị ảo tưởng (hallucination) dữ liệu từ các văn bản phi liên quan.

### Câu 2: How does the Q1 2024 U.S. sales growth of Tesla compare to Cadillac and Mercedes-Benz?
*   **Flat RAG:** Truy xuất tài liệu văn bản thô và trích xuất thông tin doanh số Tesla giảm 13.3%, đồng thời Cadillac và Mercedes-Benz nằm trong nhóm các hãng tăng trưởng trên 50%.
*   **GraphRAG:** Truy xuất đồ thị và đưa ra các mối quan hệ trực quan, có số liệu rất cụ thể:
    *   `Cadillac` $\rightarrow$ `EV_SALES_GROWTH` $\rightarrow$ `499.2%`
    *   `Mercedes` $\rightarrow$ `EV_SALES_GROWTH` $\rightarrow$ `66.9%`
    *   `Tesla` $\rightarrow$ `EXPERIENCED_DECLINE` / `Negative growth`
*   **Đánh giá:** GraphRAG vượt trội trong việc tổng hợp các số liệu so sánh trực tiếp từ các node quan hệ, giúp LLM đưa ra câu trả lời gọn gàng, so sánh trực diện thay vì phải tự trích lọc số liệu từ văn bản thô dài dòng.

### Câu 3: What are the main factors that impact electric vehicle battery life, and what is the typical battery warranty length?
*   **Flat RAG:** Thành công tìm được thông tin chi tiết trong các đoạn văn bản thô về tác động khí hậu (longevity 12-15 năm ở ôn đới, 8-12 năm ở khí hậu khắc nghiệt), chu kỳ sạc, và bảo hành tiêu chuẩn 8 năm hoặc 100,000 dặm.
*   **GraphRAG:** Đồ thị tri thức không lưu trữ các chi tiết kỹ thuật mô tả vụn vặt này nên không có thông tin trực tiếp từ đồ thị, hệ thống tự động fallback qua tri thức nền (General Knowledge) để trả lời đầy đủ về nhiệt độ, chu kỳ sạc, BMS và quy định bảo hành 8 năm/100,000 dặm ở Mỹ.
*   **Đánh giá:** Flat RAG ưu thế hơn khi trả lời các câu hỏi mang tính mô tả kỹ thuật chi tiết (fine-grained technical descriptions) do văn bản gốc chứa đầy đủ các chi tiết này, trong khi đồ thị tri thức chỉ tập trung lưu trữ các quan hệ thực thể mức cao.

### Câu 4: What is the financial performance of VinFast in Q3 2024, and what are their revenue figures?
*   **Flat RAG:** Đọc văn bản thô và trích xuất các thông tin hỗ trợ tài chính từ Vingroup/Chủ tịch Phạm Nhật Vượng (tài trợ VND 50k tỷ, cho vay VND 35k tỷ, chuyển đổi VND 80k tỷ nợ thành cổ phần ưu đãi) và mục tiêu bàn giao 80k xe. Tuy nhiên, Flat RAG báo cáo chính xác là **không tìm thấy số liệu doanh thu cụ thể** trong văn bản.
*   **GraphRAG:** Tìm thấy thực thể `VinFast` và quan hệ `(VinFast, experienced growth, Revenue)` nhưng không có số liệu cụ thể. GraphRAG đã bổ sung bằng tri thức nền bên ngoài về báo cáo tài chính chính thức của VinFast niêm yết trên Nasdaq (doanh thu Q3 2024 đạt khoảng 445 triệu USD).
*   **Đánh giá:** GraphRAG kết hợp hiệu quả thông tin định tính trong đồ thị và thông tin định lượng từ tri thức nền để đưa ra câu trả lời đầy đủ hơn khi tập dữ liệu bị thiếu hụt thông tin.

### Câu 5: How do Zero Emission Vehicle (ZEV) regulations in the US impact electric vehicle model availability and market share?
*   **Flat RAG:** Trích xuất xuất sắc các số liệu thống kê cụ thể trong tài liệu: bang áp dụng ZEV đạt 5% thị phần EV so với 1.3% ở các bang khác, chiếm 2/3 tổng doanh số EV tại Mỹ năm 2020 và tăng ít nhất 13 mẫu xe sẵn có.
*   **GraphRAG:** Đồ thị tri thức không có liên kết trực tiếp giữa node ZEV với thị phần và số lượng dòng xe, chỉ có các thông tin ngữ cảnh phụ (California quản lý EV, đạo luật IRA tác động ngành EV, thị phần Tesla 51.3%-55%). GraphRAG sử dụng tri thức nền để giải thích cơ chế tác động của ZEV bắt buộc các hãng xe tăng cung cấp dòng xe mới để tránh phạt.
*   **Đánh giá:** Flat RAG trả lời chính xác số liệu thực nghiệm trong văn bản gốc. GraphRAG có khả năng khái quát hóa tốt nhưng thiếu số liệu thống kê chi tiết do các số liệu này khó biểu diễn một cách tự nhiên dưới dạng quan hệ chủ-vị trên đồ thị.

---

## 3. KẾT LUẬN

1.  **Flat RAG** cực kỳ mạnh mẽ đối với các câu hỏi tra cứu chi tiết kỹ thuật, số liệu thống kê hoặc thông tin định lượng nằm tập trung trong một hoặc vài đoạn văn bản cụ thể.
2.  **GraphRAG** vượt trội khi thực hiện các truy vấn so sánh đa thực thể (multi-entity comparison), xâu chuỗi quan hệ đa bước (multi-hop reasoning) và khi cần tổng hợp thông tin có tính cấu trúc.
3.  **Sự kết hợp hoàn hảo:** Hệ thống RAG thực tế nên sử dụng cơ chế lai (Hybrid RAG) kết hợp cả Vector Search (Flat RAG) cho thông tin chi tiết và Knowledge Graph (GraphRAG) cho thông tin cấu trúc/mối quan hệ để đạt hiệu quả tối ưu nhất.
