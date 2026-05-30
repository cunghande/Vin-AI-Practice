# 01 - Individual Problem Scan

## Bảng Scan Problems

| # | Lăng kính | Problem quan sát được | Ai đang đau? | Dấu hiệu thật |
|---:|---|---|---|---|
| 1 | Tốn thời gian | Tổng hợp tài liệu ôn thi từ nhiều nguồn | Sinh viên | Mất 2-3 giờ trước mỗi kỳ thi để gom slide, PDF, đề cương và ghi chú |
| 2 | AI có thể tốt hơn | Đọc paper AI để lấy ý chính | Sinh viên AI | Mất 20-30 phút cho mỗi paper, dễ bỏ sót methodology hoặc limitation |
| 3 | Lặp lại | Tìm lại thông tin trong Discord/Zalo lớp | Sinh viên | Mất 10-15 phút mỗi lần tìm deadline, link nộp bài hoặc câu trả lời cũ |
| 4 | Pain từ người khác | Thành viên nhóm không nắm được tiến độ đồ án | Nhóm đồ án | Thành viên hỏi lại nhiều lần về việc ai đang làm gì, việc nào đã xong |
| 5 | Tốn thời gian | Viết báo cáo môn học | Sinh viên | Phải sửa nhiều lần về format, cấu trúc và nội dung |
| 6 | Lặp lại | Theo dõi deadline nhiều môn học | Sinh viên | Deadline nằm rải rác ở LMS, Zalo, email; dễ quên hạn hoặc nộp sát hạn |
| 7 | AI có thể tốt hơn | Tìm đề tài nghiên cứu phù hợp | Sinh viên AI | Mất nhiều thời gian tìm paper, so sánh độ khó và mức độ phù hợp |
| 8 | Pain từ người khác | Người mới khó hiểu hệ thống đồ án | Thành viên mới | Phải giải thích lại kiến trúc, cách chạy project và quy ước nhóm |

## Top 3 Problems

| Rank | Problem | Vì sao chọn | Điều còn chưa chắc |
|---:|---|---|---|
| 1 | Tổng hợp tài liệu ôn thi | Pain thật, xảy ra trước mỗi kỳ thi, tốn nhiều thời gian và có thể đo bằng thời gian tạo outline ôn tập | Chất lượng tóm tắt của AI và khả năng bỏ sót kiến thức quan trọng |
| 2 | Tìm lại thông tin Discord/Zalo | Nhiều sinh viên gặp, workflow rõ và impact đo được bằng thời gian tìm kiếm | Khó lấy dữ liệu từ Zalo/Discord và cần xử lý quyền riêng tư |
| 3 | Theo dõi deadline môn học | Dễ đo hiệu quả, liên quan trực tiếp đến việc nộp bài đúng hạn | Có thể chỉ cần Rule/Calendar, không nhất thiết cần AI |

---

## Problem Card #1 - Tổng hợp tài liệu ôn thi

### Problem 1 câu

Sinh viên mất nhiều thời gian tổng hợp tài liệu ôn thi từ nhiều nguồn khác nhau trước kỳ thi.

### Actor

Sinh viên đại học.

### Thời điểm / bối cảnh

Trước kỳ thi giữa kỳ hoặc cuối kỳ, khi sinh viên cần gom slide bài giảng, PDF tham khảo, đề cương môn học và ghi chú cũ để tạo tài liệu ôn tập.

### Current Workflow

| Bước | Actor | Input | Output | Thời gian |
|---:|---|---|---|---|
| 1 | Sinh viên | Slide bài giảng | Danh sách slide cần đọc | 10 phút |
| 2 | Sinh viên | PDF tham khảo | Tài liệu tham khảo liên quan | 15 phút |
| 3 | Sinh viên | Đề cương môn học | Các chủ đề cần ôn | 5 phút |
| 4 | Sinh viên | Tất cả tài liệu | Ghi chú tạm | 90 phút |
| 5 | Sinh viên | Ghi chú tạm | Tài liệu ôn tập ban đầu | 30 phút |

### Current Workflow Diagram

```text
[Slide]
   \
    \
     > [Đọc tài liệu] ---> [Ghi chú tạm] ---> [Tài liệu ôn tập]
    /
   /
[PDF]

[Đề cương] ---------------^
```

### Bottleneck

Đọc, lọc ý chính và tổng hợp tài liệu mất khoảng 120 phút.

### Impact

Sinh viên tốn nhiều thời gian trước kỳ thi, dễ bỏ sót kiến thức quan trọng hoặc tạo tài liệu ôn tập thiếu cấu trúc.

### Success Metric

Giảm thời gian tạo bản nháp outline ôn tập từ khoảng 3 giờ xuống dưới 30 phút. Sinh viên vẫn phải review nội dung trước khi dùng để học.

### Non-AI Alternative

Dùng template ghi chú và checklist ôn tập theo từng môn.

### AI Hypothesis

AI hỗ trợ tóm tắt slide/PDF/đề cương, gom ý trùng nhau, tạo outline ôn tập và đánh dấu phần cần sinh viên kiểm tra lại.

### Quick Gut

Workflow.

### Future Workflow

