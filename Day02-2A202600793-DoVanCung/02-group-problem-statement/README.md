# 02 — Group Problem Statement Draft

## Candidate problem nhóm chốt

```text
Cognitive reframing khi sinh viên nhận feedback tiêu cực.
```

Problem 1 câu:

```text
Sinh viên khi nhận feedback hoặc điểm thấp thường diễn giải feedback thành đánh giá tiêu cực về bản thân, thay vì chuyển feedback thành các điểm sửa cụ thể và kế hoạch cải thiện.
```

Domain:

```text
Domain lớn: Empathy
Hướng cụ thể: Cognitive Reframing
Mức AI dự kiến: Workflow
```

Boundary ngắn:

```text
AI không đóng vai AI therapist, không chẩn đoán, không trị liệu, không xử lý khủng hoảng tâm lý, không chấm lại bài và không đánh giá năng lực cá nhân. AI chỉ hỗ trợ self-reflection, cognitive reframing và chuyển feedback thành action items. Người dùng vẫn tự chọn, sửa và quyết định.
```

---

## 1. Group convergence

Nhóm chọn candidate này vì nó có actor rõ, workflow rõ, bottleneck rõ và dễ vẽ before/after workflow. Problem cũng đủ an toàn vì AI không can thiệp vào đánh giá học thuật hay điều trị tâm lý; AI chỉ hỗ trợ người học tự diễn giải feedback theo cách cân bằng hơn.

### Candidate pool

Phân bổ candidate: mỗi thành viên đề xuất **3 đề tài**.

| # | Người đưa ra | Candidate problem | Người gặp vấn đề | Bottleneck | Ghi chú |
|---|---|---|---|---|---|
| 1 | Cung | Tổng hợp tài liệu ôn thi | Sinh viên trước kỳ thi | Tài liệu nằm rải rác ở slide, note, Discord/Zalo | Utility problem; dễ thành search/summarization |
| 2 | Cung | Tìm lại thông tin Discord/Zalo | Sinh viên trong lớp/CLB | Tin nhắn trôi, keyword nhớ không chính xác | Retrieval rõ nhưng không thuộc Empathy |
| 3 | Cung | Theo dõi deadline môn học | Sinh viên nhiều môn | Deadline phân tán ở LMS, Discord, calendar | Có thể giải bằng reminder/calendar |
| 4 | Anh | Tìm quán ăn phù hợp ngân sách | Sinh viên quanh trường | Budget, khẩu vị, khoảng cách thay đổi theo ngày | Recommendation problem, impact học tập thấp |
| 5 | Anh | Tìm tuyến đường tối ưu đến trường | Sinh viên đi học bằng xe/bus | Delay/traffic, chuyển tuyến | Data phụ thuộc bản đồ, không phải problem lớp |
| 6 | Anh | Tìm phòng trọ gần trường | Sinh viên cần thuê nhà | Thông tin phòng không minh bạch, cập nhật nhanh | Rộng, cần dữ liệu thị trường thật |
| 7 | Kiên | Kiến thức AI quá nhiều và tốc độ học quá nhanh | Người mới học AI/AI20K | Overload, không biết ưu tiên học gì | Pain thật nhưng scope rất rộng |
| 8 | Kiên | Khó cân bằng giữa việc học ở trường đại học và AI20K | Sinh viên học song song | Lịch học, bài tập và tự học cạnh tranh thời gian | Gần productivity/coaching dài hạn |
| 9 | Kiên | Lớp học đông, trợ giảng không đủ hỗ trợ | Học viên và TA | Câu hỏi lặp lại, TA quá tải | Problem hệ thống, actor chính có thể là TA |
| 10 | Dũng | Copy-paste Excel vào CMS | Người nhập liệu/admin | Format bảng bị vỡ, thao tác lặp lại | Operational automation |
| 11 | Dũng | Sửa định dạng/dấu cách Excel | Người làm file dữ liệu | Dữ liệu không sạch, spacing lỗi | Rule/process fix có thể là đủ |
| 12 | Dũng | Gắn Tags cho thanh Search | Người quản trị nội dung | Thiếu taxonomy/tag chuẩn | Information architecture, không thuộc Empathy |
| 13 | Phúc | Cognitive reframing khi nhận feedback tiêu cực | Sinh viên nhận feedback/điểm thấp | Cá nhân hóa feedback thành "mình kém" | Candidate nhóm chốt |
| 14 | Phúc | Reframing tin nhắn mơ hồ để giảm overthinking | Sinh viên/người trẻ nhắn tin | AI dễ đoán ý định người gửi thay người dùng | Gần Empathy nhưng boundary rủi ro |
| 15 | Phúc | Cognitive reframing cho deadline panic thành bước hành động nhỏ | Sinh viên sát deadline | Panic làm tê liệt, không chia nhỏ được việc | Gần topic chốt nhưng dễ thành task planner |

