"""LLM cost guard with Redis persistence and local fallback."""

import time
from dataclasses import dataclass

from fastapi import HTTPException


PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006


@dataclass
class UsageSummary:
    monthly_cost_usd: float
    monthly_budget_usd: float
    daily_cost_usd: float
    daily_budget_usd: float
    request_count: int


class CostGuard:
    def __init__(
        self,
        redis_client=None,
        monthly_budget_usd: float = 10.0,
        daily_budget_usd: float = 1.0,
    ):
        self.redis = redis_client
        self.monthly_budget_usd = monthly_budget_usd
        self.daily_budget_usd = daily_budget_usd
        self._memory: dict[str, float | int] = {}

    def check_budget(self) -> None:
        summary = self.get_usage()
        if summary.monthly_cost_usd >= self.monthly_budget_usd:
            raise HTTPException(503, "Monthly budget exhausted. Try again next month.")
        if summary.daily_cost_usd >= self.daily_budget_usd:
            raise HTTPException(503, "Daily budget exhausted. Try again tomorrow.")

    def record_usage(self, input_tokens: int, output_tokens: int) -> UsageSummary:
        cost = (
            (input_tokens / 1000) * PRICE_PER_1K_INPUT_TOKENS
            + (output_tokens / 1000) * PRICE_PER_1K_OUTPUT_TOKENS
        )
        month_key, day_key = self._period_keys()
        if self.redis:
            pipe = self.redis.pipeline()
            pipe.incrbyfloat(f"cost:{month_key}", cost)
            pipe.incrbyfloat(f"cost:{day_key}", cost)
            pipe.incr(f"requests:{month_key}")
            pipe.expire(f"cost:{month_key}", 60 * 60 * 24 * 370)
            pipe.expire(f"cost:{day_key}", 60 * 60 * 48)
            pipe.expire(f"requests:{month_key}", 60 * 60 * 24 * 370)
            pipe.execute()
        else:
            self._memory[f"cost:{month_key}"] = self._memory.get(f"cost:{month_key}", 0.0) + cost
            self._memory[f"cost:{day_key}"] = self._memory.get(f"cost:{day_key}", 0.0) + cost
            self._memory[f"requests:{month_key}"] = self._memory.get(f"requests:{month_key}", 0) + 1
        return self.get_usage()

    def get_usage(self) -> UsageSummary:
        month_key, day_key = self._period_keys()
        if self.redis:
            monthly = float(self.redis.get(f"cost:{month_key}") or 0)
            daily = float(self.redis.get(f"cost:{day_key}") or 0)
            requests = int(self.redis.get(f"requests:{month_key}") or 0)
        else:
            monthly = float(self._memory.get(f"cost:{month_key}", 0))
            daily = float(self._memory.get(f"cost:{day_key}", 0))
            requests = int(self._memory.get(f"requests:{month_key}", 0))
        return UsageSummary(
            monthly_cost_usd=monthly,
            monthly_budget_usd=self.monthly_budget_usd,
            daily_cost_usd=daily,
            daily_budget_usd=self.daily_budget_usd,
            request_count=requests,
        )

    def _period_keys(self) -> tuple[str, str]:
        return time.strftime("%Y-%m"), time.strftime("%Y-%m-%d")
