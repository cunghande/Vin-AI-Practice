# Ngày 1 - Bài Tập & Phản Ánh
## Nền Tảng LLM API | Phiếu Thực Hành

**Thời lượng:** 1:30 giờ  
**Cấu trúc:** Lập trình cốt lõi (60 phút) -> Bài tập mở rộng (30 phút)

---

## Phần 1 - Lập Trình Cốt Lõi (0:00-1:00)

Đã triển khai các TODO trong `solution.py`:

- `call_openai`
- `call_openai_mini`
- `compare_models`
- `streaming_chatbot`
- `retry_with_backoff`
- `batch_compare`
- `format_comparison_table`

Kết quả kiểm thử:

```bash
python -m pytest tests/ -v
```

Kết quả: 19 tests passed.

GitHub: https://github.com/cunghande

---

## Phần 2 - Bài Tập Mở Rộng (1:00-1:30)

### Bài tập 2.1 - Độ Nhạy Của Temperature

Gọi `call_openai` với các giá trị temperature 0.0, 0.5, 1.0 và 1.5 sử dụng prompt **"Hãy kể cho tôi một sự thật thú vị về Việt Nam."**

**Bạn nhận thấy quy luật gì qua bốn phản hồi?** (2-3 câu)
> Khi temperature thấp, đặc biệt là 0.0, câu trả lời thường ổn định, ngắn gọn và ít thay đổi giữa các lần gọi. Khi temperature tăng lên 1.0 hoặc 1.5, câu trả lời có xu hướng sáng tạo hơn, cách diễn đạt phong phú hơn, nhưng cũng có nguy cơ kém nhất quán hoặc thêm chi tiết không cần thiết. Vì vậy temperature càng cao thì mức độ đa dạng và bất ngờ trong output càng lớn.

**Bạn sẽ đặt temperature bao nhiêu cho chatbot hỗ trợ khách hàng, và tại sao?**
> Tôi sẽ đặt temperature khoảng 0.2 đến 0.5 cho chatbot hỗ trợ khách hàng. Mức này giúp câu trả lời rõ ràng, ổn định và đáng tin cậy, trong khi vẫn đủ linh hoạt để diễn đạt tự nhiên. Với hỗ trợ khách hàng, độ chính xác và tính nhất quán quan trọng hơn sự sáng tạo.

---

### Bài tập 2.2 - Đánh Đổi Chi Phí

Xem xét kịch bản: 10.000 người dùng hoạt động mỗi ngày, mỗi người thực hiện 3 lần gọi API, mỗi lần trung bình ~350 token.

**Ước tính xem GPT-4o đắt hơn GPT-4o-mini bao nhiêu lần cho workload này:**
> Theo đề bài, chi phí output của GPT-4o là 0.010 USD / 1K token, còn GPT-4o-mini là 0.0006 USD / 1K token. Tỉ lệ chi phí là 0.010 / 0.0006 = khoảng 16.67 lần, nghĩa là GPT-4o đắt hơn GPT-4o-mini khoảng 16-17 lần cho cùng số token output. Với 10.000 người dùng x 3 lần gọi x 350 token = 10.500.000 token mỗi ngày, GPT-4o ước tính tốn khoảng 105 USD/ngày, còn GPT-4o-mini khoảng 6.3 USD/ngày.

**Mô tả một trường hợp mà chi phí cao hơn của GPT-4o là xứng đáng, và một trường hợp GPT-4o-mini là lựa chọn tốt hơn:**
> GPT-4o xứng đáng hơn khi tác vụ cần chất lượng lập luận cao, câu trả lời chính xác hơn, xử lý yêu cầu phức tạp hoặc nội dung ảnh hưởng trực tiếp đến trải nghiệm quan trọng của người dùng, ví dụ trợ lý phân tích tài liệu, tư vấn kỹ thuật khó, hoặc tổng hợp thông tin có nhiều ràng buộc. GPT-4o-mini phù hợp hơn cho các tác vụ lặp lại, đơn giản và có số lượng lớn, ví dụ chatbot FAQ, phân loại nội dung, viết câu trả lời ngắn, hoặc hỗ trợ khách hàng mức cơ bản.

---

### Bài tập 2.3 - Trải Nghiệm Người Dùng với Streaming

**Streaming quan trọng nhất trong trường hợp nào, và khi nào thì non-streaming lại phù hợp hơn?** (1 đoạn văn)
> Streaming quan trọng nhất khi câu trả lời dài hoặc người dùng cần cảm giác hệ thống đang phản hồi ngay, ví dụ chatbot hỏi đáp, trợ lý viết nội dung, giải thích từng bước, hoặc các ứng dụng cần trải nghiệm hội thoại tự nhiên. Khi streaming, người dùng không phải chờ đến khi toàn bộ câu trả lời hoàn tất mới thấy kết quả, nên cảm giác độ trễ thấp hơn. Non-streaming phù hợp hơn khi câu trả lời ngắn, cần xử lý trọn gói trước khi hiển thị, cần parse JSON, cần lưu kết quả vào database, hoặc cần đảm bảo output hoàn chỉnh và hợp lệ trước khi trả về cho ứng dụng.

---

## Danh Sách Kiểm Tra Nộp Bài

- [x] Tất cả tests pass: `python -m pytest tests/ -v`
- [x] `call_openai` đã triển khai và kiểm thử
- [x] `call_openai_mini` đã triển khai và kiểm thử
- [x] `compare_models` đã triển khai và kiểm thử
- [x] `streaming_chatbot` đã triển khai và kiểm thử
- [x] `retry_with_backoff` đã triển khai và kiểm thử
- [x] `batch_compare` đã triển khai và kiểm thử
- [x] `format_comparison_table` đã triển khai và kiểm thử
- [x] `exercises.md` đã điền đầy đủ
- [x] Sao chép bài làm vào folder `solution`