### Vì sao chọn candidate này

```text
1. Actor cụ thể: sinh viên nhận feedback/điểm thấp.
2. Current workflow dễ quan sát: nhận feedback → cảm thấy khó chịu → diễn giải tiêu cực → né đọc kỹ → trì hoãn sửa.
3. Bottleneck không nằm ở thiếu thông tin, mà ở bước diễn giải feedback.
4. Success metric có thể đo bằng action items, thời gian bắt đầu sửa bài, và self-rated distress nhẹ.
5. AI intervention nằm ở một bước rõ: hỗ trợ self-reflection và cognitive reframing, không thay người dùng quyết định.
```

Đoạn pitch lý do chọn đề tài của Phúc so với các đề tài khác:

```text
Trong 15 candidate của nhóm, nhiều vấn đề rất thực tế nhưng thiên về utility/search/reminder như tìm tài liệu ôn thi, tìm tin nhắn Discord/Zalo, theo dõi deadline, tìm quán ăn, tìm tuyến đường hoặc tìm phòng trọ. Các vấn đề này có workflow rõ, nhưng ít chạm tới domain Empathy và thường có thể giải bằng search, filter, reminder hoặc recommendation system tương đối quen thuộc. Một số vấn đề khác như kiến thức AI quá nhiều, cân bằng đại học với AI20K, hoặc lớp đông thiếu TA có impact lớn hơn, nhưng scope rộng, nhiều stakeholder và khó làm thành một AI workflow nhỏ trong thời gian lab.

Candidate "Cognitive reframing khi nhận feedback tiêu cực" được chọn vì nằm ở điểm giữa tốt nhất: pain đủ cá nhân và dễ đồng cảm, input đủ cụ thể là feedback/điểm/comment thật, workflow hiện tại dễ vẽ, bottleneck rõ ở bước diễn giải feedback, và AI có thể can thiệp đúng một đoạn nhỏ bằng self-reflection + cognitive reframing + action items. So với reframing tin nhắn mơ hồ, đề tài này an toàn hơn vì AI không cần đoán ý định người khác. So với deadline panic, đề tài này ít bị trượt thành task planner hơn vì trọng tâm vẫn là Empathy và cách sinh viên diễn giải feedback về bản thân.
```

### Vì sao không chọn các candidate khác

