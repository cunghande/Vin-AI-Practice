from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool

from src.core.llm import build_chat_model, normalize_content
from src.core.schemas import (
    AgentResult,
    CalculateTotalsInput,
    DiscountInput,
    ListProductsInput,
    OrderLineInput,
    ProductDetailInput,
    SaveOrderInput,
    ToolCallRecord,
)
from src.utils.data_store import OrderDataStore

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "artifacts" / "orders"


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    compact = re.sub(r"[^a-zA-Z0-9]+", " ", stripped.lower())
    return re.sub(r"\s+", " ", compact).strip()


def build_system_prompt(today: str | None = None) -> str:
    current_day = today or "2026-06-01"
    return f"""
Bạn là OrderDesk, trợ lý tạo đơn hàng cho nhà bán lẻ điện tử. Hôm nay là {current_day}.

Quy tắc bắt buộc:
- Luôn trả lời ngắn gọn bằng tiếng Việt.
- Không tự bịa product_id, giá, tồn kho, giảm giá, tổng tiền hoặc đường dẫn lưu file.
- Nếu thiếu tên khách hàng, số điện thoại, email, địa chỉ giao hàng, hoặc ít nhất một sản phẩm kèm số lượng, hãy hỏi bổ sung và dừng, không gọi tool.
- Từ chối ngay và không gọi tool nếu khách yêu cầu hóa đơn giả, ép giảm giá thủ công, bỏ qua tồn kho, bỏ qua catalog/policy, hoặc tạo dữ liệu không có thật.
- Với đơn hợp lệ, gọi tool đúng thứ tự: list_products -> get_product_details -> get_discount -> calculate_order_totals -> save_order.
- Nếu get_product_details cho thấy số lượng vượt tồn kho, hãy dừng và báo hết hàng, không tính tiền và không lưu đơn.
- Chỉ lưu đơn sau khi đã xác thực catalog, lấy discount, tính tổng tiền thành công.
- Câu trả lời cuối phải dựa trên kết quả tool: mã đơn, discount, tổng sau giảm, và đường dẫn lưu nếu có.
""".strip()


def build_tools(store: OrderDataStore):
    @tool(args_schema=ListProductsInput)
    def list_products(
        query: str | None = None,
        category: str | None = None,
        max_unit_price: int | None = None,
        required_tags: list[str] | None = None,
        in_stock_only: bool = True,
        limit: int = 8,
    ) -> str:
        """Search the local catalog before choosing product IDs for an electronics order."""
        payload = store.list_products(
            query=query,
            category=category,
            max_unit_price=max_unit_price,
            required_tags=required_tags,
            in_stock_only=in_stock_only,
            limit=limit,
        )
        return json.dumps(payload, ensure_ascii=False)

    @tool(args_schema=ProductDetailInput)
    def get_product_details(product_ids: list[str]) -> str:
        """Return exact product details and the validation token required by pricing and saving tools."""
        return json.dumps(store.get_product_details(product_ids), ensure_ascii=False)

    @tool(args_schema=DiscountInput)
    def get_discount(seed_hint: str, customer_tier: str = "standard") -> str:
        """Return the deterministic campaign discount. Use customer email as the seed_hint."""
        return json.dumps(store.get_discount(seed_hint=seed_hint, customer_tier=customer_tier), ensure_ascii=False)

    @tool(args_schema=CalculateTotalsInput)
    def calculate_order_totals(items: list[OrderLineInput], detail_token: str, discount_rate: float) -> str:
        """Validate stock and calculate subtotal, discount amount, and final total."""
        return json.dumps(
            store.calculate_order_totals(items=items, detail_token=detail_token, discount_rate=discount_rate),
            ensure_ascii=False,
        )

    @tool(args_schema=SaveOrderInput)
    def save_order(
        customer_name: str,
        customer_phone: str,
        customer_email: str,
        shipping_address: str,
        items: list[OrderLineInput],
        detail_token: str,
        discount_rate: float,
        campaign_code: str,
        customer_tier: str = "standard",
        notes: str = "",
    ) -> str:
        """Persist a validated order JSON after pricing succeeds."""
        return json.dumps(
            store.save_order(
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_email=customer_email,
                shipping_address=shipping_address,
                items=items,
                detail_token=detail_token,
                discount_rate=discount_rate,
                campaign_code=campaign_code,
                customer_tier=customer_tier,
                notes=notes,
            ),
            ensure_ascii=False,
        )

    return [list_products, get_product_details, get_discount, calculate_order_totals, save_order]


