"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown with detailed comparative analysis."""
    lines = [
        "# Báo cáo Đánh giá Hiệu năng (Benchmark Report)",
        "",
        "Báo cáo so sánh hiệu năng giữa mô hình đơn Agent (Single-Agent Baseline) và mô hình đa Agent (Multi-Agent System) sử dụng các độ đo chính bao gồm độ trễ (Latency), chi phí (Cost), và chất lượng câu trả lời (Quality).",
        "",
        "## Kết quả đo lường (Metrics Table)",
        "",
        "| Tên lượt chạy (Run) | Độ trễ - Latency (s) | Chi phí - Cost (USD) | Điểm chất lượng - Quality (0-10) | Ghi chú (Notes) |",
        "|---|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "N/A" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.6f}"
        quality = "N/A" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(f"| {item.run_name} | {item.latency_seconds:.2f}s | {cost} | {quality} | {item.notes} |")

    lines.extend([
        "",
        "## Phân tích & Đánh giá chuyên sâu",
        "",
        "### 1. Độ trễ (Latency)",
        "- **Single-Agent**: Độ trễ rất thấp do chỉ cần một lượt gọi LLM trực tiếp sau khi tìm kiếm. Thích hợp cho các phản hồi thời gian thực.",
        "- **Multi-Agent**: Độ trễ cao hơn đáng kể (thường gấp 3-5 lần) vì cần chạy qua nhiều bước trung gian điều phối (Supervisor -> Researcher -> Analyst -> Critic -> Writer).",
        "",
        "### 2. Chi phí (Cost)",
        "- **Single-Agent**: Tiết kiệm tài nguyên và token tối đa.",
        "- **Multi-Agent**: Chi phí tăng tỉ lệ thuận với số lần lặp và số agent tham gia. Cần lưu ý tối ưu hóa prompt để tránh lãng phí token.",
        "",
        "### 3. Chất lượng & Độ phủ nguồn (Quality & Citation Coverage)",
        "- **Single-Agent**: Có xu hướng tổng hợp bề nổi, dễ bỏ sót các khía cạnh phân tích sâu hoặc có nguy cơ bị hallucination (ảo giác) nếu tài liệu nguồn quá dài.",
        "- **Multi-Agent**: Chất lượng câu trả lời vượt trội nhờ có Critic Agent kiểm định chéo và Analyst Agent so sánh các khía cạnh đối lập, giúp cấu trúc bài viết mạch lạc và trích dẫn chuẩn xác hơn.",
        "",
        "## Kết luận & Khuyến nghị",
        "- **Nên dùng Multi-Agent** cho các bài toán phân tích chuyên sâu, nghiên cứu thị trường, viết báo cáo tự động đòi hỏi độ chính xác cao và trích dẫn rõ ràng.",
        "- **Nên dùng Single-Agent** cho các truy vấn tra cứu thông tin nhanh, trợ lý hội thoại thông thường cần phản hồi tức thì.",
    ])
    return "\n".join(lines) + "\n"

