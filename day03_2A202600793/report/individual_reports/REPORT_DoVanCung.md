# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Do Van Cung
- **Student ID**: 2A202600793
- **Date**: 2026-06-01

---

## I. Technical Contribution

- **Modules Implemented**:
  - `src/agent/agent.py`: ReAct loop, final-answer detection, action parsing, tool execution, error logging.
  - `src/tools/ecommerce_tools.py`: Product lookup, coupon discount, shipping calculator, safe arithmetic calculator.
  - `src/chatbot.py`: Direct chatbot baseline.
  - `src/core/fake_provider.py`: Deterministic local provider for offline tests and repeatable evaluation.
  - `scripts/evaluate.py`: Chatbot-vs-agent evaluation runner.
  - `tests/test_agent.py`: Offline tests for full ReAct flow and failure handling.

- **Code Highlights**:
  - The agent enforces `Action: tool_name({...})` with JSON arguments.
  - The calculator avoids unsafe `eval` by parsing arithmetic with `ast`.
  - Error cases are structured as telemetry events: `PARSER_ERROR`, `HALLUCINATED_TOOL`, `TOOL_ARGUMENT_ERROR`, `TOOL_RUNTIME_ERROR`, and `timeout`.

- **Documentation**:
  - The group report explains the architecture, tool inventory, evaluation results, failure cases, and production-readiness notes.

---

## II. Debugging Case Study

- **Problem Description**: A direct chatbot cannot solve a multi-step order total because it does not know product price, stock, coupon discount, shipping cost, or arithmetic result.
- **Log Source**: `logs/2026-06-01.log`
- **Example Input**: "I want 2 headphones with coupon SAVE10 shipped to Hanoi. What is the total?"
- **Diagnosis**:
  - The chatbot responded with an estimate.
  - The agent solved the task by calling tools in sequence and feeding each observation back into the prompt.
- **Solution**:
  - Implemented ReAct scratchpad handling in `src/agent/agent.py`.
  - Added precise tool schemas and a v2 system prompt with strict JSON action format.
  - Added `max_steps` to prevent infinite loops.

Final trace:
1. `get_product_info({"item_name": "headphones"})`
2. `get_discount({"coupon_code": "SAVE10"})`
3. `calc_shipping({"weight_kg": 1.0, "destination": "Hanoi"})`
4. `calculator({"expression": "2*80*(1-10/100)+5"})`
5. `Final Answer: The final total is $149.00.`

---

## III. Personal Insights: Chatbot vs ReAct

1. **Reasoning**: The `Thought` step forces the model to decompose the task before answering. This makes multi-step work easier to inspect and debug.
2. **Reliability**: The agent is stronger when facts must come from tools, but it can be worse for simple questions if the prompt pushes it to call tools unnecessarily.
3. **Observation**: Tool observations are the key difference. The agent does not need to guess; it can use returned data to choose the next step.

---

## IV. Future Improvements

- **Scalability**: Move the ReAct loop into a state-machine framework such as LangGraph for retries, branching, and memory.
- **Safety**: Add argument validation with Pydantic schemas before executing tools.
- **Performance**: Cache repeated tool calls and track cost per successful task.
- **Evaluation**: Expand from 3 local cases to a larger dataset with success rate, token cost, latency percentiles, and failure categories.
