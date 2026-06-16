# Day 05 - 02 Group SPEC

## Nhóm

| Thành viên | Mã học viên |
|---|---|
| Phạm Đình Phúc | 2A202600802 |
| Nguyễn Tuấn Anh | 2A202600758 |
| Hà Vũ Anh | 2A202600571 |
| Đỗ Văn Cung | 2A202600793 |

## Chủ đề nhóm

**Track:** A - Learning OS

**Tên ý tưởng:** Learning OS Knowledge Intake Agent

Nhóm thiết kế một agent hỗ trợ học viên AI in Action hỏi về bài học hoặc cách vận hành chương trình. Agent không trả lời bằng suy đoán; agent hỏi thêm khi thiếu context, tìm trong tài liệu đã nạp, rồi trả về checklist/source-grounded answer. Nếu không có nguồn, agent nói rõ không tìm thấy thông tin và gợi ý câu hỏi gửi mentor/TA.

## Các file trong folder này

| File | Vai trò |
|---|---|
| `evidence-pack.md` | Gom evidence, pain thật, insight và lý do đổi thành SPEC. |
| `workflow.md` | Mô tả workflow ASCII để build prototype Day06: ask loop, source check, unknown/refusal, correction loop. |
| `thin-spec.md` | SPEC mỏng: user, pain, build slice, output contract, 4 paths, failure mode và owner plan. |

## Build slice chốt

```text
Một học viên hỏi mơ hồ về Day05/Day06
  -> Agent hỏi thêm nếu thiếu context
  -> Agent phân loại Learning Content / Program Operations
  -> Agent tìm trong knowledge pack đã nạp
  -> Agent trả checklist/source-grounded answer
  -> Nếu không có nguồn, agent nói không biết và draft câu hỏi gửi mentor/TA
```
