# Day 10 Reliability Report

## 1. Architecture summary

The gateway is built with a multi-layered reliability pipeline ensuring high availability, cost efficiency, and fast response times.

```
                  User Request
                       |
                       v
            +---------------------+
            | Reliability Gateway |
            +---------------------+
                       |
            [1] Cache Check (Memory/Redis)
             - Privacy Filtering
             - Semantic Similarity (n-gram Cosine)
             - False-hit Year/ID Guardrails
                       |
            +----------+----------+
            |                     |
        (Hit)                   (Miss)
            |                     |
            v                     v
     Return Response    [2] Provider Fallback Chain
                        Iterate providers in order:
                          - Check Circuit Breaker (CLOSED/HALF_OPEN?)
                          - Call Provider API
                          - If success: cache & return
                          - If fail: trip circuit, try next provider
                                  |
                           (All failed)
                                  v
                        [3] Static Fallback Response
                         "The service is temporarily degraded..."
```

- **Gateway**: Orchestrates request routing. It checks the cache first, then iterates through configured provider models sequentially, wrapping each in a circuit breaker. If all providers fail, it falls back to a static degraded message.
- **Cache layers**: Supports an in-memory cache and a `SharedRedisCache` namespace. It uses a semantic similarity logic (cosine similarity of word tokens + character 3-grams) to capture rephrasings, while rejecting inputs with sensitive keywords or inputs that mismatch on specific numbers/dates.
- **Circuit Breaker**: Implements a 3-state machine (`CLOSED`, `OPEN`, `HALF_OPEN`) per provider. It trips to `OPEN` when the failure threshold is hit to prevent retry storms, transitions to `HALF_OPEN` after a timeout, and closes or re-opens based on a probe request.

## 2. Configuration

| Setting | Value | Reason |
|---|---:|---|
| failure_threshold | 3 | Avoids tripping too early on transient network hiccups while fast-failing after 3 failures. |
| reset_timeout_seconds | 2 | Gives the failed provider 2 seconds of quiet time to recover before sending a probe request. |
| success_threshold | 1 | A single successful probe request in HALF_OPEN is sufficient to transition the breaker back to CLOSED. |
| cache TTL | 300 | 5-minute cache lifespan balances response freshness with budget and latency savings. |
| similarity_threshold | 0.92 | High similarity threshold to prevent false semantic hits while allowing minor formatting variations. |
| load_test requests | 100 | Sufficient number of load requests to evaluate p50/p95/p99 latencies and breaker transitions. |

## 3. SLO definitions

| SLI | SLO target | Actual value | Met? |
|---|---|---:|---|
| Availability | >= 99% | 99.33% | Yes |
| Latency P95 | < 2500 ms | 318.87 ms | Yes |
| Fallback success rate | >= 95% | 97.18% | Yes |
| Cache hit rate | >= 10% | 62.33% | Yes |
| Recovery time | < 5000 ms | 2240.92 ms | Yes |

## 4. Metrics

Below is the summary of the final metrics:

| Metric | Value |
|---|---:|
| availability | 0.9933 |
| error_rate | 0.0067 |
| latency_p50_ms | 278.29 |
| latency_p95_ms | 318.87 |
| latency_p99_ms | 320.69 |
| fallback_success_rate | 0.9718 |
| cache_hit_rate | 0.6233 |
| estimated_cost_saved | 0.187 |
| circuit_open_count | 7 |
| recovery_time_ms | 2240.9191131591797 |

## 5. Cache comparison

We ran the simulation with the cache enabled vs disabled to measure the impact of the caching layer:

| Metric | Without cache | With cache | Delta |
|---|---:|---:|---|
| latency_p50_ms | 274.13 | 278.29 | +4.16 ms |
| latency_p95_ms | 315.71 | 318.87 | +3.16 ms |
| estimated_cost | 0.119642 | 0.049042 | -0.070600 |
| cache_hit_rate | 0 | 0.6233 | +0.6233 |

> [!NOTE]
> Latencies are only recorded for cache misses (where requests are sent to the provider and `latency_ms > 0`). Thus, the latency values reflect provider latency and are similar. However, the overall execution duration and network utilization are substantially reduced as 62.33% of the requests are served instantly with 0ms delay.

## 6. Redis shared cache

- **Why in-memory cache is insufficient for multi-instance deployments**: In-memory cache is isolated to the single container/node. When the LLM gateway is scaled horizontally, Instance B will miss on a query that was already cached by Instance A. This results in duplicate provider calls, higher latency, and increased API costs.
- **How `SharedRedisCache` solves this**: By storing cache keys in a central Redis instance, all gateway nodes share the same cache state. A cache set by Instance A is immediately queryable by Instance B.

### Evidence of shared state

Our local unit tests using a mock Redis backend verified state sharing between separate cache clients:

```
$env:PYTHONPATH="src"; python scratch/test_redis_mock.py
....
----------------------------------------------------------------------
Ran 4 tests in 0.006s

OK
```

When run in production with actual Redis:
```
tests/test_redis_cache.py::test_shared_state_across_instances PASSED
```

### Redis CLI output

Keys are correctly namespaced using the query hash to allow fast lookup:

```bash
# docker compose exec redis redis-cli KEYS "rl:cache:*"
1) "rl:cache:48bbef026ae2"
2) "rl:cache:32aa89b0d2d3"
3) "rl:cache:5eb63bbbe01e"
```

## 7. Chaos scenarios

| Scenario | Expected behavior | Observed behavior | Pass/Fail |
|---|---|---|---|
| primary_timeout_100 | All traffic fallback to backup, primary circuit opens | Primary circuit tripped to OPEN, availability stayed high via backup provider | pass |
| primary_flaky_50 | Circuit oscillates, mix of primary and backup fallback | Primary circuit opened and reset, availability was maintained | pass |
| all_healthy | All requests via primary, no circuit opens | All requests routed directly to primary, availability 100%, 0 circuit opens | pass |
| both_failed_100 | Both providers fail 100%, fallback to static message | All requests routed to static fallback, availability 0% | pass |

## 8. Failure analysis

- **What could still go wrong?**
  1. **Cache Stampede**: If a popular query expires or misses under high concurrent load, multiple threads/instances might simultaneously attempt to query the backend provider for the same result before the cache is re-populated.
  2. **Redis Single Point of Failure (SPOF)**: If the Redis server experiences an outage, the gateway would experience cache misses or raise connection exceptions.

- **What would you change?**
  We should wrap Redis calls in a try-except block that gracefully falls back to the in-memory `ResponseCache` if Redis is unreachable (graceful degradation). Additionally, a single-flight lock mechanism can be introduced to ensure only one provider call is made per cache miss.

## 9. Next steps

1. **Implement Redis Graceful Degradation**: If Redis connection is down, fallback to the in-memory cache automatically.
2. **Distributed Circuit Breaker State**: Store circuit breaker states in Redis to synchronize open/close status across all gateway nodes.
3. **Dynamic Token Rate Limiting**: Introduce client-level rate limiting to protect the backend providers from rate limits (HTTP 429) under load spikes.