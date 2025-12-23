# Solution Guide (For Evaluators Only)

## The Fault
The service is configured to call `fraud-api.internal.corp:8443` which:
1. Is a non-existent internal hostname (DNS resolution will fail)
2. Causes connection errors or timeouts on payment and refund requests
3. Results in 503/504 errors for 92% of payment requests and 88% of refund requests
4. Other endpoints (customers, transactions, stats) work fine as they don't call the fraud API

**Why this is realistic**: The multiple working endpoints make it less obvious where the problem is, forcing candidates to analyze patterns rather than immediately seeing "everything is broken".

## Expected Investigation Path

### 1. Symptom Identification (5-8 min)
- Overall error rate is 31%, but not all endpoints are affected
- /api/payment has 92% error rate
- /api/refund has 88% error rate
- All other endpoints (customers, transactions, stats) are healthy
- 503/504 errors indicating dependency issues
- High latency (~2s) on failing endpoints, matching timeout configuration
- Health endpoint is fine

**Key insight**: Only payment and refund operations are failing, not read operations

### 2. Hypothesis Formation (5-7 min)
Strong candidates should notice:
- Errors are specifically 503/504 (dependency-related)
- Only payment/refund endpoints fail (not customer/transaction reads)
- Latency matches FRAUD_CHECK_TIMEOUT (2s)
- Metrics show fraud API is unreachable since 02:35 UTC
- Health check passes (doesn't call fraud API)
- Pattern suggests a specific dependency used only by payment operations

**Expected hypothesis**: Fraud API dependency (used by payment/refund) is failing/unreachable

### 3. Investigation Steps (10-12 min)
Good candidates will:
- Review metrics to identify which endpoints are failing
- Notice the pattern: payment/refund fail, but reads succeed
- Check logs: `docker logs payment-processor`
- See connection errors to fraud-api.internal.corp in payment/refund logs
- Correlate the failing endpoints with fraud check dependency
- Test DNS resolution: `docker exec payment-processor nslookup fraud-api.internal.corp`
- Or test connectivity: `docker exec payment-processor curl -v fraud-api.internal.corp:8443`
- Identify DNS failure as root cause

**Weaker candidates might**:
- Get distracted by the healthy endpoints
- Spend time investigating database or other dependencies
- Not notice the pattern that only fraud-check-dependent endpoints fail

### 4. Safe Mitigation (15 min)
Multiple valid approaches:

**Option A: Graceful Degradation (Best)**
```python
# Modify app.py to skip fraud check or use fallback
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
    logger.warning(f"Fraud check unavailable, allowing payment with manual review flag")
    # Allow payment but flag for manual review
    return jsonify({
        "status": "success",
        "transaction_id": f"txn_{int(time.time())}",
        "requires_manual_review": True
    }), 200
```

**Option B: Fix DNS (If they identify the issue)**
```yaml
# docker-compose.yml - comment out or fix the URL
environment:
  - FRAUD_CHECK_URL=http://fraud-api-backup.example.com/verify
  # Or disable fraud check temporarily
```

**Option C: Circuit Breaker**
Add logic to fail fast after N failures

### 5. Verification (5 min)
- Restart service
- Test payment endpoint
- Monitor error rate drops
- Check logs for success

### 6. Permanent Fix Proposal (5 min)
Should include:
- Fix DNS configuration or use correct fraud API endpoint
- Implement circuit breaker pattern
- Add graceful degradation for non-critical checks
- Improve monitoring: DNS resolution checks, dependency health
- Add alerting for dependency failures
- Consider retry logic with exponential backoff

## Evaluation Rubric

### Excellent (90-100%)
- Quickly identifies symptom → dependency failure → DNS issue
- Proposes safe mitigation with rollback plan
- Considers blast radius and business impact
- Documents investigation clearly
- Suggests comprehensive permanent fix
- Shows awareness of trade-offs (security vs availability)

### Good (75-89%)
- Identifies dependency failure
- Proposes reasonable mitigation
- Basic documentation
- Suggests permanent fix
- Some safety considerations

### Adequate (60-74%)
- Eventually identifies the issue
- Proposes mitigation (may not be optimal)
- Minimal documentation
- Basic permanent fix ideas

### Needs Improvement (<60%)
- Struggles to identify root cause
- Unsafe mitigation attempts
- Poor documentation
- No clear permanent fix
- Doesn't consider safety/rollback

## Red Flags
- Making changes without understanding the issue
- No rollback plan
- Ignoring logs/metrics
- Not documenting investigation
- Proposing fixes that increase blast radius
- No consideration of business impact
