# Evidence Pack - Food & Delivery

## 1. Nhóm và track

**Tên nhóm:** Food & Delivery - Cung, Tuấn Anh, Vũ Anh, Phúc  
**Track:** Food & Delivery  
**Product/app đã chọn:** GrabFood  
**Build slice đang nghĩ:** AI hỏi nhanh nhu cầu ăn uống rồi gợi ý 3 món/quán phù hợp theo ngân sách, khẩu vị, thời gian giao và mức độ chắc chắn.

## 2. Self-use evidence

Nhóm dùng workflow: mở app giao đồ ăn khi đang đói nhưng chưa biết ăn gì, thử tìm món theo nhu cầu mơ hồ như "ăn gì nhanh dưới 60k", "món nhẹ buổi chiều", "ăn no nhưng không cay".

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Khi user chưa có món cụ thể, app thường đưa nhiều danh mục/quán/voucher cùng lúc. User phải tự lọc theo giá, phí giao, rating, thời gian giao. | Cần bổ sung screenshot app thật của nhóm ở Day06 checkpoint M1. Nguồn tham khảo: https://food.grab.com/vn/en/ | Low-confidence | Pain không chỉ là "không có món", mà là quá nhiều lựa chọn nhưng thiếu quyết định được cá nhân hóa. |
| Grab nói người dùng trung bình dành 17 phút browsing trước khi đặt món và 74% browse khi chưa có cuisine cụ thể. | https://www.grab.com/inside-grab/stories/personalising-food-recommendations-on-grabfood/ | Failure / Low-confidence | Build slice nên tập trung vào user "chưa biết ăn gì", không phải user đã biết chính xác quán/món. |
| GrabFood dùng machine learning-driven search and recommendations để cá nhân hóa food discovery. | https://www.grab.com/inside-grab/stories/personalising-food-recommendations-on-grabfood/ | Happy | AI/recommendation là feature thật của app, nên nhóm có thể học pattern từ app thật thay vì tự nghĩ chatbot chung chung. |
| Grab có pattern "Order Again" cho user hay mua lại quán quen, nhưng user cũng cần khám phá món mới. | https://www.grab.com/inside-grab/stories/personalising-food-recommendations-on-grabfood/ | Correction / Happy | Prototype nên cho user chọn "quán quen" hoặc "thử món mới", vì cùng một user có hai nhu cầu khác nhau. |

## 3. User / review / social evidence

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| "Consumers are spending an average of 17 minutes browsing on GrabFood before placing their order" | Grab official article: https://www.grab.com/inside-grab/stories/personalising-food-recommendations-on-grabfood/ | Người dùng GrabFood cần đặt đồ ăn | Tốn thời gian chọn món trước khi order. |
| "Some 74 per cent also browse without a particular cuisine in mind" | Grab official article | User chưa biết ăn món gì | Search/recommendation dễ fail nếu user không có keyword rõ. |
| Grab nói họ dùng hành vi như order history và clicks để hiểu likes/dislikes của user. | Grab official article | User dùng app nhiều lần | Nếu không dùng context cá nhân, gợi ý có thể chung chung và không đáng tin. |
| ShopeeFood public site cho thấy số lượng địa điểm rất lớn: TP.HCM hơn 120k địa điểm, Hà Nội hơn 66k địa điểm. | ShopeeFood public site: https://shopee.shopeefood.vn/ | User ở đô thị lớn | Nhiều lựa chọn làm tăng cognitive load; cần bộ lọc/gợi ý tốt hơn. |

Nếu nhóm chưa có screenshot app thật trong điện thoại:

```text
Đây là evidence public + self-use draft. Nhóm sẽ kiểm bằng cách mỗi thành viên chụp 1 màn hình app GrabFood/ShopeeFood khi tìm món mơ hồ trước checkpoint M1 Day 06.
```

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| GrabFood | Cá nhân hóa search/recommendation bằng order history, clicks, thời điểm trong ngày, budget và willingness to wait. | Dùng vài tín hiệu hẹp để rank món/quán, không hỏi user quá nhiều. | Có. Prototype dùng form 3 câu và mock ranking. |
| ShopeeFood | Có mạng lưới địa điểm lớn ở nhiều thành phố, nhiều lựa chọn món/quán. | Vấn đề chính là lọc và quyết định, không phải thiếu lựa chọn. | Có. Dùng evidence số lượng địa điểm để justify pain. |
| Netflix / Spotify recommendation | Gợi ý theo lịch sử, mood, preference và cho user sửa feedback. | Cần nút "không thích", "quá đắt", "giao lâu" để correction. | Có. Prototype có feedback chips. |

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
GrabFood users browse trung bình 17 phút trước khi đặt món; 74% browse khi chưa có cuisine cụ thể.
GrabFood đã dùng ML search/recommendation để cá nhân hóa discovery.
ShopeeFood cho thấy số lượng địa điểm trong đô thị rất lớn, nên user dễ bị quá tải lựa chọn.

Insight:
User không chỉ gặp vấn đề "không biết ăn gì".
Thật ra họ cần decision support nhanh, có lý do rõ, để chọn một món đủ hợp trong bối cảnh rất cụ thể: ngân sách, khẩu vị, thời gian giao và mức độ đói.

Opportunity:
AI có thể giúp bằng cách augment bước chọn món: hỏi 2-3 câu, rank 3 lựa chọn phù hợp, giải thích lý do, và cho user sửa nếu gợi ý sai.
```

## 6. Evidence đổi SPEC như thế nào?

- [x] Đổi user chính.
- [x] Đổi pain statement.
- [x] Đổi build slice.
- [x] Đổi Auto/Aug decision.
- [x] Đổi 4 paths.
- [x] Đổi failure mode.
- [x] Đổi owner/test plan.

Ghi rõ thay đổi quan trọng:

```text
Trước evidence, nhóm có thể định làm "AI assistant cho đặt đồ ăn".
Sau evidence, nhóm đổi thành "AI gợi ý 3 món/quán cho user chưa biết ăn gì".
Lý do: evidence cho thấy pain nằm ở browsing/discovery và quá tải lựa chọn, không nằm ở toàn bộ quy trình đặt hàng.

Trước evidence, nhóm có thể muốn AI tự chọn món.
Sau evidence, nhóm chọn augmentation: AI gợi ý, user quyết định cuối.
Lý do: khẩu vị, dị ứng, ngân sách và thời gian giao là quyết định cá nhân; AI sai có thể làm user mất tiền hoặc nhận món không phù hợp.
```