```text
[Slide + PDF + Đề cương]
            |
            v
      [AI tóm tắt]
            |
            v
    [AI tạo outline]
            |
            v
   [Sinh viên review]
            |
            v
 [Tài liệu ôn tập đã kiểm tra]
```

### Human Boundary

Sinh viên phải kiểm tra lại nội dung, đối chiếu với đề cương và slide gốc trước khi học hoặc chia sẻ cho người khác.

---

## Problem Card #2 - Tìm lại thông tin Discord/Zalo lớp

### Problem 1 câu

Sinh viên mất nhiều thời gian tìm lại thông tin cũ trong Discord hoặc Zalo lớp.

### Actor

Sinh viên.

### Thời điểm / bối cảnh

Khi cần tìm lại deadline, link nộp bài, file tài liệu, quyết định của nhóm/lớp hoặc câu trả lời cũ trong các kênh chat.

### Current Workflow

```text
[Mở Discord/Zalo]
        |
        v
  [Search từ khóa]
        |
        v
[Đọc nhiều tin nhắn]
        |
        v
[Tìm được thông tin]
```

### Bottleneck

Phải đọc lại nhiều tin nhắn, thử nhiều từ khóa khác nhau và dễ bỏ sót thông tin nếu không nhớ đúng cách người khác đã viết.

### Impact

Mỗi lần tìm mất 10-15 phút; nếu tìm sai hoặc không thấy có thể nộp bài muộn, hỏi lại bạn cùng lớp hoặc làm theo thông tin cũ.

### Success Metric

Giảm thời gian tìm thông tin từ 10-15 phút xuống dưới 1 phút, kết quả trả về phải kèm nguồn/tin nhắn gốc để người dùng xác nhận.

### Non-AI Alternative

Pin các thông tin quan trọng, tạo FAQ hoặc document tổng hợp link/deadline.

### AI Hypothesis

Semantic search giúp sinh viên hỏi bằng ngôn ngữ tự nhiên và trả về thông tin liên quan kèm link/tin nhắn gốc.

### Quick Gut

Workflow.

### Future Workflow

```text
[Nhập câu hỏi]
       |
       v
[AI semantic search]
       |
       v
[Trả kết quả + nguồn]
       |
       v
[Người dùng xác nhận]
```

### Human Boundary

Người dùng cần kiểm tra nguồn gốc vì AI có thể lấy nhầm tin nhắn cũ, sai ngữ cảnh hoặc bỏ sót thông báo mới hơn.

---

## Problem Card #3 - Theo dõi deadline môn học

### Problem 1 câu

Sinh viên gặp khó khăn khi theo dõi deadline của nhiều môn học cùng lúc.

### Actor

Sinh viên.

### Thời điểm / bối cảnh

Trong học kỳ, khi deadline bài tập, quiz, project và báo cáo được thông báo ở nhiều nơi như LMS, email, Zalo lớp hoặc lời nhắc của giảng viên.

### Current Workflow

```text
[LMS]
   |
   v
[Zalo lớp]
   |
   v
[Email]
   |
   v
[Ghi chú thủ công]
   |
   v
[Theo dõi deadline]
```

### Bottleneck

Thông tin deadline nằm ở nhiều nơi, sinh viên phải tự kiểm tra và ghi lại thủ công.

### Impact

Sinh viên dễ quên deadline, nộp sát hạn hoặc bỏ sót yêu cầu nhỏ trong thông báo.

### Success Metric

100% deadline được ghi vào calendar trong vòng 24 giờ sau khi được thông báo. Nhắc trước hạn 3 ngày và 1 ngày. Số lần quên deadline trong một học kỳ giảm từ 2-3 lần xuống 0 lần.

### Non-AI Alternative

Google Calendar, checklist theo môn và reminder lặp lại.

### AI Hypothesis

AI có thể đọc thông báo từ nhiều nguồn, nhận diện deadline, trích xuất tên môn, yêu cầu nộp bài và đề xuất lịch nhắc.

### Quick Gut

Rule.

### Future Workflow

```text
[LMS + Email + Zalo]
          |
          v
[Tổng hợp deadline]
          |
          v
[Calendar tập trung]
          |
          v
[Nhắc trước hạn]
          |
          v
[Hoàn thành bài tập]
```

### Human Boundary

Sinh viên cần xác nhận deadline trước khi thêm vào calendar, đặc biệt khi thông báo bị sửa hoặc có nhiều mốc nộp bài khác nhau.

---

## Card muốn pitch nhất

### Card tôi muốn pitch nhất

Problem Card #1 - Tổng hợp tài liệu ôn thi từ nhiều nguồn.

### Vì sao

Đây là pain thật của sinh viên trước mỗi kỳ thi, xảy ra lặp lại ở nhiều môn, tốn nhiều thời gian và có thể đo được bằng thời gian chuẩn bị tài liệu ôn tập. Bài này cũng phù hợp để so sánh giữa template ghi chú, workflow hỗ trợ và AI tóm tắt.

### Câu hỏi tôi muốn nhóm challenge

- AI tóm tắt có làm mất hoặc hiểu sai kiến thức quan trọng không?
- Làm sao kiểm tra chất lượng outline ôn tập?
- Bài này nên dùng AI ở mức Workflow hay chỉ cần template + checklist?
