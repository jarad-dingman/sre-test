# Progressive Hints (For Examiner Use Only)

Use these hints progressively if the candidate is stuck. Don't give them all at once!

## Hint 1 (After 15 minutes if no progress)
"Start by looking at the metrics files. Are all endpoints affected equally?"

## Hint 2 (After 20 minutes)
"Compare the endpoints that are failing with those that are working. What might they have in common?"

## Hint 3 (After 25 minutes)
"The error codes 503 and 504 typically indicate what kind of problem?"
- Expected answer: Dependency/upstream service issues

## Hint 4 (After 30 minutes)
"Look at the runbook. Which dependency is used by payment and refund operations but not by read operations?"

## Hint 5 (After 35 minutes)
"Try checking if you can reach the fraud API from inside the container. What tools could you use?"
- Examples: nslookup, dig, curl, ping

## Hint 6 (After 38 minutes - last resort)
"What happens when you try to resolve the hostname fraud-api.internal.corp?"

## If They Identify the Issue But Struggle with Mitigation
"Think about the business impact. Is it better to:
- Block all payments until the fraud API is fixed?
- Allow payments to go through with some additional risk/review process?
- Something else?"

## If They Want to "Fix" DNS
"That's one approach, but in a real incident at 3 AM, you might not have access to DNS servers or know the correct hostname. What could you do to restore service quickly while you investigate the proper fix?"

## If They're Not Documenting
"Remember, other engineers might need to take over this incident. What information would they need to know about what you've found so far?"
