# Thin SPEC - Learning OS Knowledge Intake Agent

## 1. Track, product/app và user

**Track:** A - Learning OS

**Product/app thật:** LMS hiện tại, Discord lớp, GitHub repo lab, slide/README/rubric của AI in Action

**User cụ thể:** Học viên AI in Action đang hỏi mơ hồ về nội dung bài học, bài lab, deadline, nộp repo, làm nhóm/cá nhân, hoặc chuẩn bị prototype

**Nhóm có phải user thật không?** Có. Nhóm đang trực tiếp gặp pain này khi đọc Day05/Day06 và phân biệt file `01` với `02`.

## 2. Scope

| Scope | Bao gồm | Không bao gồm |
|---|---|---|
| Learning Content Support | Giải thích khái niệm, lab, rubric, ví dụ, cách làm bài. | Không tự chấm điểm cuối cùng. |
| Program Operations Support | Lịch, deadline, nộp repo, cá nhân/nhóm, demo, owner plan. | Không đoán rule nếu tài liệu không có. |

## 3. Evidence Summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Day05 README tách `01-invidual-workshop` và `02-group-spec`. | GitHub repo Day05 | User dễ nhầm bài cá nhân và phần nhóm. | Agent phải hỏi scope trước khi trả lời. |
| Slide Day05 yêu cầu evidence, slice, decision, failure path, owner. | Screenshot slide | User cần checklist deliverable, không chỉ giải thích chung. | Output phải có checklist + missing info. |
| Tài liệu lớp nằm ở nhiều nơi: slide, repo, Discord, mentor note. | Self-use observation | User không biết nguồn nào là source of truth. | Agent phải source-grounded và nêu source status. |
| Có câu hỏi không có trong source hoặc source có thể đổi. | Domain observation | AI đoán có thể làm sai deadline/rubric. | Thêm no-source/unknown path. |

## 4. Pain Statement

```text
Học viên AI in Action đang gặp khó khi hỏi về bài học hoặc cách vận hành chương trình,
vì thông tin nằm rải rác ở slide, repo, README, Discord và mentor note,
dẫn tới user không biết câu hỏi thuộc nội dung học hay rule vận hành, không biết nguồn nào là đúng,
và dễ làm sai deliverable nếu AI trả lời bằng suy đoán.
```

## 5. Build slice

```text
Cho một học viên hỏi mơ hồ "Day05 phải làm gì?",
prototype dùng AI để hỏi thêm nếu thiếu context, phân loại câu hỏi thành Learning Content hoặc Program Operations,
tìm trong knowledge pack đã nạp, rồi tạo source-grounded answer gồm summary, checklist, missing info, source status,
và xử lý failure mode "không có nguồn hoặc sai scope" bằng ask loop, no-source/unknown response, correction loop, và draft câu hỏi gửi mentor/TA.
```

## 6. Agent Workflow

```text
Understand question
  -> Decide scope: Learning Content / Program Operations / Ambiguous
  -> Ask loop nếu thiếu context
  -> Retrieve source trong knowledge pack
  -> Synthesize nếu có nguồn
  -> Refuse/Unknown nếu không có nguồn hoặc source outdated
  -> Correction loop nếu user sửa scope/day/context
```

## 7. Output Contract

Prototype luôn phải có:

- Detected scope
- Source status
- Answer summary
- Action checklist
- Missing info
- Refusal/unknown note nếu thiếu nguồn

## 8. Auto/Aug decision

- [x] **Augmentation:** AI hỏi, tìm nguồn, tổng hợp, tạo checklist.
- [ ] Conditional automation
- [ ] Automation

**Lý do chọn:** AI không nên tự quyết định rule/deadline/nộp bài thay user. AI chỉ hỗ trợ hiểu tài liệu và chuẩn bị next step; user/mentor vẫn xác nhận cuối.

**Human role:** learner, verifier, corrector, mentor/TA khi source thiếu hoặc mâu thuẫn.

## 9. Four Paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | User hỏi "Day05 phần group spec cần gì?" -> agent tìm source và xuất checklist. |
| Low-confidence | User hỏi "bài này làm sao?" -> agent hỏi day, scope, cá nhân/nhóm, output mong muốn. |
| No-source / Unknown | User hỏi "deadline đổi chưa?" nhưng knowledge pack không có update -> agent không đoán, draft câu hỏi gửi mentor/Discord. |
| Correction | User sửa "không phải Day05, là Day06 prototype" -> agent update memory và đổi checklist. |
| Wrong-scope recovery | User hỏi khái niệm rồi chuyển sang hỏi cách nộp -> agent chuyển scope từ Learning Content sang Program Operations. |

## 10. Failure mode nguy hiểm nhất

```text
Nếu user hỏi một câu mơ hồ về bài lab hoặc deadline,
AI có thể đoán sai scope hoặc trả lời không có nguồn,
hậu quả là user làm sai file, thiếu evidence, nộp sai cấu trúc repo, hoặc mất thời gian hỏi lại.
Prototype xử lý bằng ask loop, source status, no-source/unknown response, correction loop, và draft câu hỏi gửi mentor/TA.
```

## 11. Owner plan cho Day06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| Phúc | Research / evidence | Screenshot slide, README Day05, quote câu hỏi mơ hồ |
| Tuấn Anh | SPEC | `evidence-pack.md`, `workflow.md`, `thin-spec.md` |
| Vũ Anh | Prototype | `prototype/index.html`, `styles.css`, `app.js` |
| Cung | Test / failure path | Test happy, low-confidence, no-source/unknown, correction, wrong-scope |
| Phúc | Demo script / repo | README hoặc demo notes |
