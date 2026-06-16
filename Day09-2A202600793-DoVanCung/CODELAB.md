# Codelab: Xây Dựng Hệ Thống Multi-Agent với A2A Protocol

**Thời gian:** 2 giờ  
**Ngôn ngữ:** Python 3.11+  
**Công nghệ:** LangGraph, LangChain, A2A SDK

## Mục Tiêu Học Tập

Sau khi hoàn thành codelab này, bạn sẽ:
- Hiểu cách LLM hoạt động từ cơ bản đến nâng cao
- Biết cách tích hợp tools và RAG vào LLM
- Xây dựng được single agent với ReAct pattern
- Tạo multi-agent system với LangGraph
- Triển khai distributed agents với A2A protocol

## Chuẩn Bị

### Yêu Cầu Hệ Thống
- Python 3.11 trở lên
- [uv](https://docs.astral.sh/uv/) package manager
- API key từ [OpenRouter](https://openrouter.ai)

### Cài Đặt

```bash
# Clone repository
git clone <repo-url>
cd legal_multiagent

# Cài đặt dependencies
uv sync

# Cấu hình environment
cp .env.example .env
# Sửa file .env, thêm OPENROUTER_API_KEY của bạn
```

---

## Phần 1: Direct LLM Calling (20 phút)

### Lý Thuyết

LLM (Large Language Model) ở dạng cơ bản nhất là một API nhận input text và trả về output text. Không có memory, không có tools, chỉ dựa vào training data.

**Ưu điểm:**
- Đơn giản, dễ implement
- Phản hồi nhanh

**Nhược điểm:**
- Không có kiến thức real-time
- Không thể tra cứu database
- Không có context giữa các lần gọi

### Thực Hành

**Bước 1:** Chạy demo Stage 1

```bash
uv run python stages/stage_1_direct_llm/main.py
```

**Bước 2:** Đọc và hiểu code

Mở file `stages/stage_1_direct_llm/main.py` và trả lời:

1. LLM được khởi tạo như thế nào? (Tìm hàm `get_llm()`)
2. Message được gửi đến LLM có cấu trúc gì?
3. Tại sao cần có `SystemMessage` và `HumanMessage`?

**Đáp án:**

1. LLM được khởi tạo bằng hàm `get_llm()`:

```python
llm = get_llm()
```

Hàm này nằm trong `common/llm.py`, tạo một `ChatOpenAI` client dùng model và API key từ biến môi trường OpenRouter.

2. Message gửi đến LLM là một list gồm `SystemMessage` và `HumanMessage`:

```python
messages = [
    SystemMessage(content="..."),
    HumanMessage(content=QUESTION),
]
```

3. `SystemMessage` dùng để đặt vai trò, quy tắc và cách trả lời cho LLM. `HumanMessage` là câu hỏi thật của người dùng. Tách ra như vậy giúp LLM hiểu đâu là chỉ dẫn hệ thống và đâu là nội dung cần trả lời.

**Bài Tập 1.1:** Thay đổi câu hỏi

Sửa biến `QUESTION` thành câu hỏi pháp lý khác (tiếng Việt hoặc tiếng Anh) và chạy lại.

**Bài Tập 1.2:** Thêm temperature control

Thêm parameter `temperature=0.3` vào hàm `get_llm()` trong `common/llm.py` để làm output ổn định hơn.

---

## Phần 2: LLM + RAG & Tools (30 phút)

### Lý Thuyết

**RAG (Retrieval-Augmented Generation):** Cho phép LLM tra cứu knowledge base trước khi trả lời.

**Tools:** Các function mà LLM có thể gọi để thực hiện tác vụ cụ thể (tính toán, query database, gọi API).

**Function Calling Flow:**
1. LLM nhận câu hỏi + danh sách tools
2. LLM quyết định gọi tool nào (hoặc không gọi)
3. Tool được execute, trả về kết quả
4. LLM nhận kết quả và tạo câu trả lời cuối cùng

### Thực Hành

**Bước 1:** Chạy demo Stage 2

```bash
uv run python stages/stage_2_rag_tools/main.py
```

**Bước 2:** Phân tích code

Mở `stages/stage_2_rag_tools/main.py` và tìm:

1. Hàm `@tool` decorator được dùng ở đâu?
2. `LEGAL_KNOWLEDGE` được cấu trúc như thế nào?
3. LLM được bind với tools ra sao? (Tìm `.bind_tools()`)

**Đáp án:**

1. `@tool` được dùng trước các hàm muốn cho LLM gọi, ví dụ:

```python
@tool
def search_legal_database(query: str) -> str:
```

```python
@tool
def calculate_damages(breach_type: str, contract_value: float) -> str:
```

```python
@tool
def check_statute_of_limitations(case_type: str) -> str:
```

2. `LEGAL_KNOWLEDGE` là một list gồm nhiều dictionary. Mỗi dictionary có:

```python
{
    "id": "...",
    "keywords": [...],
    "text": "..."
}
```

Trong đó `id` là mã nguồn kiến thức, `keywords` là từ khóa tìm kiếm, và `text` là nội dung pháp lý.

3. LLM được bind với tools bằng `.bind_tools()`:

```python
llm = get_llm()
llm_with_tools = llm.bind_tools(TOOLS)
```

Danh sách tool hiện tại:

```python
TOOLS = [search_legal_database, calculate_damages, check_statute_of_limitations]
```

**Bài Tập 2.1:** Thêm knowledge base entry

Thêm một entry mới vào `LEGAL_KNOWLEDGE` về luật lao động:

```python
{
    "id": "labor_law",
    "keywords": ["lao động", "sa thải", "hợp đồng lao động", "labor", "termination"],
    "text": (
        "Theo Bộ luật Lao động Việt Nam 2019, người sử dụng lao động có thể "
        "đơn phương chấm dứt hợp đồng trong các trường hợp: (1) người lao động "
        "thường xuyên không hoàn thành công việc; (2) bị ốm đau, tai nạn đã điều trị "
        "12 tháng chưa khỏi; (3) thiên tai, hỏa hoạn; (4) người lao động đủ tuổi nghỉ hưu."
    ),
}
```

**Bài Tập 2.2:** Tạo tool mới

Tạo một tool `@tool` mới tên `check_statute_of_limitations` nhận vào `case_type` (string) và trả về thời hiệu khởi kiện:

```python
@tool
def check_statute_of_limitations(case_type: str) -> str:
    """Kiểm tra thời hiệu khởi kiện theo loại vụ án.
    
    Args:
        case_type: Loại vụ án (contract, tort, property)
    """
    limits = {
        "contract": "4 năm (UCC § 2-725)",
        "tort": "2-3 năm tùy bang",
        "property": "5 năm",
    }
    return limits.get(case_type.lower(), "Không xác định")
```

Thêm tool này vào danh sách tools và test.

---

## Phần 3: Single Agent với ReAct (25 phút)

### Lý Thuyết

**ReAct Pattern:** Reasoning + Acting

Agent tự động lặp lại chu trình:
1. **Think:** Suy nghĩ cần làm gì
2. **Act:** Gọi tool
3. **Observe:** Nhận kết quả
4. Lặp lại cho đến khi có câu trả lời cuối cùng

LangGraph cung cấp `create_react_agent` để tự động hóa pattern này.

### Thực Hành

**Bước 1:** Chạy demo Stage 3

```bash
uv run python stages/stage_3_single_agent/main.py
```

**Bước 2:** Quan sát output

Chú ý cách agent tự động:
- Quyết định tool nào cần gọi
- Gọi nhiều tools liên tiếp
- Tổng hợp kết quả

**Bước 3:** Đọc code

Mở `stages/stage_3_single_agent/main.py`:

1. Tìm `create_react_agent()` — đây là magic function
2. So sánh với Stage 2: không còn manual tool loop
3. Xem `agent_executor.invoke()` — chỉ cần gọi một lần

**Đáp án:**

1. `create_react_agent()` là hàm của LangGraph dùng để tạo agent theo mẫu ReAct (Reasoning + Acting). Agent có thể tự quyết định cần gọi tool nào, đọc kết quả tool, rồi tiếp tục gọi tool khác nếu cần.

Trong file `stages/stage_3_single_agent/main.py`, agent được tạo bằng:

```python
graph = create_react_agent(model=llm, tools=TOOLS, prompt=SYSTEM_PROMPT)
```

2. So với Stage 2, Stage 3 không còn manual tool loop vì `create_react_agent()` đã tự động hóa vòng lặp gọi tool. Ở Stage 2, code phải tự kiểm tra `response.tool_calls`, tự chạy tool, rồi đưa kết quả về lại LLM. Ở Stage 3, agent tự làm các bước Think, Act, Observe cho đến khi đủ thông tin để trả lời.

3. Trong hướng dẫn có nhắc `agent_executor.invoke()`, nhưng file hiện tại dùng LangGraph streaming thay cho `invoke()` trực tiếp:

```python
async for chunk in graph.astream(inputs, stream_mode="updates"):
```

Cách này vẫn cùng mục đích: chỉ cần đưa input vào agent một lần, agent sẽ tự chạy qua các bước suy nghĩ, gọi tool, quan sát kết quả và sinh câu trả lời cuối cùng.

**Bài Tập 3.1:** Thêm tool tra cứu án lệ

```python
@tool
def search_case_law(keywords: str) -> str:
    """Tìm kiếm án lệ theo từ khóa.
    
    Args:
        keywords: Từ khóa tìm kiếm
    """
    cases = {
        "breach": "Hadley v. Baxendale (1854) - Consequential damages",
        "negligence": "Donoghue v. Stevenson (1932) - Duty of care",
        "contract": "Carlill v. Carbolic Smoke Ball Co (1893) - Unilateral contract",
    }
    for key, case in cases.items():
        if key in keywords.lower():
            return case
    return "Không tìm thấy án lệ phù hợp"
```

Thêm vào tools list và test với câu hỏi về breach of contract.

**Bài Tập 3.2:** Debug agent reasoning

Thêm `verbose=True` vào `create_react_agent()` để xem chi tiết quá trình suy nghĩ của agent.

---

## Phần 4: Multi-Agent In-Process (30 phút)

### Lý Thuyết

**Multi-Agent System:** Nhiều agents chuyên môn hóa cùng làm việc.

**Ưu điểm:**
- Mỗi agent tập trung vào domain riêng
- Có thể chạy song song (parallel execution)
- Dễ maintain và mở rộng

**LangGraph StateGraph:**
- Định nghĩa state (dữ liệu chia sẻ giữa các nodes)
- Tạo nodes (các bước xử lý)
- Định nghĩa edges (luồng điều khiển)

**Send API:** Cho phép dispatch nhiều tasks song song.

### Thực Hành

**Bước 1:** Chạy demo Stage 4

```bash
uv run python stages/stage_4_milti_agent/main.py
```

**Bước 2:** Phân tích kiến trúc

Mở `stages/stage_4_milti_agent/main.py`:

1. Tìm `class State(TypedDict)` — đây là shared state
2. Tìm các agent functions: `law_agent`, `tax_agent`, `compliance_agent`
3. Tìm `Send()` API — dispatch parallel tasks
4. Xem `graph.add_node()` và `graph.add_edge()`

**Đáp án:**

1. Shared state nằm trong `class LegalState(TypedDict)` ở `stages/stage_4_milti_agent/main.py`. State này chứa dữ liệu dùng chung giữa các node như `question`, `law_analysis`, `tax_result`, `compliance_result`, `privacy_result`, và `final_answer`.

2. Các agent/node chính trong Stage 4 gồm:

```python
analyze_law
call_tax_specialist
call_compliance_specialist
call_privacy_specialist
aggregate
```

3. `Send()` API được dùng trong hàm routing để dispatch nhiều specialist agents song song:

```python
sends.append(Send("call_tax_specialist", state))
sends.append(Send("call_compliance_specialist", state))
sends.append(Send("call_privacy_specialist", state))
```

4. Graph được khai báo bằng `graph.add_node()` để thêm node và `graph.add_edge()` hoặc `graph.add_conditional_edges()` để nối luồng xử lý. Luồng chính là:

```text
analyze_law -> check_routing -> specialist agents -> aggregate -> END
```

**Bước 3:** Vẽ graph

```python
# Thêm vào cuối file main.py
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png()))
```

**Bài Tập 4.1:** Thêm agent mới

Tạo `privacy_agent` chuyên về GDPR và privacy law:

```python
def privacy_agent(state: State) -> dict:
    """Agent chuyên về luật bảo vệ dữ liệu cá nhân."""
    llm = get_llm()
    
    prompt = f"""Bạn là chuyên gia về GDPR và luật bảo vệ dữ liệu cá nhân.
    
Câu hỏi gốc: {state['question']}
Phân tích pháp lý: {state.get('law_analysis', 'N/A')}

Hãy phân tích các vấn đề về privacy và GDPR (nếu có).
"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"privacy_analysis": response.content}
```

Thêm node này vào graph và kết nối với `aggregate_results`.

**Đã làm:**

Trong `stages/stage_4_milti_agent/main.py`, đã thêm privacy specialist:

```python
async def call_privacy_specialist(state: LegalState) -> dict:
```

Agent này phân tích các vấn đề về GDPR, CCPA/CPRA, consent, data protection, privacy rights, breach notification và data governance. Kết quả được trả về qua field:

```python
privacy_result
```

**Bài Tập 4.2:** Implement conditional routing

Sửa `check_routing` để chỉ gọi privacy_agent khi câu hỏi có từ khóa "data", "privacy", "gdpr":

```python
def check_routing(state: State) -> list[Send]:
    question_lower = state["question"].lower()
    tasks = []
    
    if any(kw in question_lower for kw in ["tax", "irs", "thuế"]):
        tasks.append(Send("tax_agent", state))
    
    if any(kw in question_lower for kw in ["compliance", "sec", "regulation"]):
        tasks.append(Send("compliance_agent", state))
    
    if any(kw in question_lower for kw in ["data", "privacy", "gdpr", "dữ liệu"]):
        tasks.append(Send("privacy_agent", state))
    
    return tasks if tasks else [Send("aggregate_results", state)]
```

**Đã làm:**

Trong `stages/stage_4_milti_agent/main.py`, routing đã kiểm tra keyword:

```python
needs_privacy = any(
    kw in question_lower
    for kw in ["data", "privacy", "gdpr", "ccpa", "consent", "user", "dữ liệu"]
)
```

Nếu `needs_privacy=True`, graph sẽ gửi task đến:

```python
Send("call_privacy_specialist", state)
```

Sau đó `call_privacy_specialist` được nối về `aggregate` để tổng hợp cùng các kết quả khác.

---

## Phần 5: Distributed A2A System (15 phút)

### Lý Thuyết

**A2A (Agent-to-Agent) Protocol:** Chuẩn giao tiếp giữa các agents qua HTTP.

**Khác biệt với Stage 4:**
- Mỗi agent là một service độc lập
- Giao tiếp qua HTTP thay vì in-process
- Dynamic discovery qua Registry
- Có thể scale từng agent riêng biệt

**Kiến trúc:**
```
Registry (10000) ← agents register on startup
    ↓
Customer Agent (10100) → Law Agent (10101)
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
            Tax Agent (10102)   Compliance Agent (10103)
```

### Thực Hành

**Bước 1:** Khởi động toàn bộ hệ thống

```bash
./start_all.sh
```

Chờ ~10 giây để tất cả services khởi động.

**Bước 2:** Test hệ thống

```bash
uv run python test_client.py
```

**Bước 3:** Quan sát logs

Mở 5 terminal tabs và xem logs của từng service:
- Registry: port 10000
- Customer Agent: port 10100
- Law Agent: port 10101
- Tax Agent: port 10102
- Compliance Agent: port 10103

**Bài Tập 5.1:** Trace request flow

Trong logs, tìm `trace_id` và theo dõi request đi qua các agents. Vẽ sequence diagram.

**Đáp án:**

Request flow của Stage 5:

```text
User/test_client
  -> Customer Agent :10100
  -> Registry :10000 để discover Law Agent
  -> Law Agent :10101
  -> Registry :10000 để discover Tax/Compliance Agent nếu cần
  -> Tax Agent :10102
  -> Compliance Agent :10103
  -> Law Agent tổng hợp
  -> Customer Agent trả kết quả cuối
```

Sequence diagram dạng text:

```text
test_client -> customer_agent: gửi câu hỏi
customer_agent -> registry: discover("legal_question")
registry -> customer_agent: trả endpoint law_agent
customer_agent -> law_agent: delegate qua A2A
law_agent -> registry: discover("tax_question"), discover("compliance_question")
law_agent -> tax_agent: gọi phân tích thuế
law_agent -> compliance_agent: gọi phân tích compliance
tax_agent -> law_agent: trả tax analysis
compliance_agent -> law_agent: trả compliance analysis
law_agent -> customer_agent: trả phân tích tổng hợp
customer_agent -> test_client: trả final answer
```

**Bài Tập 5.2:** Test dynamic discovery

1. Dừng Tax Agent (Ctrl+C)
2. Chạy lại `test_client.py`
3. Quan sát lỗi và cách hệ thống xử lý

**Đáp án:**

Khi dừng Tax Agent, Registry vẫn có thể còn endpoint đã đăng ký nhưng service ở port `10102` không phản hồi. Khi Law Agent cố gọi Tax Agent, request tax có thể lỗi connection hoặc timeout. Hệ thống vẫn cho thấy lợi ích của dynamic discovery: các agent không hardcode URL trực tiếp trong business logic, mà hỏi Registry để tìm service phù hợp.

Trong production nên xử lý thêm:

- health check để Registry biết agent nào đang sống
- timeout ngắn cho request A2A
- retry với backoff
- fallback để vẫn trả lời phần legal/compliance nếu tax agent lỗi

**Bài Tập 5.3:** Modify agent behavior

Sửa `tax_agent/graph.py`, thay đổi system prompt để agent trả lời ngắn gọn hơn. Restart tax agent và test lại.

**Đáp án:**

Cách sửa: mở `tax_agent/graph.py`, tìm system prompt của Tax Agent, thêm yêu cầu như:

```text
Keep your answer concise, use bullet points, and stay under 150 words.
```

Sau đó restart Tax Agent và chạy lại:

```bash
uv run python test_client.py
```

Kết quả mong đợi: phần trả lời của Tax Agent ngắn hơn, ít giải thích lan man hơn, nhưng vẫn giữ các ý chính về IRS, penalty, FBAR/FATCA hoặc tax fraud nếu liên quan.

---

## Phần 6: Tổng Kết & Mở Rộng (10 phút)

### So Sánh 5 Stages

| Stage | Pattern | Use Case | Complexity |
|---|---|---|---|
| 1 | Direct LLM | Câu hỏi đơn giản, không cần tools | ⭐ |
| 2 | LLM + Tools | Cần tra cứu data hoặc tính toán | ⭐⭐ |
| 3 | ReAct Agent | Tự động orchestration, multi-step | ⭐⭐⭐ |
| 4 | Multi-Agent | Nhiều domains, parallel processing | ⭐⭐⭐⭐ |
| 5 | Distributed A2A | Production, scalable, fault-tolerant | ⭐⭐⭐⭐⭐ |

### Câu Hỏi Ôn Tập

1. Khi nào nên dùng single agent thay vì multi-agent?
2. Ưu điểm của A2A protocol so với gRPC hoặc REST thông thường?
3. Làm thế nào để prevent infinite delegation loops trong A2A?
4. Tại sao cần Registry service? Có thể hardcode URLs không?

**Đáp án:**

1. Nên dùng single agent khi bài toán nhỏ, ít domain chuyên môn, không cần parallel processing và muốn hệ thống đơn giản, dễ debug. Ví dụ: một câu hỏi pháp lý đơn giản chỉ cần tra cứu một knowledge base hoặc gọi vài tool.

2. A2A protocol phù hợp hơn cho giao tiếp giữa agents vì nó chuẩn hóa cách agent mô tả capability, nhận task, trả response và phối hợp với nhau. So với REST/gRPC thông thường, A2A tập trung vào workflow agent-to-agent, delegation, discovery và message/task semantics thay vì chỉ gọi endpoint kỹ thuật.

3. Để prevent infinite delegation loops trong A2A, có thể dùng `MAX_DELEGATION_DEPTH`, truyền `trace_id`/`context_id`, lưu lịch sử agent đã gọi, đặt timeout, và từ chối delegate tiếp khi vượt quá độ sâu hoặc gặp lại cùng một agent/task.

4. Registry service cần để agents tự đăng ký capability và tự discover nhau runtime. Có thể hardcode URLs trong demo nhỏ, nhưng không nên dùng cho hệ thống thật vì khó scale, khó thay đổi port/service, khó health check và dễ coupling giữa các agents.

### Bài Tập Nâng Cao (Tự Học)

**Challenge 1:** Thêm memory/conversation history

Implement conversation memory để agent nhớ các câu hỏi trước đó.

**Challenge 2:** Add authentication

Thêm API key authentication cho các A2A endpoints.

**Challenge 3:** Implement retry logic

Khi một agent fail, tự động retry với exponential backoff.

**Challenge 4:** Monitoring & Observability

Tích hợp LangSmith hoặc Prometheus để monitor agent performance.

---

## Tài Liệu Tham Khảo

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [A2A Protocol Spec](https://github.com/google/A2A)
- [OpenRouter API](https://openrouter.ai/docs)
- Architecture diagrams: `docs/*.svg`

## Hỗ Trợ

Nếu gặp vấn đề:
1. Check `.env` file có đúng API key không
2. Đảm bảo tất cả ports (10000-10103) không bị chiếm
3. Xem logs trong terminal để debug
4. Đọc error messages cẩn thận — thường có hint rõ ràng

---

## **Bài Tập Cộng Điểm:**
Sau khi chạy full Stage 5 (test_client.py) trả lời 2 câu hỏi:
- Latency (Tổng thời gian trả lời 1 câu hỏi của hệ thống) là bao nhiêu giây?
- Đề xuất phương án giảm latency và demo + show thời gian xử lý đã giảm được khi apply phương án?

**Trả lời:**

Hiện tại chưa đo được latency thực tế trên máy này vì môi trường chưa chạy được `uv` và `.venv` đang trỏ tới Python không tồn tại. Khi môi trường chạy được, đo latency bằng cách thêm timer quanh request trong `test_client.py`:

```python
import time

start = time.perf_counter()
# call customer agent
elapsed = time.perf_counter() - start
print(f"Latency: {elapsed:.2f}s")
```

Phương án giảm latency:

1. Chạy Tax Agent và Compliance Agent song song thay vì tuần tự.
2. Cache kết quả `registry.discover(...)` để giảm số lần gọi Registry.
3. Giảm độ dài system prompt và giới hạn số token trả lời.
4. Dùng timeout/retry hợp lý để tránh chờ agent lỗi quá lâu.
5. Dùng model nhanh hơn cho routing hoặc các tác vụ phụ.

Trong repo này, Stage 4 đã minh họa hướng giảm latency quan trọng nhất: dùng LangGraph `Send` API để dispatch các specialist agents song song. Với Stage 5, áp dụng cùng ý tưởng bằng cách gọi các A2A specialist agents bằng `asyncio.gather(...)` ở Law Agent.

**Chúc các bạn học tốt! 🚀**
