# Design Template

## Problem

Hệ thống cần xử lý các truy vấn nghiên cứu chuyên sâu, phức tạp (ví dụ: nghiên cứu công nghệ GraphRAG mới nhất và viết tóm tắt). Hệ thống phải tự động tìm kiếm thông tin từ môi trường mạng, tóm tắt các phát hiện thực tế, phân tích các góc nhìn đối lập hoặc điểm hạn chế, thẩm định chéo độ chính xác của tài liệu để tránh ảo giác, và cuối cùng tổng hợp thành một bài báo cáo có cấu trúc mạch lạc kèm trích dẫn nguồn chi tiết.

## Why multi-agent?

Mô hình Single-Agent RAG truyền thống thường gặp các hạn chế sau đối với tác vụ nghiên cứu chuyên sâu:
1. **Quá tải ngữ cảnh (Context Overload)**: Agent đơn phải xử lý đồng thời việc tìm kiếm nguồn, đọc hiểu, phân tích phản biện và viết báo cáo, dễ dẫn đến bỏ sót chi tiết quan trọng.
2. **Ảo giác (Hallucination)**: Thiếu bước thẩm định chéo độc lập khiến agent dễ tự bịa ra thông tin mà không có nguồn đối chiếu.
3. **Thiếu tính phản biện**: Khó có được góc nhìn đa chiều (so sánh ưu/nhược điểm) khi một agent tự viết và tự duyệt.

Hệ thống **Multi-Agent** phân chia các công đoạn cho 5 Agent chuyên biệt, hoạt động độc lập giúp cải thiện chất lượng thông tin, tăng khả năng kiểm soát lỗi và đảm bảo tính khách quan của báo cáo.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| **Supervisor** | Điều phối toàn bộ workflow, lựa chọn Agent tiếp theo cần chạy hoặc dừng hệ thống khi hoàn thành. | Lịch sử route, trạng thái thông tin hiện tại trong state. | Tên Agent tiếp theo (researcher, analyst, critic, writer, done). | Chọn sai Agent tiếp theo hoặc rơi vào vòng lặp vô hạn (khắc phục bằng hard iteration limit). |
| **Researcher** | Gọi Search Client thu thập dữ liệu nguồn và tổng hợp thành ghi chú thô kèm trích dẫn. | `request.query`, `max_sources`. | `sources` (list), `research_notes`. | Không tìm được nguồn phù hợp hoặc tóm tắt sơ sài. |
| **Analyst** | Phân tích sâu các ghi chú thô, trích xuất luận điểm cốt lõi, so sánh ưu/nhược điểm và chỉ ra lỗ hổng bằng chứng. | `research_notes`. | `analysis_notes`. | Phân tích phiến diện hoặc bỏ sót thông tin quan trọng. |
| **Critic** | Kiểm tra chéo chất lượng phân tích so với nguồn tài liệu gốc, kiểm định trích dẫn nguồn, phát hiện ảo giác. | `research_notes`, `analysis_notes`, `sources`. | `critic_feedback`. | Bỏ sót lỗi logic hoặc phê bình không mang tính đóng góp xây dựng. |
| **Writer** | Tổng hợp toàn bộ thông tin từ ghi chú, phân tích và phản hồi phê bình thành báo cáo Markdown hoàn chỉnh cho độc giả mục tiêu. | `research_notes`, `analysis_notes`, `critic_feedback`, `request.audience`. | `final_answer`. | Trình bày thiếu mạch lạc hoặc quên ghi nhận nguồn trích dẫn. |

## Shared state

Hệ thống sử dụng một class `ResearchState` dùng chung để lưu giữ toàn bộ ngữ cảnh trao đổi giữa các Agent:
- `request`: Thông tin truy vấn ban đầu của người dùng (giữ nguyên làm mục tiêu).
- `iteration`: Số lần di chuyển giữa các Agent để Supervisor kiểm soát giới hạn.
- `route_history`: Nhật ký các Agent đã chạy giúp debug và định hướng tiếp theo.
- `sources`: Tài liệu gốc thu thập được, đóng vai trò làm "single source of truth".
- `research_notes`: Ghi chú thô của Researcher.
- `analysis_notes`: Phân tích chuyên sâu của Analyst.
- `critic_feedback`: Ý kiến kiểm định chất lượng của Critic.
- `final_answer`: Báo cáo hoàn chỉnh cuối cùng của Writer.
- `agent_results`: Kết quả chi tiết của từng Agent kèm token/cost phục vụ đo đạc benchmark.
- `trace`: Nhật ký trace span phục vụ observability.

## Routing policy

Supervisor điều phối đồ thị LangGraph dưới dạng star-architecture:
1. `Supervisor` kiểm tra state -> Nhận diện thông tin còn thiếu -> Gọi Agent tương ứng.
2. Agent (Researcher/Analyst/Critic/Writer) xử lý xong -> Trả quyền điều khiển lại cho `Supervisor`.
3. Sơ đồ định tuyến tuần tự mặc định:
   `Supervisor` -> `Researcher` -> `Supervisor` -> `Analyst` -> `Supervisor` -> `Critic` -> `Supervisor` -> `Writer` -> `Supervisor` -> `done` (END).
4. Nếu Critic phát hiện lỗi nghiêm trọng, Supervisor có thể định tuyến lại cho Researcher hoặc Analyst để bổ sung thông tin.

## Guardrails

- **Max iterations**: Giới hạn cứng tối đa 6 bước điều phối để phòng ngừa vòng lặp vô hạn giữa Critic và các Worker Agent.
- **Timeout**: Thiết lập thời gian chờ tối đa 60 giây đối với các tác vụ chạy ngầm để tránh nghẽn luồng.
- **Retry**: Sử dụng `tenacity` để tự động gọi lại (retry) 3 lần đối với các lỗi kết nối LLM API hoặc lỗi mạng.
- **Fallback**: Cơ chế định tuyến dự phòng (Rule-based routing fallback) tự động kích hoạt khi Supervisor Agent gặp lỗi gọi LLM hoặc trả về sai định dạng.
- **Validation**: Đảm bảo câu trả lời cuối cùng phải chứa các thẻ trích dẫn dạng `[Source X]`, nếu không sẽ cảnh báo hoặc chạy lại Writer Agent.

## Benchmark plan

- **Test Query**: `"Research GraphRAG state-of-the-art and write a 500-word summary"`
- **Metrics**:
  1. *Latency*: Đo bằng wall-clock time của toàn bộ tiến trình chạy (giây).
  2. *Cost*: Tính toán dựa trên lượng token thực tế tiêu thụ từ API (USD).
  3. *Quality*: Sử dụng LLM-as-a-judge chấm điểm trên thang từ 0-10 điểm dựa trên tính sâu sắc và độ chính xác của bài viết.
  4. *Citation Coverage*: Tỉ lệ phần trăm các tài liệu nguồn thực tế được trích dẫn trong bài viết cuối cùng.
- **Expected Outcome**: Mô hình đa Agent (Multi-Agent) dự kiến đạt điểm chất lượng và độ phủ trích dẫn cao hơn rõ rệt so với Single-Agent Baseline, đổi lại độ trễ và chi phí token sẽ cao hơn.

