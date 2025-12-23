# Post-Incident Follow-Up Questions

After the candidate has identified and mitigated the issue, ask these questions to assess deeper SRE knowledge:

## Technical Understanding (5-10 minutes)

### 1. Root Cause Analysis
- "Walk me through your investigation process. What led you to the root cause?"
- "What were the key signals that pointed you to the issue?"
- "Were there any red herrings that distracted you? How did you rule them out?"

### 2. Alternative Solutions
- "You proposed [their solution]. What are 2-3 other ways you could have mitigated this?"
- "What are the trade-offs of your approach vs. alternatives?"
- "If you couldn't modify the code, what would you do?"

### 3. Blast Radius & Safety
- "What's the blast radius of your mitigation?"
- "How would you safely deploy this fix to production?"
- "What could go wrong with your solution?"
- "How would you roll back if your fix made things worse?"

## System Design & Architecture (5-10 minutes)

### 4. Resilience Patterns
- "How would you make this system more resilient to dependency failures?"
- "What's a circuit breaker and would it help here? How would you implement it?"
- "Should fraud checks be synchronous or asynchronous? Why?"

### 5. Monitoring & Alerting
- "What monitoring would have caught this issue earlier?"
- "What alerts would you set up to prevent this in the future?"
- "What SLIs/SLOs would you define for this service?"

### 6. Permanent Fix
- "What's the difference between your mitigation and a permanent fix?"
- "How would you prevent this class of issue in the future?"
- "What process improvements would you recommend?"

## Incident Management (5 minutes)

### 7. Communication
- "Who would you notify about this incident and when?"
- "What would you put in your incident update to stakeholders?"
- "When would you escalate this incident?"

### 8. Post-Mortem
- "What would be the key points in your post-mortem?"
- "How would you categorize this incident? (SEV-1, SEV-2, etc.)"
- "What action items would you propose?"

## Scenario Variations (Optional - 5 minutes)

### 9. "What If" Scenarios
- "What if the fraud API was responding but very slowly (10s latency)?"
- "What if only 10% of requests were failing instead of 90%?"
- "What if this was happening during Black Friday with 100x traffic?"
- "What if the fraud API team says the hostname is correct and should work?"

### 10. Production Considerations
- "How would your approach differ if this was production vs. staging?"
- "What if you couldn't restart the service?"
- "What if this affected multiple services, not just payments?"

## Scoring Rubric

### Excellent (90-100%)
- Clear, structured thinking
- Considers multiple solutions with trade-offs
- Strong understanding of resilience patterns
- Proactive about monitoring and prevention
- Good communication and incident management skills

### Good (75-89%)
- Solid technical understanding
- Identifies some alternatives
- Basic monitoring/alerting knowledge
- Adequate communication

### Adequate (60-74%)
- Understands the specific issue
- Limited broader thinking
- Basic incident management
- Needs prompting for deeper insights

### Needs Improvement (<60%)
- Struggles to explain reasoning
- No alternative solutions
- Poor understanding of production concerns
- Weak communication

## Red Flags
- Can't explain their own solution
- No consideration of safety/rollback
- Blames others (fraud API team, DNS team, etc.)
- No learning mindset (doesn't think about prevention)
- Overconfident without considering edge cases
