# SRE Exam Setup Summary

## What's Been Built

A realistic SRE on-call triage exercise with multiple services and complexity layers.

## Services

### 1. Payment Processor (Flask Application)
- **Container**: `payment-processor`
- **Port**: 8080
- **Language**: Python/Flask
- **Database**: PostgreSQL with SQLAlchemy
- **Endpoints**: 10+ API endpoints
- **The Fault**: Calls non-existent `fraud-api.internal.corp:8443` causing DNS failures

### 2. PostgreSQL Database
- **Container**: `payment-db`
- **Port**: 5432
- **Version**: PostgreSQL 15 Alpine
- **Credentials**: paymentuser / paymentpass123
- **Database**: payments
- **Tables**: customers, transactions, payment_methods, account_balances
- **Sample Data**: 6 customers, 5 transactions, 5 payment methods

### 3. Log Viewer (Dozzle)
- **Container**: `log-viewer`
- **Port**: 9999
- **URL**: http://localhost:9999
- **Purpose**: Web UI for viewing all container logs in real-time

### 4. Traffic Generator
- **Container**: `traffic-generator`
- **Purpose**: Simulates realistic application load
- **Traffic Pattern**: 70% reads (successful), 30% writes (mix of success/failure)
- **Request Rate**: 1 request every 0.5-3 seconds (realistic bursty traffic)
- **Effect**: Creates continuous log activity, burying errors among normal operations

## Endpoints Behavior

### ✅ Working Endpoints (8)
1. `GET /health` - Health check with DB status
2. `GET /api/customers/{id}` - Get customer from DB
3. `POST /api/customers` - Create customer in DB
4. `GET /api/accounts/{id}/balance` - Get account balance from DB
5. `GET /api/payment-methods/{id}` - Get payment methods from DB
6. `GET /api/transactions` - List transactions from DB
7. `GET /api/transactions/{id}` - Get transaction details from DB
8. `GET /api/stats` - Service statistics from DB
9. `POST /api/webhooks/payment-gateway` - Webhook receiver

### ❌ Failing Endpoints (2)
1. `POST /api/payment` - 92% error rate (503/504)
2. `POST /api/refund` - 88% error rate (503/504) for amounts > $1000

## The Challenge

Candidates must:
1. **Identify the pattern**: Only payment/refund operations fail
2. **Correlate with dependency**: These endpoints call fraud-api.internal.corp
3. **Diagnose root cause**: DNS resolution failure
4. **Propose safe mitigation**: Graceful degradation or circuit breaker
5. **Document investigation**: Clear incident notes
6. **Suggest permanent fix**: Proper DNS config, monitoring, resilience patterns

## Complexity Features

### Pattern Recognition Required
- Not all endpoints fail (only 2 out of 10+)
- Must analyze metrics to identify affected operations
- Healthy database might be a distraction

### Multiple Investigation Paths
- Logs (CLI or web UI)
- Metrics (provided files)
- Database queries
- Container health checks
- DNS/network testing

### Realistic Distractions
- Database is healthy and working
- Most endpoints return 200 OK
- Health check passes
- Log viewer shows mixed success/failure

## Files Provided

### For Candidates
- `README.md` - Exam instructions
- `runbook.md` - Service runbook (with intentional gaps)
- `metrics/error-rate.txt` - Error rate dashboard
- `metrics/latency.txt` - Latency metrics
- `metrics/dependencies.txt` - Dependency health
- `incident-notes.md` - Template for documentation
- `DATABASE_QUERIES.md` - Helpful DB queries

### For Examiners
- `SOLUTION.md` - Complete solution guide with rubric
- `EXAMINER_GUIDE.md` - Setup and observation guide
- `HINTS.md` - Progressive hints if candidate is stuck
- `test-endpoints.sh` - Automated endpoint testing

### Infrastructure
- `docker-compose.yml` - Multi-service setup
- `service/app.py` - Flask application with fault
- `service/Dockerfile` - Container build
- `db/init.sql` - Database initialization with sample data

## Quick Start for Examiners

```bash
# Start all services
docker-compose up -d

# Wait for initialization
sleep 10

# Verify setup
./test-endpoints.sh

# Open log viewer
open http://localhost:9999

# Give candidate access and start timer (45 min)
```

## Expected Solution Time

- **Strong candidate**: 25-30 minutes
- **Average candidate**: 35-40 minutes
- **Struggling candidate**: >40 minutes (may need hints)

## Key Evaluation Points

1. **Systematic approach**: Reads metrics before diving in
2. **Pattern recognition**: Identifies which endpoints fail
3. **Hypothesis-driven**: Forms theories before testing
4. **Safety awareness**: Considers rollback and blast radius
5. **Documentation**: Clear incident notes
6. **Communication**: Explains thinking process
7. **SRE mindset**: Mitigation first, root cause second

## What Makes This Realistic

- Multiple services (not just one container)
- Real database with queryable data
- Log aggregation tool (like production)
- Mixed success/failure (not everything broken)
- Requires pattern recognition
- Multiple valid mitigation approaches
- Trade-offs between security and availability
