import ast
import operator
from typing import Any, Dict, List


PRODUCTS = {
    "iphone": {"name": "iphone", "price": 799.0, "weight_kg": 0.4, "stock": 5},
    "headphones": {"name": "headphones", "price": 80.0, "weight_kg": 0.5, "stock": 10},
    "laptop": {"name": "laptop", "price": 1200.0, "weight_kg": 1.8, "stock": 3},
    "keyboard": {"name": "keyboard", "price": 45.0, "weight_kg": 0.8, "stock": 20},
}

DISCOUNTS = {
    "WINNER": 15,
    "SAVE10": 10,
    "STUDENT": 20,
    "NONE": 0,
}

SHIPPING_BASE = {
    "hanoi": 5.0,
    "ho chi minh": 6.0,
    "danang": 5.5,
    "da nang": 5.5,
}

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def get_product_info(item_name: str) -> Dict[str, Any]:
    key = item_name.strip().lower()
    product = PRODUCTS.get(key)
    if not product:
        return {"error": "product_not_found", "item_name": item_name}
    return product


def get_discount(coupon_code: str) -> Dict[str, Any]:
    code = coupon_code.strip().upper() or "NONE"
    return {"coupon_code": code, "discount_percent": DISCOUNTS.get(code, 0)}


def calc_shipping(weight_kg: float, destination: str) -> Dict[str, Any]:
    destination_key = destination.strip().lower()
    base = SHIPPING_BASE.get(destination_key, 8.0)
    shipping_cost = base + max(float(weight_kg) - 1.0, 0) * 2.0
    return {"destination": destination, "shipping_cost": round(shipping_cost, 2)}


def calculator(expression: str) -> Dict[str, Any]:
    tree = ast.parse(expression, mode="eval")
    result = _eval_math(tree.body)
    return {"expression": expression, "result": round(float(result), 2)}


def _eval_math(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
        return SAFE_OPERATORS[type(node.op)](_eval_math(node.left), _eval_math(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
        return SAFE_OPERATORS[type(node.op)](_eval_math(node.operand))
    raise ValueError("Only numeric arithmetic expressions are allowed.")


def get_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "get_product_info",
            "description": "Look up product price, weight, and stock. Args JSON: {\"item_name\": \"iphone\"}.",
            "args_schema": "{\"item_name\": string}",
            "func": get_product_info,
        },
        {
            "name": "get_discount",
            "description": "Return coupon discount percentage. Args JSON: {\"coupon_code\": \"SAVE10\"}. Unknown coupons return 0.",
            "args_schema": "{\"coupon_code\": string}",
            "func": get_discount,
        },
        {
            "name": "calc_shipping",
            "description": "Calculate shipping by total weight and destination. Args JSON: {\"weight_kg\": 1.2, \"destination\": \"Hanoi\"}.",
            "args_schema": "{\"weight_kg\": number, \"destination\": string}",
            "func": calc_shipping,
        },
        {
            "name": "calculator",
            "description": "Safely evaluate arithmetic expressions for final totals. Args JSON: {\"expression\": \"2*80+5\"}.",
            "args_schema": "{\"expression\": string}",
            "func": calculator,
        },
    ]
