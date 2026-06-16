# Workflow - Learning OS Knowledge Intake Agent

## 1. Scope chốt

Chọn **Track A - Learning OS**.

Không làm chatbot học tập chung chung. Prototype là một **Knowledge Intake Agent** cho AI in Action: người vận hành/nhóm nạp tài liệu lớp vào trước, sau đó học viên hỏi. Agent chỉ trả lời dựa trên tài liệu đã nạp; nếu thiếu nguồn thì nói không biết, không đoán.

Chia thành 2 scope:

| Scope | User hỏi gì? | Agent giúp gì? |
|---|---|---|
| Learning Content Support | Nội dung bài học, lab, rubric, khái niệm, ví dụ, cách làm bài, lỗi khi làm bài. | Tìm trong tài liệu học, giải thích lại, chia nhỏ bước làm, tạo checklist học tập. |
| Program Operations Support | Cách hoạt động của AI in Action: lịch, deadline, nộp repo, làm nhóm/cá nhân, demo, grading, owner plan. | Tìm trong tài liệu vận hành, tổng hợp yêu cầu, nhắc file cần có, nêu phần thiếu source nếu chưa chắc. |

## 2. Pain point chốt

Học viên không thiếu mỗi câu trả lời. Pain thật là thông tin nằm rải rác ở nhiều nguồn: slide, repo, README, Discord, mentor note, rubric. Khi hỏi một câu mơ hồ như:

```text
Day05 phải làm gì?
```

agent cần hiểu user đang hỏi:

- nội dung bài học hay cách nộp bài;
- phần cá nhân hay phần nhóm;
- Day05 hay chuẩn bị Day06;
- cần checklist, giải thích, demo script hay owner plan;
- có tài liệu/source nào để dựa vào không.

Nếu AI trả lời bằng trí nhớ hoặc suy đoán, output dễ sai deadline, sai file, sai scope, hoặc lệch rubric. Vì vậy workflow phải có **ask loop**, **source check**, **unknown/refusal**, và **correction loop**.

## 3. Knowledge Pack

Agent không cần truy cập nội bộ thật ngay. Prototype cho phép nạp hoặc chọn trước các nhóm tài liệu:

| Knowledge pack | Ví dụ tài liệu | Dùng cho scope |
|---|---|---|
| Course content docs | Slide bài học, notebook, README lab, prompt examples, code template. | Learning Content Support |
| Assignment docs | Lab brief, rubric, acceptance checklist, repo instructions. | Learning Content + Program Operations |
| Program ops docs | Schedule, deadline, submission rule, team rule, demo instruction, FAQ. | Program Operations Support |
| Live updates | Discord pinned messages, mentor note, change log. | Program Operations + correction |

Source rule:

```text
Nếu thông tin không nằm trong knowledge pack,
hoặc source có thể outdated,
agent không được bịa.
Agent phải nói rõ: "mình chưa tìm thấy trong tài liệu đã nạp".
```

## 4. Workflow tổng thể

```mermaid
flowchart TD
    A["USER ASKS<br/>Ví dụ: Day05 phải làm gì?"] --> B["1. READ CURRENT CONVERSATION<br/>- Câu hỏi mới nhất<br/>- Context user đã bổ sung<br/>- Working memory hiện tại"]

    B --> C["2. DETECT INTENT + SCOPE<br/>Agent xác định scope:<br/>A. Learning Content Support<br/>B. Program Operations Support<br/>C. Ambiguous / thiếu context"]

    C --> D{"Scope đã rõ chưa?"}

    D -->|Rõ| E["3A. SCOPE CLEAR<br/>Có đủ context để tìm nguồn"]
    D -->|Chưa rõ| F["3B. SCOPE AMBIGUOUS<br/>Thiếu day / scope / role / output"]

    E --> G["4A. RETRIEVE SOURCE<br/>Tìm trong knowledge pack<br/>theo scope đã detect"]

    F --> H["4B. ASK LOOP<br/>Hỏi 1–5 câu hoặc đưa option<br/>User trả lời trong cùng chat"]
    H --> I["5B. APPEND CONTEXT<br/>Không mở conversation mới<br/>Update working memory"]

    G --> J["6. SOURCE CHECK<br/>Agent kiểm tra:<br/>- Có source liên quan không?<br/>- Source thuộc content hay operations?<br/>- Source mới hay outdated?<br/>- Có mâu thuẫn không?"]
    I --> J

    J --> K{"Source đủ tin cậy không?"}

    K -->|Có| L["7A. SOURCE FOUND<br/>Có đủ căn cứ để trả lời"]
    K -->|Không| M["7B. NO SOURCE / LOW TRUST<br/>Không có nguồn hoặc nguồn outdated"]

    L --> N["8A. SYNTHESIZE ANSWER<br/>Tóm tắt + checklist<br/>source status + next step"]

    M --> O["8B. UNKNOWN / REFUSAL<br/>Không đoán<br/>Draft câu hỏi gửi mentor / TA / Discord"]

    N --> P["9. CORRECTION LOOP<br/>Nếu user sửa Day05 → Day06,<br/>cá nhân → nhóm,<br/>content → ops,<br/>hoặc upload source mới,<br/>agent update memory và chạy lại"]
    O --> P

    P --> B
```