| Candidate | Lý do chưa chọn |
|---|---|
| Tìm tài liệu ôn thi / tìm lại thông tin Discord/Zalo | Rất thực tế nhưng chủ yếu là retrieval/search problem, không thể hiện rõ domain Empathy |
| Theo dõi deadline / tìm tuyến đường / tìm quán ăn / tìm phòng trọ | Có thể giải bằng reminder, map, filter hoặc recommendation; AI không phải điểm can thiệp bắt buộc |
| Kiến thức AI quá nhiều / cân bằng đại học và AI20K | Pain lớn nhưng scope rộng, dễ thành coaching system dài hạn hoặc productivity app |
| Lớp học đông, trợ giảng không đủ hỗ trợ | Impact cao nhưng actor và quyền can thiệp nghiêng về TA/giảng viên/hệ thống lớp học hơn là một workflow cá nhân |
| Copy-paste Excel vào CMS / sửa định dạng Excel / gắn tags cho search | Workflow rõ nhưng thiên về operational automation hoặc information architecture, ít liên quan tới Empathy |
| Reframing tin nhắn mơ hồ | Gần Empathy nhưng AI dễ đoán ý định người gửi, boundary xã hội nhạy cảm hơn |
| Cognitive reframing cho deadline panic | Cũng gần topic chốt, nhưng dễ biến thành task planner; feedback tiêu cực có input cụ thể hơn để AI bám vào |

Nếu có disagreement:

```text
Nhóm sẽ không vote ngay theo cảm tính. Nhóm dùng tiêu chí actor rõ, workflow rõ, bottleneck rõ, metric đo được, boundary an toàn, và mức AI phù hợp để so sánh.
```

---

## 2. Quick validation

Tổng số người dự kiến hỏi nhanh: **5 người tính cả Phúc**.

Mục tiêu không phải chứng minh solution hay, mà kiểm tra pain có thật không:

```text
- Có ai thật sự cá nhân hóa feedback thành "mình kém" không?
- Có ai né đọc kỹ feedback vì thấy khó chịu không?
- Có ai mất lâu mới chuyển feedback thành việc cần sửa không?
- Có ai thấy AI có thể phản tác dụng nếu an ủi sáo rỗng hoặc hiểu sai context không?
```

### Câu hỏi validation

```text
1. Lần gần nhất bạn nhận feedback/điểm thấp, suy nghĩ tiêu cực đầu tiên của bạn là gì?
2. Bạn có từng nghĩ kiểu "mình kém", "mình không hợp môn này", hoặc "mình làm gì cũng sai" không?
3. Sau feedback đó, bạn thường đọc kỹ comment ngay hay né/trì hoãn vì thấy khó chịu?
4. Feedback đó có làm bạn mất động lực, sửa bài muộn, hoặc không biết bắt đầu từ đâu không?
5. Bạn mất khoảng bao lâu để biến feedback thành việc cần sửa cụ thể?
6. Nếu có một workflow hỏi gợi mở, giúp reframe suy nghĩ và tạo 3 action items, bạn có dùng không?
7. Điều gì sẽ làm bạn không tin tool đó: an ủi sáo rỗng, hiểu sai feedback, quá giống AI therapist, hay sợ phụ thuộc?
```

### Bảng validation notes

Ghi chú: bảng dưới đây là **draft/synthetic notes** để nhóm chuẩn bị pitch và đi hỏi nhanh. Khi có câu trả lời thật, nhóm nên thay bằng lời người được hỏi.

| Người được hỏi | Có gặp problem không? | Workflow hiện tại | Bottleneck | Insight |
|---|---|---|---|---|
| Phúc | Có | Nhận feedback → hụt mood → nhìn điểm/comment trước → tự nghĩ "mình kém" → để sau mới sửa | Cá nhân hóa feedback thành đánh giá bản thân | Pain mạnh nhất nằm ở 10-20 phút đầu sau khi nhận feedback; cần reframe trước khi né feedback |
| Cung | Có một phần | Đọc comment → thấy khó chịu → hỏi bạn xem feedback có quá nặng không → sau đó mới quay lại sửa | Cần một người phản chiếu để bớt diễn giải quá tiêu cực | Tool có ích nếu AI hỏi ngắn, không phán xét, không an ủi sáo rỗng |
| Anh | Có | Nhận feedback ngắn/cứng → nghĩ TA/giảng viên không thích bài mình → mất động lực sửa | Trộn lẫn fact trong feedback với assumption về ý định người feedback | AI nên tách fact/thought/feeling, nhưng không được đoán ý định người khác |
| Kiên | Có | Thấy điểm thấp → panic → mở nhiều tài liệu cùng lúc → không biết sửa phần nào trước | Không chuyển feedback thành next step cụ thể | Action items là giá trị chính; reframe chỉ có ích nếu dẫn tới bước sửa nhỏ |
| Dũng | Chưa chắc / có nhẹ | Vẫn đọc feedback nhưng dễ defensive nếu comment quá trực diện → chỉ nhớ câu tiêu cực nhất | Phản ứng tự vệ làm bỏ qua phần feedback đúng | Problem không nặng với tất cả mọi người; target nên là sinh viên dễ self-critical hoặc nhận feedback phê bình mạnh |

