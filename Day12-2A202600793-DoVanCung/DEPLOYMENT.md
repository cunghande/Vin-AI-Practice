# Deployment Information

## Public URL

TODO: add the deployed service URL, for example `https://your-agent.railway.app`.

## Platform

Railway, Render, or Cloud Run.

## Test Commands

### Health Check

```bash
curl https://your-agent.railway.app/health
# Expected: {"status":"ok", ...}
```

### Readiness Check

```bash
curl https://your-agent.railway.app/ready
# Expected: {"ready":true, ...}
```

### Authentication Required

```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
# Expected: 401
```

### API Test

```bash
curl -X POST https://your-agent.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
# Expected: 200
```

### Rate Limit Test

```bash
for i in {1..15}; do
  curl -X POST https://your-agent.railway.app/ask \
    -H "X-API-Key: YOUR_KEY" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test","question":"rate limit test"}'
done
# Expected: first requests return 200, later requests return 429
```

## Environment Variables Set

- `PORT`
- `ENVIRONMENT=production`
- `REDIS_URL`
- `AGENT_API_KEY`
- `JWT_SECRET`
- `RATE_LIMIT_PER_MINUTE=10`
- `MONTHLY_BUDGET_USD=10.0`
- `DAILY_BUDGET_USD=1.0`
- `LOG_LEVEL` or platform logging defaults

## Screenshots

- TODO: `screenshots/dashboard.png`
- TODO: `screenshots/running.png`
- TODO: `screenshots/test.png`