## 5. Hai scope chạy như thế nào

### 5.1 Learning Content Support

```text
User hỏi:
  "Thin spec là gì?"
  "Build slice nghĩa là sao?"
  "Happy path với failure path khác nhau thế nào?"

Agent làm:
  1. Detect scope = Learning Content.
  2. Retrieve slide/README/rubric có khái niệm liên quan.
  3. Nếu có nguồn:
       - giải thích ngắn;
       - đưa ví dụ từ bài lab;
       - gợi ý cách áp dụng vào file đang làm.
  4. Nếu thiếu nguồn:
       - nói chưa thấy trong tài liệu đã nạp;
       - draft câu hỏi gửi mentor;
       - không tự bịa định nghĩa quá chắc.

Output:
  - Detected scope: Learning Content
  - Source status
  - Explanation
  - Example
  - Next action
```

### 5.2 Program Operations Support

```text
User hỏi:
  "Day05 phải nộp gì?"
  "File 01 có liên quan gì tới 02 không?"
  "Mai Day06 build gì?"
  "Nộp repo cá nhân hay nhóm?"

Agent làm:
  1. Detect scope = Program Operations.
  2. Nếu câu hỏi mơ hồ, hỏi thêm:
       - Day05 hay Day06?
       - phần cá nhân hay nhóm?
       - cần checklist nộp bài hay giải thích yêu cầu?
  3. Retrieve README, lab brief, schedule, screenshot slide, Discord pinned.
  4. Nếu có nguồn:
       - tổng hợp deliverables;
       - liệt kê file/folder cần có;
       - chỉ ra việc còn thiếu;
       - nêu source đã dùng.
  5. Nếu thiếu source:
       - nói không tìm thấy rule/deadline trong tài liệu đã nạp;
       - draft câu hỏi gửi mentor/TA.

Output:
  - Detected scope: Program Operations
  - Source status
  - Deliverable checklist
  - Missing info
  - Next action
```

## 6. Working Memory

Agent giữ một working memory cho **case hiện tại**, không mở conversation mới khi user bổ sung context.

| Field | Ý nghĩa |
|---|---|
| Current case | Câu hỏi/task hiện tại user đang xử lý. |
| Scope | Learning Content, Program Operations, hoặc Ambiguous. |
| Day/module | Day05, Day06, lab nào, track nào. |
| User role | Làm cá nhân, làm nhóm, owner evidence, owner SPEC, owner prototype, reviewer. |
| Knowledge source used | File/slide/README/screenshot/Discord note nào đã dùng. |
| Source status | Found, missing, outdated risk, conflict. |
| Missing info | Day, role, source, deadline, deliverable, output format còn thiếu. |
| Desired output | Checklist, explanation, demo script, owner plan, question to mentor. |
| Conversation corrections | User đã sửa scope/day/context gì trong cuộc trò chuyện. |

## 7. Ask Loop Policy

Agent không hỏi cố định 3 câu. Agent chủ động quyết định số câu hỏi theo context thiếu.

```text
Nếu thiếu ít:
  hỏi 1-2 câu.

Nếu câu hỏi rất mơ hồ:
  hỏi tối đa 5 câu/option trong một lượt.

Nếu user trả lời vẫn thiếu:
  hỏi tiếp vòng sau, nhưng vẫn giữ cùng conversation.
```

Priority khi hỏi:

| Slot thiếu | Độ ưu tiên | Ví dụ câu hỏi |
|---|---|---|
| Scope | P0 | "Bạn đang hỏi nội dung bài học hay cách nộp/vận hành chương trình?" |
| Day/module | P0 | "Bạn hỏi Day05, Day06, hay lab khác?" |
| User role | P1 | "Bạn đang làm phần cá nhân, phần nhóm, hay chuẩn bị prototype/demo?" |
| Source | P1 | "Bạn có slide/README/screenshot nào muốn agent dùng làm nguồn không?" |
| Output format | P2 | "Bạn muốn checklist ngắn, giải thích chi tiết, hay demo script?" |

Ví dụ ask loop:

```text
User: Bài này làm sao?

Agent:
Mình cần làm rõ một chút trước khi trả lời:
1. Bạn đang hỏi Day05 hay Day06?
2. Bạn hỏi phần cá nhân hay phần nhóm?
3. Bạn muốn checklist cần nộp hay giải thích cách làm?
```

## 8. Source Check Policy

Agent chỉ trả lời chắc khi có nguồn trong knowledge pack.

Nguồn ưu tiên:

1. README/lab brief/rubric trong repo.
2. Slide hoặc screenshot chính thức của buổi học.
3. Schedule, submission rule, Discord pinned message.
4. Mentor note/change log nếu user cung cấp.
5. Context user cung cấp trong conversation.

Nếu nhiều nguồn mâu thuẫn:

```text
Agent không chọn bừa.
Agent nêu mâu thuẫn:
  - Source A nói gì
  - Source B nói gì
Agent ưu tiên nguồn mới hơn/chính thức hơn nếu rõ.
Nếu không rõ, agent draft câu hỏi gửi mentor/TA.
```

## 9. Unknown / Refusal Policy

Agent phải nói không biết khi:

- không tìm thấy thông tin trong knowledge pack;
- user hỏi deadline/rule nhưng source có thể đã đổi;
- câu hỏi quá mơ hồ và user chưa bổ sung context;
- nguồn mâu thuẫn nhau;
- user yêu cầu agent đoán thay vì dựa vào tài liệu.

Mẫu trả lời:

```text
Mình chưa tìm thấy thông tin này trong tài liệu đã nạp.
Mình không muốn đoán vì có thể làm sai deadline/rubric.
Bạn có thể gửi thêm source, hoặc hỏi mentor/TA bằng câu này:
"[draft question]"
```

## 10. Output Contract

Mỗi câu trả lời của prototype nên có format ổn định:

| Output | Nội dung |
|---|---|
| Detected scope | Learning Content / Program Operations / Ambiguous. |
| Source status | Found / Missing / Outdated risk / Conflict. |
| Answer summary | Câu trả lời ngắn dựa trên nguồn. |
| Action checklist | 3-5 bước tiếp theo. |
| Missing info | Thứ còn thiếu để trả lời chắc hơn. |
| Unknown note | Phần agent không biết hoặc cần mentor/TA xác nhận. |
| Suggested follow-up | Câu hỏi tiếp theo hoặc draft hỏi mentor/TA. |

Ví dụ output:

```text
Detected scope: Program Operations
Source status: Found in Day05 README + slide checklist

Summary:
Day05 chưa cần prototype hoàn chỉnh. Nhóm cần evidence pack, build slice,
Auto/Aug decision, 4 paths, failure mode và owner plan.

Checklist:
1. Hoàn thiện evidence-pack.md.
2. Chốt build slice trong thin-spec.md.
3. Viết workflow.md có happy/low-confidence/failure/correction.
4. Ghi owner plan cho Day06.
5. Đánh dấu phần chưa có evidence thật.

Unknown note:
Mình chưa thấy update deadline mới ngoài source đã nạp.
```

## 11. Four paths cần test

| Path | Input demo | Agent behavior | Output mong muốn |
|---|---|---|---|
| Happy | "Day05 phải nộp gì cho phần group spec?" | Detect Program Operations, retrieve README/slide, tổng hợp checklist. | Deliverables + file cần có + next step + source status. |
| Low-confidence | "Bài này làm sao?" | Không trả lời ngay; hỏi day, scope, cá nhân/nhóm, output mong muốn. | Ask loop trong cùng chat. |
| No-source / Unknown | "Deadline đổi sang mấy giờ rồi?" nhưng knowledge pack không có update. | Không đoán; nói chưa thấy nguồn, draft câu hỏi gửi mentor/Discord. | Refusal rõ + cách kiểm chứng. |
| Correction | User sửa "không phải Day05, là Day06 prototype." | Update working memory, retrieve docs Day06, đổi checklist. | Checklist mới đúng Day06. |
| Wrong-scope recovery | User hỏi "thin spec là gì" rồi chuyển sang "nộp repo ở đâu". | Chuyển scope từ Learning Content sang Program Operations. | Answer mới theo ops, không giữ nhầm scope cũ. |

## 12. Day06 build slice

Prototype ngày mai chỉ cần build lát cắt nhỏ:

```text
Một học viên hỏi câu mơ hồ về Day05/Day06
  -> Agent hỏi thêm nếu thiếu context
  -> Agent phân loại Learning Content / Program Operations
  -> Agent tìm trong knowledge pack đã nạp
  -> Agent trả checklist/source-grounded answer
  -> Nếu không có nguồn, agent nói không biết và draft câu hỏi gửi mentor/TA
```

Không build cả LMS. Không build full chatbot cho mọi môn học. Chỉ cần chứng minh một flow:

```text
input -> ask loop -> source check -> answer/unknown -> correction
```

## 13. Owner Plan

| Owner | Việc làm | Output |
|---|---|---|
| Phúc | Research / evidence | Screenshot slide/repo + quote câu hỏi mơ hồ |
| Tuấn Anh | SPEC | `evidence-pack.md`, `thin-spec.md`, `workflow.md` |
| Vũ Anh | Prototype | UI có chat, quick options, source status, checklist |
| Cung | Test / failure path | Happy, low-confidence, no-source, correction, wrong-scope |
| Phúc | Demo script / repo | Demo script cho input -> AI -> output -> failure handling |