### Validation takeaway

```text
Draft signal: 4/5 người nhận ra tình huống nhận feedback tiêu cực; 3-4/5 có biểu hiện cá nhân hóa feedback, né đọc kỹ hoặc bị kẹt ở cảm xúc ban đầu; 3/5 nói action items cụ thể sẽ hữu ích hơn lời an ủi chung chung. Tín hiệu này ủng hộ việc chọn candidate #13, nhưng nhóm vẫn cần xác nhận bằng hỏi nhanh thật.

Nếu validation thật cho kết quả tương tự, problem nên Go cho lab prototype. Nếu đa số đọc feedback và sửa ngay, nhóm cần thu hẹp actor: sinh viên dễ self-critical, sinh viên mới học môn khó, hoặc sinh viên nhận feedback phê bình mạnh.
```

---

## 3. Research giải pháp / pattern đã có

Phần này nhóm dùng cả pattern thực hành và paper gần đây từ ACL Anthology để tránh nghĩ trong chân không. Vì các paper dưới đây nằm gần vùng mental health/psychotherapy, nhóm chỉ lấy bài học về **cognitive reframing workflow**, không mở rộng scope thành trị liệu.

| Pattern / tool type | Cần tìm gì? | Bài học kéo về problem nhóm |
|---|---|---|
| CBT-style thought record / cognitive reframing worksheet | Cách tách situation, thought, emotion, evidence, alternative thought | Non-AI alternative có thể là form cố định |
| AI journaling / self-reflection tools | Cách AI hỏi câu gợi mở và phản hồi theo ngữ cảnh | AI có thể hữu ích ở bước ngôn ngữ và empathy |
| Learning feedback / formative assessment tools | Cách feedback được chuyển thành next steps | Action items phải gắn với feedback thật, không chỉ an ủi |
| ACL research on cognitive reframing | LM/LLM hỗ trợ reframe negative thoughts như thế nào | Reframe tốt cần empathy + specificity, không chỉ chuyển tiêu cực thành tích cực |

Research notes:

