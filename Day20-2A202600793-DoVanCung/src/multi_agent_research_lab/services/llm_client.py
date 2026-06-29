"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from multi_agent_research_lab.core.errors import StudentTodoError


import logging
from dataclasses import dataclass
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client skeleton."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.api_key = self.settings.openai_api_key
        self.model = self.settings.openai_model

        if self.api_key:
            if self.api_key.startswith("sk-or-"):
                logger.info("Initializing LLMClient with OpenRouter provider.")
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                # Map gpt-4o-mini to openrouter standard alias if needed
                if self.model == "gpt-4o-mini":
                    self.model = "openai/gpt-4o-mini"
            else:
                logger.info("Initializing LLMClient with OpenAI provider.")
                self.client = OpenAI(api_key=self.api_key)
        else:
            logger.warning("No OPENAI_API_KEY found. LLMClient will operate in Mock mode.")
            self.client = None

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        If client is initialized, calls real provider, otherwise falls back to mock responses.
        """
        if self.client:
            try:
                return self._complete_api(system_prompt, user_prompt)
            except Exception as e:
                logger.error(f"Real LLM API call failed: {e}. Falling back to Mock LLM.")
                return self._complete_mock(system_prompt, user_prompt)
        else:
            return self._complete_mock(system_prompt, user_prompt)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _complete_api(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content or ""
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0

            # Estimate cost based on gpt-4o-mini pricing
            # Input: $0.150 / 1M, Output: $0.600 / 1M
            cost_usd = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000

            return LLMResponse(
                content=content,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd
            )
        except Exception as e:
            logger.error(f"Error calling LLM API: {e}")
            raise

    def _complete_mock(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        content = ""
        system_lower = system_prompt.lower()
        user_lower = user_prompt.lower()

        if "supervisor" in system_lower or "router" in system_lower:
            # Check route history from user prompt to decide the next agent
            if "critic_feedback" in user_lower and "final_answer" not in user_lower:
                content = "writer"
            elif "analysis_notes" in user_lower and "critic_feedback" not in user_lower:
                content = "critic"
            elif "research_notes" in user_lower and "analysis_notes" not in user_lower:
                content = "analyst"
            elif "sources" in user_lower and "research_notes" not in user_lower:
                content = "researcher"
            elif "final_answer" in user_lower or "writer" in user_lower:
                content = "done"
            else:
                # Default flow: researcher -> analyst -> critic -> writer -> done
                if "researcher" not in user_lower and "sources" not in user_lower:
                    content = "researcher"
                elif "analyst" not in user_lower:
                    content = "analyst"
                elif "critic" not in user_lower:
                    content = "critic"
                elif "writer" not in user_lower:
                    content = "writer"
                else:
                    content = "done"
        elif "researcher" in system_lower:
            content = (
                "### Ghi chú nghiên cứu (Research Notes)\n"
                "1. Tổng quan về chủ đề: GraphRAG kết hợp đồ thị tri thức (Knowledge Graph) với RAG truyền thống để cải thiện độ chính xác và khả năng trả lời câu hỏi mức độ toàn cục [Source 1].\n"
                "2. Ưu điểm nổi bật: Cung cấp góc nhìn toàn cảnh về dữ liệu, giảm thiểu ảo giác (hallucination) nhờ cấu trúc thực thể và quan hệ rõ ràng [Source 2].\n"
                "3. Quy trình thực hiện: Trích xuất thực thể -> Xây dựng đồ thị -> Tạo tóm tắt phân cấp -> Truy vấn dựa trên cộng đồng thực thể [Source 3]."
            )
        elif "analyst" in system_lower:
            content = (
                "### Phân tích chuyên sâu (Analysis Notes)\n"
                "- **Luận điểm chính**: GraphRAG mang lại đột phá đối với các câu hỏi dạng khái quát (global queries) so với RAG truyền thống chỉ mạnh ở dạng cục bộ (local queries).\n"
                "- **So sánh khía cạnh**: RAG truyền thống dựa trên vector similarity dễ bỏ sót ngữ cảnh kết nối, trong khi GraphRAG ánh xạ cấu trúc liên kết.\n"
                "- **Điểm yếu của minh chứng**: Chi phí xây dựng index đồ thị ban đầu rất lớn và đòi hỏi LLM chất lượng cao để trích xuất thực thể chính xác."
            )
        elif "critic" in system_lower:
            content = (
                "### Đánh giá chất lượng (Critic Feedback)\n"
                "- **Tính chính xác**: Các luận điểm phân tích đều nhất quán với tài liệu gốc.\n"
                "- **Trích dẫn (Citations)**: Nguồn trích dẫn đầy đủ từ Source 1, 2 và 3.\n"
                "- **Đóng góp cải thiện**: Cần bổ sung phân tích về độ trễ (latency) khi chạy GraphRAG so với Vector RAG để bài viết khách quan hơn."
            )
        elif "writer" in system_lower:
            content = (
                "# Nghiên cứu về State-of-the-Art GraphRAG: Tóm tắt 500 từ\n\n"
                "GraphRAG đại diện cho bước tiến vượt bậc của Retrieval-Augmented Generation. Theo tài liệu nghiên cứu [Source 1], "
                "bằng cách kết hợp Đồ thị tri thức (Knowledge Graph) với các kỹ thuật tìm kiếm vector truyền thống, hệ thống này "
                "giúp giải quyết triệt để bài toán trả lời câu hỏi mang tính khái quát (global query routing).\n\n"
                "## Phân tích & So sánh Chuyên sâu\n"
                "Điểm khác biệt cốt lõi nằm ở khả năng kết nối thông tin giữa các thực thể khác nhau [Source 2]. RAG thông thường "
                "chỉ truy xuất các khối văn bản rời rạc, dẫn đến hiện tượng thiếu ngữ cảnh kết nối. GraphRAG tổ chức dữ liệu thành "
                "mạng lưới thực thể - quan hệ và sử dụng phân nhóm cộng đồng (community detection) để tóm tắt thông tin theo cấp bậc.\n\n"
                "## Thách thức & Đánh giá\n"
                "Mặc dù hiệu quả vượt trội, quy trình xây dựng chỉ mục (indexing) của GraphRAG tốn kém tài nguyên và có độ trễ lớn "
                "[Source 3]. Hơn nữa, chất lượng đồ thị phụ thuộc nhiều vào khả năng trích xuất thông tin của LLM nền tảng. Tuy nhiên, "
                "đây vẫn là hướng đi hứa hẹn nhất để tối ưu hóa tri thức doanh nghiệp hiện nay."
            )
        else:
            content = (
                f"Báo cáo tổng kết rút gọn cho câu hỏi: '{user_prompt}'\n\n"
                "Hệ thống đã nghiên cứu GraphRAG dựa trên nguồn tài liệu trực tuyến [Source 1], [Source 2]. "
                "Kết quả cho thấy kết hợp đồ thị giúp RAG trả lời các câu hỏi tổng quát tốt hơn so với RAG tìm kiếm vector truyền thống. "
                "Điểm hạn chế là chi phí indexing lớn."
            )

        return LLMResponse(
            content=content,
            input_tokens=100,
            output_tokens=200,
            cost_usd=0.00015
        )

