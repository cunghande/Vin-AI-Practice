# Lab 21 — Evaluation Report

**Học viên**: Đỗ Văn Cung — 2A202600793  
**Ngày nộp**: 2026-06-25  
**Submission option**: C (code-only)

---

## 1. Setup
- **Base model**: `unsloth/Qwen2.5-3B-bnb-4bit` (4-bit NF4 quantized)
- **Dataset**: `5CD-AI/Vietnamese-alpaca-gpt4-gg-translated`, 200 samples (180 train + 20 eval)
- **max_seq_length**: 1024 (p95 = 562, rounded up to the nearest power of 2)
- **GPU**: Tesla T4, 16 GB VRAM (Google Colab Environment)
- **Training cost**: ~$0.07 USD (Tổng cộng 12.1 phút huấn luyện @ $0.35/hr của cấu hình T4)
- **HF Hub link** (nếu Option B): N/A (Nộp theo Option C)

---

## 2. Rank Experiment Results

| Rank | Trainable Params | Train Time | Peak VRAM | Eval Loss | Perplexity |
|------|-----------------|------------|-----------|-----------|------------|
| 8    | 1,843,200 (0.06%)| 3.96 min   | 8.70 GB   | 1.5577    | 4.75       |
| 16   | 3,686,400 (0.12%)| 4.33 min   | 6.62 GB   | 1.5161    | 4.55       |
| 64   | 14,745,600 (0.48%)| 3.82 min  | 9.48 GB   | 1.4768    | 4.38       |
| Base | -               | -          | -         | -         | -          |

> [!NOTE]
> Peak VRAM đo được có sự biến thiên nhẹ giữa các lượt chạy do cơ chế dọn dẹp cache của PyTorch (`torch.cuda.empty_cache()` và garbage collection) cùng với việc kích hoạt gradient accumulation và các tối ưu hóa custom kernel từ Unsloth. Phiên bản r=16 có peak VRAM ghi nhận thấp hơn nhờ cơ chế phân bổ động tối ưu tại thời điểm thực thi đó.

---

## 3. Loss Curve Analysis
Biểu đồ loss curve cho cả 3 ranks được lưu trữ tại `results/loss_curve.png`.

- **Quan sát đường loss**:
  - Cả 3 cấu hình `r=8`, `r=16`, và `r=64` đều cho thấy xu hướng hội tụ rất tốt qua 3 epochs (69 steps).
  - Trọng số rank càng cao (`r=64`) giúp mô hình học nhanh hơn và đạt mức training loss thấp nhất ở step cuối cùng (~1.28 so với ~1.44 ở `r=8` và ~1.39 ở `r=16`).
  - Đường eval loss đạt kết quả tương ứng: `r=64` đạt 1.4768, `r=16` đạt 1.5161, và `r=8` đạt 1.5577.
- **Hiện tượng Overfitting**:
  - Không xuất hiện hiện tượng overfitting đáng kể. Khoảng cách giữa training loss (~1.28 đến ~1.44) và validation loss (~1.47 đến ~1.55) vẫn ở khoảng an toàn và có tính đồng hướng (cả hai cùng giảm dần).
  - Do tập dữ liệu chất lượng cao (Alpaca format được chuẩn hóa và loại bỏ các mẫu nhiễu) kết hợp với cấu hình dropout=0 và số epoch huấn luyện vừa phải (3 epochs), mô hình học được đặc trưng tổng quát tốt thay vì học vẹt dữ liệu.

---

## 4. Qualitative Comparison (5 examples)