| Nguồn / tool / case | Link | Họ giải quyết phần nào? | Khoảng trống / rủi ro | Bài học cho nhóm |
|---|---|---|---|---|
| Sharma et al., ACL 2023 — *Cognitive Reframing of Negative Thoughts through Human-Language Model Interaction* | https://aclanthology.org/2023.acl-long.555/ | Nghiên cứu human-LM interaction để tạo reframed thoughts; xây framework thuộc tính ngôn ngữ cho reframe; có field study lớn với người dùng thật | Bối cảnh là negative thoughts/mental health, nhạy cảm hơn bài học tập của nhóm | Reframe không nên chỉ "positive hóa"; người dùng thích reframe có empathy và cụ thể. Điều này củng cố boundary: AI phải hỏi rõ context và tạo action items gắn với feedback thật |
| Xiao et al., ACL 2024 — *HealMe: Harnessing Cognitive Reframing in Large Language Models for Psychotherapy* | https://aclanthology.org/2024.acl-long.93/ | Đề xuất LLM workflow cho cognitive reframing, nhấn mạnh empathetic dialogue và giúp người dùng tìm góc nhìn cân bằng hơn | Paper hướng tới psychotherapy nên scope/risk cao hơn nhiều; nhóm không claim làm trị liệu | Lấy pattern "empathetic dialogue + balanced perspective", nhưng hạ scope xuống academic feedback: AI guide reflection, sinh viên tự chọn/sửa reframe |
| Maddela et al., ACL 2023 — *Training Models to Generate, Recognize, and Reframe Unhelpful Thoughts* | https://aclanthology.org/2023.acl-long.763/ | Xây PATTERNREFRAME với unhelpful thought patterns và positive reframes; dùng LM để tạo/gợi ý practice material | Tập trung vào practice data và positive reframes, chưa trực tiếp giải bài toán feedback học tập | Có thể dùng taxonomy "unhelpful thought patterns" để nhận diện kiểu suy nghĩ như all-or-nothing, overgeneralization; nhưng output của nhóm vẫn phải gắn với feedback thật |
| Chen et al., Findings EMNLP 2023 — *Cognitive Distortion Detection through Diagnosis of Thought Prompting* | https://aclanthology.org/2023.findings-emnlp.284/ | Đề xuất DoT prompting: tách facts/thoughts, contrastive reasoning, schema analysis để nhận diện cognitive distortions | Tên "diagnosis" và bối cảnh psychotherapy khá nhạy cảm; nhóm không dùng AI để chẩn đoán | Lấy ý tưởng tách fact khỏi thought và hỏi bằng chứng ủng hộ/phản bác; tránh gọi là diagnosis trong sản phẩm của nhóm |
| Qi et al., NLP4PI 2025 — *Does Reasoning with LLMs Improve Recognizing, Generating and Reframing Unhelpful Thoughts?* | https://aclanthology.org/2025.nlp4pi-1.5/ | So sánh reasoning methods cho nhận diện, tạo và reframe unhelpful thoughts | Workshop paper; không nên overclaim rằng reasoning luôn tốt trong mọi case | Có thể thử structured reasoning nội bộ cho AI, nhưng user-facing output phải ngắn, rõ, không làm người dùng thấy bị "phân tích tâm lý" quá mức |

Research takeaway:

```text
Các paper ACL/EMNLP gần đây ủng hộ hướng dùng LM/LLM để hỗ trợ cognitive reframing, nhưng cũng cho thấy rủi ro nếu AI chỉ an ủi chung chung, positive hóa quá mức, hoặc đi quá gần psychotherapy. Với bài toán nhóm, hướng hợp lý là Workflow nhỏ: AI hỏi gợi mở, tách fact/thought/feeling, gợi ý reframe cụ thể và action items; người dùng vẫn kiểm tra và quyết định.
```

---

## 4. Current workflow

```text
CURRENT STATE — feedback dễ bị cá nhân hóa

[1 Sinh viên nhận feedback/điểm thấp]
        |
        v
[2 Đọc nhanh comment hoặc chỉ nhìn điểm tổng]
        |
        v
[3 Cảm thấy thất vọng / xấu hổ / defensive]
        |
        v
[4 Diễn giải tiêu cực: "mình kém"]  <-- bottleneck chính
        |
        v
[5 Né đọc kỹ feedback hoặc chưa muốn mở lại bài]
        |
        v
[6 Trì hoãn sửa bài / không biết bắt đầu từ đâu]
        |
        v
[7 Sát deadline mới quay lại sửa, dễ lặp lại lỗi cũ]
```

### Current workflow table

| Bước | Actor | Input | Output | Thời gian/tần suất | Ghi chú |
|---|---|---|---|---|---|
| 1 | Sinh viên | Feedback/điểm | Biết kết quả bài làm | Mỗi lần nhận feedback | Trigger chính |
| 2 | Sinh viên | Comment/điểm | Ấn tượng ban đầu | 1-5 phút | Có thể chỉ nhìn điểm |
| 3 | Sinh viên | Ấn tượng ban đầu | Cảm xúc tiêu cực | Vài phút đến vài giờ | Distress nhẹ |
| 4 | Sinh viên | Cảm xúc + suy nghĩ | Diễn giải "mình kém" | Nhanh nhưng ảnh hưởng lớn | Bottleneck |
| 5 | Sinh viên | Feedback chưa xử lý | Né/trì hoãn | Vài giờ đến vài ngày | Mất cơ hội học từ feedback |
| 6 | Sinh viên | Deadline/sửa bài | Bắt đầu muộn | Không ổn định | Action items mơ hồ |

