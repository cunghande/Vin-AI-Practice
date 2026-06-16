# Evidence Pack - Learning OS Knowledge Intake Agent

## 1. Nhóm và track

**Track:** A - Learning OS

**Product/app thật để soi:** LMS hiện tại, Discord lớp, repo lab, slide/README/rubric của AI in Action

**Build slice đang nghĩ:** Agent nhận câu hỏi mơ hồ của học viên, hỏi thêm nếu thiếu context, tìm trong tài liệu đã nạp, rồi trả về checklist/source-grounded answer. Nếu không có nguồn, agent nói không biết và draft câu hỏi gửi mentor/TA.

## 2. Self-use Evidence

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Day05 có nhiều nguồn rời rạc: slide, GitHub repo, screenshot, hướng dẫn trên lớp. | Screenshot slide / repo Day05 | Low-confidence | User dễ hỏi mơ hồ kiểu "bài này làm gì" vì không biết nguồn nào là chính. |
| README Day05 tách rõ `01-invidual-workshop` và `02-group-spec`. | GitHub repo Day05 | Happy / Correction | Agent cần phân biệt câu hỏi cá nhân hay nhóm trước khi trả lời. |
| Slide yêu cầu cuối Day05 phải có evidence, slice, decision, failure path, owner. | Screenshot gate checklist | Program Operations | Agent có thể tổng hợp deliverable thành checklist nếu có nguồn. |
| Nếu không có update mới như deadline hoặc rule đổi, AI dễ đoán sai. | Domain observation | No-source / Unknown | Agent phải nói không tìm thấy trong tài liệu đã nạp thay vì đoán. |

## 3. User / Review / Social Evidence

| Quote / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| "Day05 rốt cuộc phải nộp file nào?" | Câu hỏi thật trong quá trình làm lab | Học viên AI in Action | User không biết đang hỏi phần cá nhân, nhóm, hay chuẩn bị Day06. |
| "File 01 có liên quan gì tới file 02 không?" | Câu hỏi thật trong quá trình làm lab | Học viên đang đọc repo | User cần agent phân luồng scope trước khi đưa checklist. |
| "Nếu tài liệu không có thông tin đó thì AI có được đoán không?" | Câu hỏi khi thiết kế workflow | Học viên/nhóm làm prototype | Failure mode là AI trả lời không có nguồn, sai deadline/rubric. |

## 4. Evidence -> Insight

```text
Evidence nổi bật nhất:
Lab có nhiều nguồn đúng nhưng phân tán: slide, repo, README, Discord, mentor note.

Insight:
User không chỉ cần "một chatbot trả lời bài học".
User cần một agent biết hỏi lại, xác định câu hỏi thuộc nội dung học hay vận hành chương trình,
rồi chỉ trả lời dựa trên nguồn đã nạp.

Opportunity:
AI có thể giúp bằng cách biến tài liệu lớp thành một Learning OS Knowledge Agent:
hỏi thêm context, retrieve đúng source, tổng hợp checklist, và nói "không biết" khi source thiếu.
```

## 5. Evidence đổi SPEC như thế nào?

- [x] Chọn Track A - Learning OS.
- [x] Chia scope thành Learning Content Support và Program Operations Support.
- [x] Chốt build slice đủ nhỏ: một user hỏi mơ hồ về Day05/Day06, agent hỏi thêm + tìm source + trả checklist.
- [x] Chọn Augmentation, không Automation.
- [x] Thêm failure path: no-source/unknown, wrong-scope, correction.
- [x] Thêm owner plan cho research, SPEC, prototype, test, demo.

```text
Trước evidence, ý tưởng còn dễ thành chatbot chung chung.
Sau khi đọc yêu cầu Day05 và quan sát workflow làm bài, nhóm chốt Learning OS Knowledge Intake Agent.
Lý do: scope này có nguồn thật dễ nạp, pain thật trong lớp, và demo được ask loop + source-grounded refusal trong một prototype nhỏ.
```
