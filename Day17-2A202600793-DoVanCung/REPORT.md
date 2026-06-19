# Báo cáo kết quả Lab 17 - Memory Systems for AI Agent

## 1. Kết quả Benchmark

Dưới đây là kết quả đo lường hiệu năng của hai Agent (**Baseline** và **Advanced**) trên cả hai bộ thử nghiệm: Standard Benchmark (10 phiên hội thoại thông thường) và Long-Context Stress Benchmark (hội thoại stress test dài).

### Standard Benchmark (10 Sessions)

| Agent | Agent tokens only | Prompt tokens processed | Cross-session recall | Response quality | Memory growth (bytes) | Compactions |
|---|---:|---:|---:|---:|---:|---:|
| **Baseline** | 3120 | 22398 | 0.00 | 0.10 | 0 | 0 |
| **Advanced** | 2162 | 25051 | 0.61 | 0.65 | 375 | 0 |

### Long-Context Stress Benchmark

| Agent | Agent tokens only | Prompt tokens processed | Cross-session recall | Response quality | Memory growth (bytes) | Compactions |
|---|---:|---:|---:|---:|---:|---:|
| **Baseline** | 407 | 24193 | 0.00 | 0.10 | 0 | 0 |
| **Advanced** | 819 | 20078 | 0.83 | 0.87 | 251 | 1 |

---

## 2. Phân tích & Giải thích Trade-off

### 2.1. Tại sao Advanced Agent có khả năng Recall vượt trội so với Baseline?
* **Baseline Agent:** Chỉ có short-term memory lưu trữ cục bộ trong nội bộ mỗi thread (`SessionState`). Khi bắt đầu một recall question ở một thread mới (`-recall-X`), baseline hoàn toàn không có thông tin từ các phiên làm việc trước đó, dẫn đến việc recall bằng **0.00**.
* **Advanced Agent:** Sở hữu lớp **Persistent Memory** lưu dưới dạng file vật lý `User.md` thông qua `UserProfileStore`. Mọi thông tin cập nhật hợp lệ từ các thread trước đều được trích xuất và lưu trữ ổn định. Khi sang thread mới, Agent đọc trực tiếp từ `User.md` để tái dựng lại thông tin của người dùng nên độ chính xác tăng vượt trội (recall từ **0.61** đến **0.83**).

### 2.2. So sánh chi phí Token ở hội thoại ngắn và hội thoại dài
* **Hội thoại ngắn (Standard):** Ở môi trường Standard với các thread tương đối ngắn, Advanced Agent tiêu thụ prompt tokens nhiều hơn một chút so với Baseline (25051 so với 22398). Lý do là vì Advanced luôn phải đính kèm thông tin profile dài hạn từ `User.md` vào prompt context ở mỗi lượt hội thoại để cá nhân hóa câu trả lời. Điều này tạo ra một khoản chi phí cố định (fixed cost) ở các lượt đầu.
* **Hội thoại dài (Stress Test):** Khi hội thoại kéo dài (Stress Benchmark), tổng số prompt tokens của Baseline tăng vọt lên **24193** do phải mang theo toàn bộ lịch sử thô chưa nén. Trong khi đó, Advanced Agent kích hoạt cơ chế **Compact Memory**, tiến hành tóm tắt các hội thoại cũ (`Compactions = 1`) và chỉ giữ lại các message gần nhất cùng file tóm tắt. Nhờ vậy, prompt tokens của Advanced được kéo giảm xuống chỉ còn **20078** (tiết kiệm khoảng **17%** so với Baseline) mà vẫn đảm bảo recall cao nhờ `User.md`.

### 2.3. Cách Compact Memory tối ưu `prompt tokens processed`
* Thay vì liên tục đẩy toàn bộ lịch sử trò chuyện dài dòng vào LLM ở mỗi turn, `CompactMemoryManager` kiểm tra ngưỡng token (`compact_threshold_tokens`).
* Khi vượt ngưỡng, các message cũ được chuyển vào hàm `summarize_messages()` để tạo ra một đoạn summary ngắn gọn, súc tích và xóa bỏ các message cũ đó khỏi bộ nhớ ngắn hạn của thread, chỉ giữ lại `keep_messages` lượt chat gần nhất.
* Nhờ vậy, compact memory chủ yếu tối ưu hóa phần **Prompt Context** (đầu vào của LLM) giúp giảm tốc độ tăng trưởng token theo hàm số mũ của hội thoại dài, ngăn chặn lỗi tràn ngữ cảnh (context overflow).

### 2.4. Tốc độ tăng trưởng bộ nhớ (Memory Growth) và Rủi ro hệ thống
* **Memory Growth:** Advanced Agent lưu trữ facts vào file Markdown cá nhân. Sau Standard Benchmark, file phình thêm **375 bytes** và sau Stress Test tăng thêm **251 bytes**. Tốc độ phình này là tuyến tính theo số lượng thông tin mới được cung cấp.
* **Rủi ro đi kèm:**
  1. **Lưu sai thông tin (False Facts/Noise):** Nếu không có cơ chế lọc, các câu đùa hoặc thông tin giả lập (ví dụ: "chuyển sang làm product manager") có thể bị lưu đè lên thông tin thật.
  2. **Tràn dung lượng & Chi phí đọc/ghi:** Khi số lượng người dùng lên tới hàng triệu, việc quản lý hàng triệu file `.md` nhỏ lẻ sẽ gây áp lực lên hệ thống I/O của server.
  3. **Mâu thuẫn thông tin (Conflict Accumulation):** Thông tin cũ không được dọn dẹp hoặc cập nhật đúng có thể gây nhiễu cho câu trả lời của agent.

---

## 3. Các tính năng mở rộng (Bonus) đã cài đặt

Bài làm đã triển khai thành công 2 tính năng bonus quan trọng để cải thiện độ chính xác và an toàn của hệ thống memory:

1. **Conflict Handling (Xử lý mâu thuẫn & Đính chính):**
   * Trong `UserProfileStore.upsert_fact()`, khi người dùng đính chính thông tin (ví dụ chuyển từ Đà Nẵng sang Huế, hoặc backend sang MLOps), hệ thống sẽ đọc facts cũ ra dưới dạng dictionary, ghi đè giá trị mới lên key tương ứng và lưu đè lại file `User.md`. Fact cũ bị loại bỏ hoàn toàn, ngăn chặn việc agent trả lời lẫn lộn cả hai địa điểm/nghề nghiệp.
2. **Confidence Threshold & Noise Filter (Lọc nhiễu hội thoại):**
   * `_should_skip_as_question()` lọc các câu hỏi có chứa dấu hỏi `?` hoặc các từ khóa nghi vấn để ngăn chặn việc người dùng hỏi thông tin (ví dụ: "Mình tên gì?") bị nhận nhầm thành thông tin cá nhân mới và lưu vào profile.
   * `extract_profile_updates()` sử dụng các biểu thức chính quy (Regex) kết hợp các điều kiện phủ định để bỏ qua các câu đùa nhiễu (ví dụ: `"không còn làm backend"`, `"không còn ở đà nẵng"`, hay `"ví dụ cũ"`) để chỉ lưu trữ các fact thực sự ổn định.