Bottleneck chính:

```text
Bước 4: sinh viên cá nhân hóa feedback, trộn lẫn "bài làm chưa đạt" với "mình kém", nên không chuyển feedback thành hành động sửa bài cụ thể.
```

---

## 5. Future workflow

```text
FUTURE STATE — feedback được chuyển thành self-reflection + action

[1 Sinh viên nhận feedback/điểm thấp]
        |
        v
[2 Sinh viên paste feedback hoặc tự nhập ý chính]
        |
        v
[3 AI hỏi câu gợi mở]
    - Chuyện gì đã xảy ra?
    - Bạn đang cảm thấy gì?
    - Bạn đang tự nói gì với mình?
    - Feedback này nói về bài làm hay nói về con người bạn?
        |
        v
[4 AI tách fact / feeling / interpretation]
        |
        v
[5 AI gợi ý 2-3 câu reframe cân bằng]  <-- AI intervention
        |
        v
[6 Sinh viên chọn/sửa câu reframe đúng với mình]  <-- human boundary
        |
        v
[7 AI chuyển feedback thành 3 action items cụ thể]
        |
        v
[8 Sinh viên chọn action item nhỏ nhất để bắt đầu]

Fallback:
Nếu AI gợi ý quá chung, quá tích cực giả tạo, hoặc không đúng cảm xúc thật,
sinh viên bỏ gợi ý và dùng reflection template thủ công.
```

### Before / after impact

| Metric | Trước | Sau kỳ vọng | Ghi chú |
|---|---:|---:|---|
| Thời gian để bắt đầu đọc kỹ feedback | Có thể trì hoãn vài giờ hoặc vài ngày | Dưới 15 phút sau khi nhận feedback | Cần validate |
| Số action items rõ ràng | 0 hoặc mơ hồ | Ít nhất 3 action items | Gắn với feedback thật |
| Mức distress tự đánh giá | 4/5 hoặc 5/5 | Giảm xuống 2-3/5 | Không dùng như chỉ số lâm sàng |
| Rủi ro AI | Không có AI | AI an ủi sáo rỗng hoặc hiểu sai feedback | Human boundary bắt buộc |

---

## 6. Problem Statement v0

| Field | Nội dung |
|---|---|
| **Actor** | Sinh viên nhận feedback hoặc điểm thấp từ giảng viên, TA, peer review, hoặc hệ thống chấm bài. |
| **Workflow** | Nhận feedback/điểm → đọc nhanh hoặc chỉ nhìn điểm → cảm thấy thất vọng/defensive → diễn giải thành "mình kém" → né đọc kỹ feedback → trì hoãn sửa bài → quay lại sát deadline nhưng không biết bắt đầu từ đâu. |
| **Bottleneck** | Bước diễn giải feedback: sinh viên trộn feedback về bài làm với đánh giá về bản thân, nên không chuyển được feedback thành việc cần sửa. |
| **Impact** | Giảm động lực, trì hoãn sửa bài, bỏ lỡ thông tin hữu ích trong feedback, và dễ lặp lại lỗi cũ. |
| **Success Metric** | Tạo được ít nhất 3 action items từ feedback; giảm thời gian từ lúc nhận feedback đến lúc bắt đầu sửa; giảm self-rated distress sau bước cognitive reframing; không làm thay phần tự học của sinh viên. |
| **Boundary** | AI không chẩn đoán, không trị liệu, không đánh giá năng lực cá nhân, không chấm lại bài. AI chỉ hỗ trợ self-reflection, cognitive reframing và chuyển feedback thành action items; sinh viên tự kiểm tra và quyết định. |
| **Điểm AI can thiệp** | Sau khi sinh viên nhập feedback hoặc cảm xúc ban đầu, trước khi họ né đọc kỹ feedback hoặc trì hoãn sửa bài. |
| **Mức chọn** | **Workflow**: AI hỗ trợ một chuỗi bước rõ ràng gồm hỏi gợi mở, tách fact/thought/feeling, gợi ý reframe, và tạo action items. |
| **Rủi ro & HITL** | Rủi ro: AI an ủi sáo rỗng, hiểu sai feedback, hoặc làm người dùng phụ thuộc. HITL: sinh viên chọn/sửa câu reframe, tự kiểm action items, và tìm người thật/chuyên gia nếu distress nghiêm trọng. |

