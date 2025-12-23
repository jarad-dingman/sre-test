# Examiner Guide

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- 45 minutes for candidate

### Before the Exam
1. Clone this repository
2. Test the setup:
```bash
docker-compose up -d

# Wait for services to initialize (including traffic generator)
sleep 15

# Verify traffic generator is running
docker logs traffic-generator --tail 20

# Run automated tests
./test-endpoints.sh

# Or test manually:

# Test healthy endpoints (should work)
curl http://localhost:8080/health  # Should return 200
curl http://localhost:8080/api/customers/cust_001  # Should return 200
curl http://localhost:8080/api/accounts/cust_001/balance  # Should return 200
curl http://localhost:8080/api/stats  # Should return 200

# Test failing endpoints (should fail)
curl -X POST http://localhost:8080/api/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "currency": "USD", "customer_id": "cust_001"}'
# Should return 503 or 504 error

curl -X POST http://localhost:8080/api/refund \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "txn_001", "amount": 1500}'
# Should return 503 or 504 error (for amounts > $1000)

# Check log viewer
open http://localhost:9999

# Check database
docker exec -it payment-db psql -U paymentuser -d payments -c "SELECT COUNT(*) FROM transactions;"

docker-compose down
```

### Key Complexity Features
- **Multiple services**: Payment processor, PostgreSQL database, log aggregation (Dozzle), traffic generator
- **Multiple endpoints**: 10+ different API endpoints, only 2 are failing
- **Real database**: PostgreSQL with sample data that candidates can query
- **Log viewer**: Web UI for viewing logs (http://localhost:9999)
- **Active traffic**: Traffic generator creates continuous realistic load (70% reads, 30% writes)
- **Log noise**: Constant stream of logs mixing successful and failing requests
- **Pattern recognition required**: Candidates must identify that only payment/refund operations fail
- **Realistic scenario**: Not all endpoints share the same dependencies
- **Distraction factor**: Healthy endpoints and database might lead candidates down wrong paths initially
- **Filtering required**: Candidates must filter logs to find relevant errors among normal traffic

### Starting the Exam
1. Give candidate access to the repository
2. Share README.md and explain the scenario
3. Start timer (45 minutes)
4. Observe but don't help unless they're completely stuck

## What to Observe

### Communication & Process
- [ ] Reads the runbook and metrics before diving in
- [ ] Documents investigation in incident-notes.md
- [ ] Explains their thinking process out loud
- [ ] Forms hypotheses before testing
- [ ] Updates notes as they learn more

### Technical Skills
- [ ] Checks logs systematically
- [ ] Reviews metrics to identify affected endpoints
- [ ] Recognizes pattern: only payment/refund fail, reads succeed
- [ ] Correlates failing endpoints with shared dependency
- [ ] Tests hypotheses methodically
- [ ] Identifies the DNS/connection issue
- [ ] Understands the timeout behavior
- [ ] Doesn't get distracted by healthy endpoints

### Safety & Judgment
- [ ] Considers rollback plan before making changes
- [ ] Thinks about blast radius
- [ ] Proposes safe mitigation (not just "fix it")
- [ ] Considers business impact
- [ ] Knows when to escalate

### SRE Mindset
- [ ] Focuses on mitigation first, root cause second
- [ ] Thinks about monitoring gaps
- [ ] Proposes preventive measures
- [ ] Considers trade-offs (security vs availability)
- [ ] Documents for future responders

## Common Candidate Paths

### Strong Candidate (25-30 min)
1. Reads metrics, identifies pattern: only payment/refund failing (5 min)
2. Forms hypothesis about shared dependency (fraud check) (3 min)
3. Checks logs, sees connection errors to fraud API (5 min)
4. Tests DNS resolution or connectivity, confirms issue (4 min)
5. Proposes graceful degradation with clear reasoning (5 min)
6. Documents investigation and suggests permanent fix (8 min)

### Average Candidate (35-40 min)
1. Starts with logs, sees various errors (8 min)
2. Tests some healthy endpoints, gets briefly distracted (5 min)
3. Eventually notices pattern in metrics (7 min)
4. Identifies fraud API issue (5 min)
5. Proposes basic mitigation (10 min)
6. Minimal documentation (5 min)

### Struggling Candidate (>40 min)
1. Random debugging without hypothesis
2. Doesn't notice the endpoint pattern in metrics
3. Investigates healthy endpoints unnecessarily
4. Doesn't read metrics/runbook carefully
5. Makes changes without understanding
6. Poor or no documentation
7. May not identify root cause

## Hints (If Needed)

### After 15 min if stuck
"Have you looked at which specific endpoints are failing versus which are working?"

### After 25 min if still stuck
"What do the error codes 503 and 504 typically indicate? What do the failing endpoints have in common?"

### After 35 min if still stuck
"Have you checked if the fraud API hostname is resolvable?"

## Managing Traffic Generator

The traffic generator creates realistic log noise. If you need to:

**Stop traffic temporarily** (to make logs easier to read):
```bash
docker stop traffic-generator
```

**Restart traffic**:
```bash
docker start traffic-generator
```

**View traffic generator logs**:
```bash
docker logs traffic-generator --tail 50
```

**Note**: Most candidates should be able to work with the traffic running (using grep or Dozzle filters). Only stop it if they're completely overwhelmed.

## Debrief Questions
1. Walk me through your investigation process
2. Why did you choose that mitigation approach?
3. What are the trade-offs of your solution?
4. How would you prevent this in the future?
5. What would you do differently if this was production?
6. When would you escalate this incident?

## Scoring
See SOLUTION.md for detailed rubric
