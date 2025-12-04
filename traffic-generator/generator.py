#!/usr/bin/env python3
"""
Traffic generator to simulate realistic application load.
Generates a mix of successful requests (read operations) and failing requests (payments).
"""

import requests
import time
import random
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_URL = "http://payment-processor:8080"

# Customer IDs from the database
CUSTOMER_IDS = ["cust_001", "cust_002", "cust_003", "cust_004", "cust_005", "cust_123"]
TRANSACTION_IDS = ["txn_001", "txn_002", "txn_003", "txn_004", "txn_005"]

def make_request(method, endpoint, json_data=None, description=""):
    """Make HTTP request and log result"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=json_data, timeout=5)
        
        status = "✓" if response.status_code < 400 else "✗"
        logger.info(f"{status} {method} {endpoint} → {response.status_code} ({description})")
        return response.status_code
    except requests.exceptions.Timeout:
        logger.warning(f"✗ {method} {endpoint} → TIMEOUT ({description})")
        return None
    except requests.exceptions.ConnectionError:
        logger.error(f"✗ {method} {endpoint} → CONNECTION ERROR ({description})")
        return None
    except Exception as e:
        logger.error(f"✗ {method} {endpoint} → ERROR: {str(e)} ({description})")
        return None

def generate_traffic():
    """Generate realistic traffic patterns"""
    logger.info("Traffic generator started")
    
    # Wait for service to be ready
    logger.info("Waiting for payment-processor to be ready...")
    for i in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                logger.info("Payment processor is ready!")
                break
        except:
            pass
        time.sleep(2)
    else:
        logger.error("Payment processor did not become ready in time")
        return
    
    request_count = 0
    
    while True:
        request_count += 1
        
        # Weighted random selection of operations (realistic traffic pattern)
        # 70% reads, 20% payments, 10% other writes
        rand = random.random()
        
        if rand < 0.25:
            # Get customer details
            customer_id = random.choice(CUSTOMER_IDS)
            make_request("GET", f"/api/customers/{customer_id}", description="fetch customer")
            
        elif rand < 0.45:
            # List transactions
            limit = random.choice([5, 10, 20])
            make_request("GET", f"/api/transactions?limit={limit}", description="list transactions")
            
        elif rand < 0.55:
            # Get transaction details
            txn_id = random.choice(TRANSACTION_IDS)
            make_request("GET", f"/api/transactions/{txn_id}", description="get transaction")
            
        elif rand < 0.65:
            # Get account balance
            customer_id = random.choice(CUSTOMER_IDS)
            make_request("GET", f"/api/accounts/{customer_id}/balance", description="check balance")
            
        elif rand < 0.70:
            # Get payment methods
            customer_id = random.choice(CUSTOMER_IDS)
            make_request("GET", f"/api/payment-methods/{customer_id}", description="get payment methods")
            
        elif rand < 0.75:
            # Get stats
            make_request("GET", "/api/stats", description="fetch stats")
            
        elif rand < 0.92:
            # Process payment (THIS WILL FAIL)
            customer_id = random.choice(CUSTOMER_IDS)
            amount = random.randint(10, 500)
            make_request(
                "POST", 
                "/api/payment",
                json_data={
                    "customer_id": customer_id,
                    "amount": amount,
                    "currency": "USD"
                },
                description=f"payment ${amount}"
            )
            
        elif rand < 0.97:
            # Process refund for large amount (THIS WILL FAIL)
            txn_id = random.choice(["txn_005"])  # Only txn_005 is > $1000
            make_request(
                "POST",
                "/api/refund",
                json_data={"transaction_id": txn_id},
                description=f"refund {txn_id}"
            )
            
        else:
            # Create customer (occasional)
            timestamp = int(time.time())
            make_request(
                "POST",
                "/api/customers",
                json_data={
                    "name": f"Generated User {timestamp}",
                    "email": f"user{timestamp}@example.com"
                },
                description="create customer"
            )
        
        # Log summary every 50 requests
        if request_count % 50 == 0:
            logger.info(f"--- Generated {request_count} requests so far ---")
        
        # Random delay between requests (0.5 to 3 seconds)
        # This creates realistic bursty traffic
        delay = random.uniform(0.1, 1.8)
        time.sleep(delay)

if __name__ == "__main__":
    try:
        generate_traffic()
    except KeyboardInterrupt:
        logger.info("Traffic generator stopped")
    except Exception as e:
        logger.error(f"Traffic generator error: {e}")
        raise