---

## 7. Rule / Workflow / Agent

| Mức | Phương án cho bài toán nhóm | Khi nào đủ | Rủi ro | Chọn? |
|---|---|---|---|---|
| **No AI / process fix** | Reflection template thủ công | Đủ nếu sinh viên tự điền đều và biết tự phản biện suy nghĩ | Dễ bỏ qua khi đang stress | Không chọn làm toàn bộ |
| **Rule** | Form cố định: fact → feeling → thought → evidence → action | Đủ cho case đơn giản | Ít empathy, khó phản hồi theo ngữ cảnh feedback cụ thể | Không chọn làm toàn bộ |
| **Workflow** | AI hỏi gợi mở → tách fact/thought/feeling → gợi ý reframe → tạo action items → người dùng chọn/sửa | Hợp vì các bước rõ, AI chỉ hỗ trợ ngôn ngữ và self-reflection | Có thể gợi ý chung chung hoặc quá tích cực | **Chọn** |
| **Agent** | Agent tự theo dõi feedback, tự đánh giá cảm xúc, tự lập kế hoạch học dài hạn | Chỉ cần nếu có nhiều nguồn dữ liệu, nhiều buổi học, nhiều quyết định động | Quá rộng, nhạy cảm, dễ vượt boundary | Chưa chọn |

Mức chọn:

```text
Workflow.
```

Vì sao chọn:

```text
Workflow đủ vì các bước can thiệp rõ: hỏi gợi mở, tách fact/thought/feeling, gợi ý reframe, tạo action items, rồi để sinh viên tự chọn/sửa. Không cần Agent vì AI không cần tự lập kế hoạch dài hạn hoặc tự quyết định bước tiếp theo.
```

---

## 8. Final decision draft

Decision hiện tại:

```text
Go for lab prototype → chọn candidate #13 làm problem statement nhóm.
```

Lý do:

```text
Problem có actor, workflow, bottleneck, impact, success metric và boundary rõ. Trong candidate pool của nhóm, đây là đề tài vừa bám domain Empathy/Cognitive Reframing, vừa đủ cụ thể để thiết kế AI Workflow nhỏ. Nhóm vẫn cần hỏi nhanh 5 người để củng cố evidence, nhưng hướng hiện tại đủ tốt để dùng làm problem statement v0.
```

Nếu Go, pilot nhỏ nhất:

```text
1. Lấy một feedback thật hoặc feedback mẫu.
2. Người dùng nhập cảm xúc/suy nghĩ ban đầu.
3. Workflow AI hỏi 4-5 câu gợi mở.
4. AI tạo 2-3 câu reframe và 3 action items.
5. Người dùng đánh giá: câu reframe có đúng không, action items có dùng được không.
```

Nếu validation không đủ, cần kiểm tra lại:

```text
- Có bao nhiêu người thật sự cá nhân hóa feedback?
- Có bao nhiêu người trì hoãn sửa bài sau feedback?
- AI có giúp tạo action items tốt hơn template thủ công không?
- Boundary có đủ rõ để không thành AI therapist không?
```
