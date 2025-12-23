# Monitoring & Alerting Exercise (Optional Extension)

This can be added after the candidate solves the main issue, or as a separate follow-up exercise.

## Part 1: Design Alerts (10-15 minutes)

### Scenario
"Now that you've fixed the issue, design the monitoring and alerting that would have caught this problem earlier."

### What to Provide
Give them a blank template:

```yaml
# alerts.yml template
alerts:
  - name: ""
    description: ""
    metric: ""
    threshold: ""
    duration: ""
    severity: ""
    notification: ""
```

### What to Look For

**Excellent candidates will define:**
1. **Symptom-based alerts** (error rate, latency)
   - Payment endpoint error rate > 10% for 5 minutes
   - P95 latency > 1s for 5 minutes
   
2. **Cause-based alerts** (dependency health)
   - Fraud API connection failures > 5% for 2 minutes
   - DNS resolution failures detected
   
3. **Resource alerts** (preventive)
   - Connection pool utilization > 80%
   - Memory usage > 85%

4. **Business impact alerts**
   - Failed payment count > 100 in 5 minutes
   - Revenue impact > $X threshold

**Good candidates will define:**
- Basic error rate alerts
- Latency alerts
- Some dependency monitoring

**Weak candidates will:**
- Only define generic alerts
- Not consider thresholds or durations
- Miss business impact

---

## Part 2: Design Dashboards (10 minutes)

### Scenario
"Design a dashboard for this service. What metrics would you include?"

### What to Look For

**Excellent candidates include:**

1. **Golden Signals** (USE/RED method)
   - Request Rate
   - Error Rate
   - Duration (latency)
   - Saturation (resource usage)

2. **Business Metrics**
   - Successful payments per minute
   - Failed payments per minute
   - Revenue processed
   - Average transaction value

3. **Dependency Health**
   - Fraud API response time
   - Fraud API error rate
   - Database query time
   - Database connection pool usage

4. **Breakdown Views**
   - Errors by endpoint
   - Latency by endpoint
   - Errors by customer
   - Traffic by region/source

**Bonus points for:**
- SLI/SLO tracking
- Comparison to baseline/historical
- Correlation views (errors vs. deployments)

---

## Part 3: Define SLIs/SLOs (10 minutes)

### Scenario
"Define Service Level Indicators and Objectives for this payment service."

### What to Look For

**Excellent candidates define:**

**SLIs (what to measure):**
- Availability: % of successful requests
- Latency: % of requests < 500ms
- Correctness: % of payments processed correctly

**SLOs (targets):**
- 99.9% of payment requests succeed (availability)
- 99% of payment requests complete in < 500ms (latency)
- 99.99% of payments are processed correctly (correctness)

**Error Budget:**
- 0.1% error budget = ~43 minutes downtime per month
- How to spend it: deployments, experiments, maintenance

**Good candidates:**
- Define basic SLOs
- Understand availability and latency
- May not consider error budget

**Weak candidates:**
- Confuse SLI/SLO/SLA
- Set unrealistic targets (99.999%)
- Don't consider business context

---

## Part 4: Runbook Improvements (5-10 minutes)

### Scenario
"The runbook you used had some gaps. What would you add or change?"

### What to Look For

**Excellent candidates suggest:**

1. **Better troubleshooting steps**
   - Decision tree for different error types
   - Specific commands to run
   - How to test dependencies directly

2. **Dependency documentation**
   - Exact hostnames and ports
   - How to verify DNS resolution
   - Backup/fallback endpoints

3. **Mitigation procedures**
   - Step-by-step graceful degradation
   - Feature flag instructions
   - Rollback procedures

4. **Escalation clarity**
   - When to page fraud API team
   - When to page database team
   - When to escalate to management

5. **Recent changes section**
   - Link to deployment history
   - Configuration changes
   - Infrastructure changes

**Good candidates:**
- Add missing troubleshooting steps
- Improve dependency documentation
- Add some mitigation procedures

**Weak candidates:**
- Only point out what was missing
- Don't provide concrete improvements
- Focus on blame rather than improvement

---

## Part 5: Architecture Improvements (10-15 minutes)

### Scenario
"How would you redesign this system to be more resilient?"

### What to Look For

**Excellent candidates propose:**

1. **Resilience Patterns**
   - Circuit breaker for fraud API
   - Retry with exponential backoff
   - Timeout tuning
   - Bulkhead pattern (isolate failures)

2. **Graceful Degradation**
   - Allow payments without fraud check (with manual review)
   - Use cached fraud scores
   - Risk-based approach (skip for low amounts)

3. **Async Processing**
   - Queue payments for async fraud check
   - Event-driven architecture
   - Eventual consistency

4. **Redundancy**
   - Multiple fraud API providers
   - Fallback to rule-based fraud detection
   - Geographic redundancy

5. **Observability**
   - Distributed tracing
   - Structured logging
   - Metrics at every layer

**Good candidates:**
- Suggest circuit breaker
- Mention retry logic
- Basic graceful degradation

**Weak candidates:**
- Only suggest "make it more reliable"
- No specific patterns
- Don't consider trade-offs

---

## Scoring Guide

### Monitoring & Alerting (Part 1-2)
- **Excellent**: Comprehensive alerts, considers business impact, good thresholds
- **Good**: Basic alerts, some dependency monitoring
- **Adequate**: Generic alerts, missing key metrics
- **Poor**: Doesn't understand alerting fundamentals

### SLI/SLO (Part 3)
- **Excellent**: Clear SLIs, realistic SLOs, understands error budget
- **Good**: Basic SLOs, understands availability
- **Adequate**: Confuses terms, unrealistic targets
- **Poor**: Doesn't understand SLI/SLO concept

### Runbook & Architecture (Part 4-5)
- **Excellent**: Specific improvements, resilience patterns, considers trade-offs
- **Good**: Some improvements, basic patterns
- **Adequate**: Vague suggestions, limited thinking
- **Poor**: No concrete ideas

---

## Time Allocation

### Quick Version (15 minutes)
- Part 1: Design 2-3 key alerts
- Part 4: Suggest 3 runbook improvements

### Standard Version (30 minutes)
- Part 1: Design alerts (10 min)
- Part 2: Design dashboard (10 min)
- Part 4: Runbook improvements (10 min)

### Comprehensive Version (45 minutes)
- All parts (1-5)
- Deep dive into architecture

### Senior SRE Version (60 minutes)
- All parts
- Ask them to present to "stakeholders"
- Discuss cost/benefit of improvements
- Prioritization exercise