### Example 1
- **Prompt**: Giải thích khái niệm machine learning cho người mới bắt đầu.
- **Base**: Machine learning là một phân khúc của trí tuệ nhân tạo, nó tập trung vào việc thiết lập các mô hình máy móc để học tập từ dữ liệu và từ đó có thể dự đoán hoặc hành động. Nhìn vào khía cạnh đơn giản, n...
- **Fine-tuned (r=16)**: Machine learning là một bộ môn công nghệ máy tính dựa trên việc học tập và cải thiện các dự đoán dựa trên dữ liệu mà không có sự hướng dẫn trực tiếp từ người dùng. Nó là một phần của AI (trí tuệ nhân ...
- **Nhận xét**: **Improved**. Bản dịch/hành văn của mô hình Fine-tuned tự nhiên hơn, sử dụng thuật ngữ chính xác trong tiếng Việt hiện đại và cấu trúc câu gãy gọn hơn.

### Example 2
- **Prompt**: Viết đoạn code Python tính số Fibonacci thứ n.
- **Base**: Để tính số Fibonacci thứ n, bạn có thể sử dụng hàm đệ quy hoặc vòng lặp. Đây là một đoạn mã Python cho phép bạn tính số Fibonacci thứ n:
```python
def fibonacci(n):
    if n <= 0:
        return "N p...
```
- **Fine-tuned (r=16)**: Để tính số Fibonacci thứ n, bạn có thể viết một đoạn code Python như sau:
```python
def fibonacci(n):
    if n < 0:
        raise ValueError("Input phải là một số nguyên dương.")
    elif n == 0:
        return 0
   ...
```
- **Nhận xét**: **Improved**. Bản Fine-tuned có xử lý ngoại lệ tốt hơn (sử dụng `raise ValueError` thay vì trả về chuỗi thông báo lỗi đơn thuần) và tối ưu hóa tốt về logic lập trình tiếng Việt.

### Example 3
- **Prompt**: Liệt kê 5 nguyên tắc thiết kế UI/UX.
- **Base**: 1. Thân thiện với người dùng: Mục đích của thiết kế UI/UX là cung cấp trải nghiệm người dùng thân thiện, dễ sử dụng và thân thiện. Điều này có thể được thể hiện thông qua việc sắp xếp bố cục, màu sắc,...
- **Fine-tuned (r=16)**: 1. Chuyển đổi: UI/UX thiết kế phải hướng tới việc giúp người dùng thực hiện hành động. 2. Thích ứng: UI/UX thiết kế phải thích ứng với nhiều loại thiết bị và kích thước màn hình. 3. Đơn giản: UI/UX th...
- **Nhận xét**: **Improved**. Mô hình gốc (Base) bị lặp từ ("thân thiện... thân thiện... thân thiện") và cấu trúc giải thích dài dòng. Bản Fine-tuned đưa ra các gạch đầu dòng cô đọng, hành văn chuyên nghiệp và đúng trọng tâm hơn.

### Example 4
- **Prompt**: Tóm tắt sự khác biệt giữa LoRA và QLoRA.
- **Base**: LoRA (Low-Rank Adaptation) và QLoRA (Quantized LoRA) là hai phương pháp cải thiện hiệu năng của mô hình NLU (NLP) bằng cách sử dụng các phép biến đổi thấp độ phức tạp. LoRA là phương pháp cải thiện hi...
- **Fine-tuned (r=16)**: LoRA (Layer-wise Adaptive Regularization Optimization) và QLoRA (Quantized LoRA) là hai phương pháp regularization được phát triển để cải thiện hiệu quả và độ ổn định của các mạng neural network trong...
- **Nhận xét**: **Same / Slightly degraded in terminology definitions**. Cả hai mô hình đều cố gắng giải thích khái niệm kĩ thuật. Tuy nhiên, định nghĩa chữ viết tắt của LoRA ở bản Fine-tuned bị sai thuật ngữ (đúng ra phải là *Low-Rank Adaptation* thay vì *Layer-wise Adaptive...*). Điều này cho thấy với tập dataset nhỏ (200 ví dụ dịch tiếng Việt), mô hình có thể bị "nhiễu" hoặc "hallucinate" về mặt định nghĩa thuật ngữ tiếng Anh nâng cao, mặc dù cấu trúc ngữ pháp tiếng Việt được cải thiện.

### Example 5
- **Prompt**: Phân biệt prompt engineering, RAG, và fine-tuning.
- **Base**: Prompt engineering, RAG (retrieval augmented generation), và fine-tuning là ba cách khác nhau để cải thiện hiệu suất của mô hình máy học. Prompt engineering là một kỹ thuật để cải thiện hiệu suất của ...
- **Fine-tuned (r=16)**: Prompt engineering, RAG và fine-tuning là ba kỹ thuật khác nhau được sử dụng trong lĩnh vực AI và tự động hóa. Prompt engineering là một kỹ thuật tập trung vào việc xây dựng câu lệnh (prompt) để giúp ...
- **Nhận xét**: **Improved**. Bản Fine-tuned phân tách rõ ràng và đưa ra định nghĩa chính xác, chuyên nghiệp hơn cho từng cấu phần AI, thích hợp làm câu trả lời cho hệ thống Chatbot trợ lý.

---

## 5. Conclusion về Rank Trade-off

Đối với tập dữ liệu tiếng Việt Alpaca quy mô nhỏ (200 ví dụ) này:

1. **Về mặt hiệu năng và ROI (Return on Investment)**:
   - Rank **r=16** mang lại tỷ lệ ROI tốt nhất. Nó cân bằng hoàn hảo giữa thời gian huấn luyện (4.33 phút trên T4), mức tiêu thụ tài nguyên VRAM vừa phải và cải thiện rõ rệt chất lượng văn bản so với cấu hình `r=8`.
   - Mặc dù `r=8` tiết kiệm tham số và cực kỳ gọn nhẹ, chất lượng câu trả lời và chỉ số Perplexity (4.75) vẫn chưa tối ưu bằng `r=16` (4.55).

2. **Hiện tượng giảm dần hiệu suất thu hoạch (Diminishing Returns)**:
   - Khi tăng rank từ `r=16` lên `r=64`, số lượng tham số huấn luyện tăng gấp 4 lần (từ 3.6M lên 14.7M) và peak VRAM tăng lên 9.48 GB, nhưng mức giảm Perplexity rất nhỏ (từ 4.55 xuống 4.38). Sự cải thiện này không mang lại nhiều giá trị khác biệt cho các câu trả lời thực tế (Qualitative), thể hiện rõ hiện tượng bão hòa (diminishing returns).

3. **Khuyến nghị cho Production Deployment**:
   - Nếu triển khai thực tế trên hệ thống sản phẩm lớn, tôi đề xuất lựa chọn **r=16**. Mức rank này cho phép lưu trữ và hoán đổi adapter rất nhanh (dung lượng checkpoint nhẹ), đồng thời đáp ứng tốt chất lượng hội thoại tiếng Việt chuẩn hóa mà không gây lãng phí bộ nhớ GPU hoặc tăng thời gian suy luận (inference latency).

---

## 6. What I Learned

- **Tầm quan trọng của Max Sequence Length**: Việc phân tích token length phân phối (p95) giúp xác định đúng `max_seq_length` (1024), tránh lãng phí VRAM cho đệm padding trống và tối ưu tốc độ train.
- **Cơ chế hoạt động của Rank và Alpha**: Việc cấu hình tỷ lệ $\alpha / r = 2$ là một best practice quan trọng giúp ổn định quá trình học và kiểm soát độ lớn của các cập nhật trọng số trong kỹ thuật adapter tuning.
- **Cách thức QLoRA tiết kiệm bộ nhớ**: Hiểu rõ hơn sự kết hợp giữa mô hình lượng tử hóa base 4-bit (NF4) của Unsloth cùng với việc huấn luyện adapter ở kiểu số thực 16-bit, kết hợp với các tối ưu hóa gradient checkpointing để huấn luyện các mô hình lớn 3B một cách trơn tru trên GPU giá rẻ Tesla T4.
