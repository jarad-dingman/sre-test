#!/bin/bash

echo "=== Testing Payment Processor Endpoints ==="
echo ""

BASE_URL="http://localhost:8080"

echo "1. Health Check"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/health
echo ""

echo "2. Get Customer"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/api/customers/cust_001
echo ""

echo "3. Get Account Balance"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/api/accounts/cust_001/balance
echo ""

echo "4. Get Stats"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/api/stats
echo ""

echo "5. List Transactions"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/api/transactions?limit=5
echo ""

echo "6. Get Payment Methods"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/api/payment-methods/cust_001
echo ""

echo "7. Get Transaction Details"
curl -s -w "\nStatus: %{http_code}\n" $BASE_URL/api/transactions/txn_001
echo ""

echo "8. Process Payment"
curl -s -w "\nStatus: %{http_code}\n" -X POST $BASE_URL/api/payment \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "currency": "USD", "customer_id": "cust_001"}'
echo ""

echo "9. Process Refund"
curl -s -w "\nStatus: %{http_code}\n" -X POST $BASE_URL/api/refund \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "txn_005"}'
echo ""

echo "10. Create Customer"
curl -s -w "\nStatus: %{http_code}\n" -X POST $BASE_URL/api/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test_'$(date +%s)'@example.com"}'
echo ""

echo "=== Test Complete ==="