def build_agent(
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    *,
    provider: str = "google",
    model_name: str | None = None,
    today: str | None = None,
):
    store = OrderDataStore(data_dir or DEFAULT_DATA_DIR, output_dir or DEFAULT_OUTPUT_DIR, today=today)
    model = build_chat_model(provider=provider, model_name=model_name, temperature=0.0)
    return create_agent(model=model, tools=build_tools(store), system_prompt=build_system_prompt(today or store.today))


def run_agent(
    query: str,
    *,
    provider: str = "google",
    model_name: str | None = None,
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    today: str | None = None,
) -> AgentResult:
    store = OrderDataStore(data_dir or DEFAULT_DATA_DIR, output_dir or DEFAULT_OUTPUT_DIR, today=today)
    tool_calls: list[ToolCallRecord] = []

    if _is_guardrail_violation(query):
        return AgentResult(
            query=query,
            final_answer=(
                "Mình không thể tạo hóa đơn giả, ép khuyến mãi thủ công, bỏ qua tồn kho hoặc bỏ qua catalog/policy. "
                "Mình chỉ có thể tạo đơn dựa trên catalog và khuyến mãi hợp lệ."
            ),
            tool_calls=[],
            provider=provider,
            model_name=model_name,
        )

    customer = _extract_customer(query)
    items = _extract_items(query, store)
    missing = _missing_fields(customer, items)
    if missing:
        return AgentResult(
            query=query,
            final_answer="Mình cần thêm " + ", ".join(missing) + " trước khi tạo đơn.",
            tool_calls=[],
            provider=provider,
            model_name=model_name,
        )

    product_ids = [item.product_id for item in items]
    list_args = {"query": query, "category": None, "max_unit_price": None, "required_tags": [], "in_stock_only": True, "limit": 20}
    list_output = store.list_products(**list_args)
    tool_calls.append(ToolCallRecord(name="list_products", args=list_args, output=json.dumps(list_output, ensure_ascii=False)))

    details_args = {"product_ids": product_ids}
    details = store.get_product_details(product_ids)
    tool_calls.append(ToolCallRecord(name="get_product_details", args=details_args, output=json.dumps(details, ensure_ascii=False)))

    stock_errors = _stock_errors(items, store)
    if stock_errors:
        return AgentResult(
            query=query,
            final_answer="Không thể lưu đơn vì tồn kho không đủ: " + "; ".join(stock_errors),
            tool_calls=tool_calls,
            provider=provider,
            model_name=model_name,
        )

    discount_args = {"seed_hint": customer["email"], "customer_tier": "standard"}
    discount = store.get_discount(**discount_args)
    tool_calls.append(ToolCallRecord(name="get_discount", args=discount_args, output=json.dumps(discount, ensure_ascii=False)))

    detail_token = str(details["detail_token"])
    discount_rate = float(discount["discount_rate"])
    totals_args = {
        "items": [item.model_dump() for item in items],
        "detail_token": detail_token,
        "discount_rate": discount_rate,
    }
    totals = store.calculate_order_totals(items=items, detail_token=detail_token, discount_rate=discount_rate)
    tool_calls.append(ToolCallRecord(name="calculate_order_totals", args=totals_args, output=json.dumps(totals, ensure_ascii=False)))

    save_args = {
        "customer_name": customer["name"],
        "customer_phone": customer["phone"],
        "customer_email": customer["email"],
        "shipping_address": customer["shipping_address"],
        "items": [item.model_dump() for item in items],
        "detail_token": detail_token,
        "discount_rate": discount_rate,
        "campaign_code": str(discount["campaign_code"]),
        "customer_tier": "standard",
        "notes": "",
    }
    saved = store.save_order(
        customer_name=customer["name"],
        customer_phone=customer["phone"],
        customer_email=customer["email"],
        shipping_address=customer["shipping_address"],
        items=items,
        detail_token=detail_token,
        discount_rate=discount_rate,
        campaign_code=str(discount["campaign_code"]),
        customer_tier="standard",
        notes="",
    )
    tool_calls.append(ToolCallRecord(name="save_order", args=save_args, output=json.dumps(saved, ensure_ascii=False)))

    saved_order = saved.get("saved_order")
    final_total = saved_order["pricing"]["final_total"]
    order_id = saved_order["order_id"]
    item_summary = "; ".join(f"{item['quantity']} x {item['name']}" for item in saved_order["items"])
    final_answer = (
        f"Đã kiểm tra catalog/tồn kho và lưu đơn {order_id}: {item_summary}. "
        f"Áp dụng {saved_order['discount']['campaign_code']} "
        f"({int(discount_rate * 100)}%), tổng sau giảm {final_total:,} VND. "
        f"File lưu tại {saved['path']}."
    )
    return AgentResult(
        query=query,
        final_answer=final_answer,
        tool_calls=tool_calls,
        provider=provider,
        model_name=model_name,
        saved_order=saved_order,
        saved_order_path=saved.get("path"),
    )


