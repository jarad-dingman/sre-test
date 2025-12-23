# Payment Processor Runbook

## Service Overview
- **Service**: payment-processor
- **Purpose**: Processes customer payment transactions and manages customer data
- **Dependencies**: 
  - Fraud verification service (external - used for payments/refunds)
  - PostgreSQL database (payment-db container)
  - Payment Gateway API (external)
- **SLA**: 99.9% uptime, p95 latency < 500ms
- **Recent Changes**: Database connection pool increased from 10 to 20 connections (deployed 02:00 UTC)

## Architecture
```
Client → payment-processor → Fraud Verification API (external)
                          → PostgreSQL (customer/transaction data)
                          → Payment Gateway (external)

Supporting Services:
- payment-db (PostgreSQL 15)
- log-viewer (Dozzle - http://localhost:9999)
- traffic-generator (simulates realistic application load)
```

**Note**: The traffic-generator container continuously sends requests to simulate production traffic patterns (70% reads, 30% writes). This creates realistic log volume.

## Endpoints
- `GET /health` - Health check (includes DB connectivity check)
- `GET /api/customers/{id}` - Get customer details (reads from DB)
- `POST /api/customers` - Create customer (writes to DB)
- `GET /api/accounts/{customer_id}/balance` - Get account balance (reads from DB)
- `GET /api/payment-methods/{customer_id}` - Get payment methods (reads from DB)
- `GET /api/transactions` - List transactions (reads from DB)
- `GET /api/transactions/{id}` - Get transaction details (reads from DB)
- `POST /api/payment` - Process payment (calls fraud check, writes to DB)
- `POST /api/refund` - Process refund (calls fraud check for amounts > $1000, writes to DB)
- `GET /api/stats` - Service statistics (reads from DB)
- `POST /api/webhooks/payment-gateway` - Payment gateway webhook

## Database Access
```bash
# Connect to database
docker exec -it payment-db psql -U paymentuser -d payments

# Useful queries
SELECT * FROM customers LIMIT 10;
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 20;
SELECT status, COUNT(*) FROM transactions GROUP BY status;
SELECT * FROM transaction_summary LIMIT 10;
```

## Log Access
- **Web UI**: http://localhost:9999 (Dozzle log viewer - recommended for filtering)
- **CLI**: `docker logs payment-processor`
- **Follow logs**: `docker logs -f payment-processor`
- **All services**: `docker-compose logs -f`
- **Filter by error**: `docker logs payment-processor 2>&1 | grep -i error`
- **Recent errors only**: `docker logs payment-processor --tail 100 | grep -i error`
- **Deployment history**: See `deployments.log` for recent changes

**Tip**: With traffic generator running, logs will be very active. Use grep or the Dozzle UI filters to focus on errors.

## Common Issues

### High Error Rate (5xx)
**Symptoms**: Elevated 503/504 errors, customer complaints

**Possible Causes**:
- Downstream dependency failure
- Resource exhaustion
- Database connection issues

**Investigation Steps**:
1. Check service logs: `docker logs payment-processor --tail 100` or use http://localhost:9999
2. Verify health endpoint: `curl http://localhost:8080/health`
3. Check which endpoints are affected (not all endpoints may be failing)
4. Check database connectivity: `docker exec -it payment-db psql -U paymentuser -d payments -c "SELECT 1"`
5. Review recent deployments: `cat deployments.log`
6. Review error patterns by endpoint
7. Check all container statuses: `docker-compose ps`

### High Latency
**Symptoms**: Slow response times, timeouts

**Possible Causes**:
- Database slow queries
- Network issues
- Downstream service degradation

**Investigation Steps**:
1. Check metrics for latency spikes
2. Review logs for timeout errors

## Mitigation Strategies

### Circuit Breaker Pattern
If a dependency is failing, consider implementing a circuit breaker to fail fast.

### Rollback Procedure
```bash
# Rollback to previous version
docker-compose down
# Edit docker-compose.yml to use previous image tag
docker-compose up -d
```

## Configuration

### Environment Variables
- `FRAUD_CHECK_URL`: URL for fraud verification service
- `FRAUD_CHECK_TIMEOUT`: Timeout for fraud check (default: 2s)
- `RATE_LIMIT_PER_MINUTE`: Rate limit per customer
- `LOG_LEVEL`: Logging verbosity (info, debug, error)

### Changing Configuration
```bash
# Edit docker-compose.yml
vim docker-compose.yml

# Restart service
docker-compose restart payment-processor
```

## Recent Incidents

### INC-2024-1115 (Nov 15, 2024)
- **Issue**: High latency on all endpoints
- **Root Cause**: Database connection pool exhaustion
- **Resolution**: Increased pool size from 10 to 20
- **Prevention**: Added connection pool monitoring

### INC-2024-1028 (Oct 28, 2024)
- **Issue**: Intermittent 503 errors on payment endpoint
- **Root Cause**: Payment gateway rate limiting
- **Resolution**: Implemented exponential backoff
- **Prevention**: Added rate limit monitoring

## Escalation
- **On-call Engineer**: @payments-team
- **Manager**: @engineering-manager
- **Escalate if**: Issue not resolved in 30 minutes or revenue impact > $10k
