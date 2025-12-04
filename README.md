# SRE Practical Exam: On-Call Triage Exercise

## Scenario
You've been paged at 2:47 AM. The payment-processor service is experiencing elevated error rates. Users are reporting failed transactions.

## Time Limit
45 minutes

## Your Task
1. Identify the symptom and probable root cause
2. Propose and execute a safe mitigation (not necessarily a full fix)
3. Document your investigation in `incident-notes.md`
4. Outline a permanent fix in your notes

## What You Have Access To
- **Payment Service**: `http://localhost:8080`
- **Log Viewer (Dozzle)**: `http://localhost:9999` - Web UI for viewing all container logs
- **PostgreSQL Database**: `localhost:5432` (credentials in docker-compose.yml)
- Docker containers: `payment-processor`, `payment-db`, `log-viewer`, `traffic-generator`
- Logs: `docker logs payment-processor` or use the log viewer UI
- Metrics snippets in `metrics/`
- Runbook in `runbook.md`
- Service configuration in `service/`

**Note**: A traffic generator is running to simulate realistic application load. This creates continuous log activity mixing successful and failing requests.

## Getting Started
```bash
# Start all services (payment processor, database, log viewer, traffic generator)
docker-compose up -d

# Wait for services to be ready (about 15 seconds)
sleep 15

# Traffic generator will start automatically and simulate realistic load

# Quick test of all endpoints (optional)
./test-endpoints.sh

# Or test manually:

# Check service health
curl http://localhost:8080/health

# View logs in browser
open http://localhost:9999  # or visit in your browser

# Test various endpoints
curl http://localhost:8080/api/customers/cust_001
curl http://localhost:8080/api/accounts/cust_001/balance
curl http://localhost:8080/api/stats
curl http://localhost:8080/api/transactions?limit=5

# Try processing a payment (users report this is failing)
curl -X POST http://localhost:8080/api/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "currency": "USD", "customer_id": "cust_001"}'

# Access database directly (if needed)
docker exec -it payment-db psql -U paymentuser -d payments
```

## Evaluation Criteria
- Hypothesis-driven debugging approach
- Clear communication in incident notes
- Safety awareness (rollbacks, blast radius considerations)
- Effective use of observability signals
- Structured problem-solving under pressure