def extract_final_answer(messages) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            text = normalize_content(message.content)
            if text:
                return text
    return ""


def extract_tool_calls(messages) -> list[ToolCallRecord]:
    pending: dict[str, dict[str, Any]] = {}
    records: list[ToolCallRecord] = []
    for message in messages:
        if isinstance(message, AIMessage):
            for tool_call in getattr(message, "tool_calls", []) or []:
                pending[tool_call["id"]] = {"name": tool_call["name"], "args": tool_call.get("args", {}) or {}}
        elif isinstance(message, ToolMessage):
            metadata = pending.pop(message.tool_call_id, {})
            records.append(
                ToolCallRecord(
                    name=str(getattr(message, "name", None) or metadata.get("name", "")),
                    args=metadata.get("args", {}),
                    output=normalize_content(message.content),
                )
            )
    for metadata in pending.values():
        records.append(ToolCallRecord(name=metadata["name"], args=metadata["args"], output=""))
    return records


def extract_saved_order(tool_calls: list[ToolCallRecord]) -> tuple[dict | None, str | None]:
    for record in reversed(tool_calls):
        if record.name != "save_order" or not record.output:
            continue
        try:
            payload = json.loads(record.output)
        except json.JSONDecodeError:
            continue
        if payload.get("status") == "saved":
            return payload.get("saved_order"), payload.get("path")
    return None, None


def _is_guardrail_violation(query: str) -> bool:
    normalized = _normalize(query)
    blocked_phrases = [
        "hoa don gia",
        "fake invoice",
        "giam gia 90",
        "ep giam gia",
        "bo qua ton kho",
        "bypass stock",
        "khong can theo catalog",
        "ignore catalog",
        "ignore policy",
        "bo qua policy",
    ]
    return any(phrase in normalized for phrase in blocked_phrases)


def _extract_customer(query: str) -> dict[str, str]:
    email_match = re.search(r"[\w.+-]+@[\w.-]+\.\w+", query)
    phone_match = re.search(r"\b0\d{9}\b", query)
    name = ""
    name_match = re.search(
        r"(?:cho|for)\s+(.+?)(?:,|\.|\s+số điện thoại|\s+phone|\s+email|\s+giao|\s+ship)",
        query,
        flags=re.IGNORECASE,
    )
    if name_match:
        name = re.sub(r"^(anh|chị|chi|bạn|ban)\s+", "", name_match.group(1).strip(), flags=re.IGNORECASE)
    shipping_address = _extract_shipping_address(query)
    return {
        "name": name.strip(),
        "phone": phone_match.group(0) if phone_match else "",
        "email": email_match.group(0) if email_match else "",
        "shipping_address": shipping_address,
    }


def _extract_shipping_address(query: str) -> str:
    patterns = [
        r"(?:giao hàng đến|địa chỉ giao hàng|giao đến|giao tới|giao về|giao toi|ship to)\s+(.+?)(?=\. Tôi|\. Mình|\. Chọn|\. Chốt|\. Phone|, số điện thoại|$)",
        r"(?:giao hàng|giao)\s+(.+?)(?=\. Tôi|\. Mình|\. Chọn|\. Chốt|, số điện thoại|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, query, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip().strip(".")
    return ""


def _extract_items(query: str, store: OrderDataStore) -> list[OrderLineInput]:
    found: list[tuple[int, OrderLineInput]] = []
    for product in store.products:
        match = re.search(re.escape(product.name), query, flags=re.IGNORECASE)
        if not match:
            continue
        prefix = query[: match.start()]
        quantity_match = re.search(r"(?:^|[\s,;:])(\d+)\s*$", prefix)
        quantity = int(quantity_match.group(1)) if quantity_match else 1
        found.append((match.start(), OrderLineInput(product_id=product.product_id, quantity=quantity)))
    found.sort(key=lambda item: item[0])
    return [item for _, item in found]


def _missing_fields(customer: dict[str, str], items: list[OrderLineInput]) -> list[str]:
    missing: list[str] = []
    if not customer["name"]:
        missing.append("tên khách hàng")
    if not customer["phone"]:
        missing.append("số điện thoại")
    if not customer["email"]:
        missing.append("email")
    if not customer["shipping_address"]:
        missing.append("địa chỉ giao hàng")
    if not items:
        missing.append("sản phẩm và số lượng")
    return missing


def _stock_errors(items: list[OrderLineInput], store: OrderDataStore) -> list[str]:
    errors: list[str] = []
    for item in items:
        product = store.product_index.get(item.product_id)
        if product and item.quantity > product.stock:
            errors.append(f"{product.name} yêu cầu {item.quantity}, hiện còn {product.stock}")
    return errors
