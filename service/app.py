import os
import time
import logging
import random
from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

app = Flask(__name__)
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO').upper())
logger = logging.getLogger(__name__)

FRAUD_CHECK_URL = os.getenv('FRAUD_CHECK_URL', 'http://fraud-api.internal.corp:8443/verify')
FRAUD_CHECK_TIMEOUT = float(os.getenv('FRAUD_CHECK_TIMEOUT', '2').rstrip('s'))
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://paymentuser:paymentpass123@postgres:5432/payments')

# Database connection
try:
    engine = create_engine(DATABASE_URL, poolclass=NullPool)
    logger.info("Database connection established")
except Exception as e:
    logger.error(f"Failed to connect to database: {e}")
    engine = None

@app.route('/health')
def health():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "unknown"
    }
    
    # Check database connectivity
    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            health_status["database"] = "disconnected"
            health_status["status"] = "degraded"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), status_code

@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get customer details - this endpoint works fine"""
    logger.info(f"Customer lookup: {customer_id}")
    
    # Add occasional benign warning to create noise
    if random.random() < 0.15:
        logger.warning(f"Cache miss - fetching {customer_id} from database")
    
    if not engine:
        return jsonify({"error": "Database unavailable"}), 503
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT customer_id, name, email, account_balance, status, created_at FROM customers WHERE customer_id = :cid"),
                {"cid": customer_id}
            )
            row = result.fetchone()
            
            if row:
                customer = {
                    "customer_id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "account_balance": float(row[3]),
                    "status": row[4],
                    "created_at": row[5].isoformat() if row[5] else None
                }
                return jsonify(customer), 200
            else:
                return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/customers', methods=['POST'])
def create_customer():
    """Create a new customer - works fine"""
    data = request.get_json()
    customer_id = f"cust_{int(time.time())}_{random.randint(1000, 9999)}"
    
    logger.info(f"Creating customer {customer_id}")
    
    if not engine:
        return jsonify({"error": "Database unavailable"}), 503
    
    try:
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO customers (customer_id, name, email, account_balance, status)
                    VALUES (:cid, :name, :email, 0.00, 'active')
                """),
                {"cid": customer_id, "name": data.get('name'), "email": data.get('email')}
            )
            conn.commit()
        
        customer = {
            "customer_id": customer_id,
            "name": data.get('name'),
            "email": data.get('email'),
            "account_balance": 0.00,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        return jsonify(customer), 201
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/payment-methods/<customer_id>', methods=['GET'])
def get_payment_methods(customer_id):
    """Get customer payment methods - works fine"""
    logger.info(f"Loading payment methods: {customer_id}")
    
    if not engine:
        return jsonify({"error": "Database unavailable"}), 503
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT payment_method_id, method_type, last4, brand, exp_month, exp_year, is_default
                    FROM payment_methods
                    WHERE customer_id = :cid
                """),
                {"cid": customer_id}
            )
            
            methods = []
            for row in result:
                methods.append({
                    "payment_method_id": row[0],
                    "type": row[1],
                    "last4": row[2],
                    "brand": row[3],
                    "exp_month": row[4],
                    "exp_year": row[5],
                    "is_default": row[6]
                })
            
            return jsonify({"customer_id": customer_id, "payment_methods": methods}), 200
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/transactions', methods=['GET'])
def list_transactions():
    """List recent transactions - works fine"""
    logger.info("Listing transactions")
    
    if not engine:
        return jsonify({"error": "Database unavailable"}), 503
    
    try:
        limit = int(request.args.get('limit', 10))
        customer_id = request.args.get('customer_id')
        
        query = """
            SELECT transaction_id, customer_id, amount, currency, transaction_type, 
                   status, fraud_check_status, created_at
            FROM transactions
        """
        params = {}
        
        if customer_id:
            query += " WHERE customer_id = :cid"
            params["cid"] = customer_id
        
        query += " ORDER BY created_at DESC LIMIT :limit"
        params["limit"] = limit
        
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            
            txn_list = []
            for row in result:
                txn_list.append({
                    "transaction_id": row[0],
                    "customer_id": row[1],
                    "amount": float(row[2]),
                    "currency": row[3],
                    "transaction_type": row[4],
                    "status": row[5],
                    "fraud_check_status": row[6],
                    "created_at": row[7].isoformat() if row[7] else None
                })
            
            return jsonify({
                "transactions": txn_list,
                "count": len(txn_list)
            }), 200
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/transactions/<transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """Get transaction details - works fine"""
    logger.info(f"Fetching transaction {transaction_id}")
    
    if not engine:
        return jsonify({"error": "Database unavailable"}), 503
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT transaction_id, customer_id, amount, currency, transaction_type,
                           status, fraud_check_status, created_at, metadata
                    FROM transactions
                    WHERE transaction_id = :tid
                """),
                {"tid": transaction_id}
            )
            row = result.fetchone()
            
            if row:
                transaction = {
                    "transaction_id": row[0],
                    "customer_id": row[1],
                    "amount": float(row[2]),
                    "currency": row[3],
                    "transaction_type": row[4],
                    "status": row[5],
                    "fraud_check_status": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "metadata": row[8]
                }
                return jsonify(transaction), 200
            else:
                return jsonify({"error": "Transaction not found"}), 404
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/payment', methods=['POST'])
def process_payment():
    """Process payment - THIS IS THE FAILING ENDPOINT"""
    start_time = time.time()
    data = request.get_json()
    
    logger.info(f"Processing payment for customer {data.get('customer_id')}, amount: {data.get('amount')}")
    
    # Validate input
    if not data.get('amount') or not data.get('customer_id'):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Perform fraud verification check
    try:
        logger.info(f"Starting verification process for payment")
        fraud_response = requests.post(
            FRAUD_CHECK_URL,
            json={"customer_id": data.get('customer_id'), "amount": data.get('amount')},
            timeout=FRAUD_CHECK_TIMEOUT
        )
        
        if fraud_response.status_code != 200:
            logger.error(f"Verification service returned error status: {fraud_response.status_code}")
            return jsonify({"error": "Verification failed"}), 503
            
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        logger.error(f"Request timeout after {duration:.2f}s - upstream service not responding")
        return jsonify({"error": "Service timeout", "details": "Upstream service unavailable"}), 504
    except requests.exceptions.ConnectionError as e:
        duration = time.time() - start_time
        logger.error(f"Connection failed after {duration:.2f}s - {str(e)}")
        return jsonify({"error": "Service unavailable", "details": "Upstream dependency error"}), 503
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Payment processing error: {str(e)}")
        return jsonify({"error": "Internal error"}), 500
    
    # If we got here, payment succeeded
    duration = time.time() - start_time
    transaction_id = f"txn_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Save to database
    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO transactions (transaction_id, customer_id, amount, currency, 
                                                transaction_type, status, fraud_check_status)
                        VALUES (:tid, :cid, :amount, :currency, 'payment', 'success', 'passed')
                    """),
                    {
                        "tid": transaction_id,
                        "cid": data.get('customer_id'),
                        "amount": data.get('amount'),
                        "currency": data.get('currency', 'USD')
                    }
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save transaction to database: {e}")
    
    transaction = {
        "transaction_id": transaction_id,
        "customer_id": data.get('customer_id'),
        "amount": data.get('amount'),
        "currency": data.get('currency', 'USD'),
        "status": "success",
        "fraud_check_status": "passed",
        "created_at": datetime.utcnow().isoformat(),
        "duration_ms": int(duration * 1000)
    }
    
    logger.info(f"Payment processed successfully in {duration:.2f}s")
    return jsonify(transaction), 200

@app.route('/api/refund', methods=['POST'])
def process_refund():
    """Process refund - also calls fraud check, so also fails"""
    start_time = time.time()
    data = request.get_json()
    
    transaction_id = data.get('transaction_id')
    logger.info(f"Processing refund for transaction {transaction_id}")
    
    if not transaction_id:
        return jsonify({"error": "Missing transaction_id"}), 400
    
    if not engine:
        return jsonify({"error": "Database unavailable"}), 503
    
    # Look up original transaction from database
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT transaction_id, customer_id, amount FROM transactions WHERE transaction_id = :tid"),
                {"tid": transaction_id}
            )
            row = result.fetchone()
            
            if not row:
                return jsonify({"error": "Transaction not found"}), 404
            
            original_txn = {
                "transaction_id": row[0],
                "customer_id": row[1],
                "amount": float(row[2])
            }
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500
    
    # Refunds also require fraud check for large amounts
    if original_txn.get('amount', 0) > 1000:
        try:
            logger.info(f"Processing refund verification for large transaction")
            fraud_response = requests.post(
                FRAUD_CHECK_URL,
                json={"transaction_id": transaction_id, "type": "refund"},
                timeout=FRAUD_CHECK_TIMEOUT
            )
            
            if fraud_response.status_code != 200:
                logger.error(f"Fraud check failed with status {fraud_response.status_code}")
                return jsonify({"error": "Fraud check failed"}), 503
                
        except requests.exceptions.Timeout:
            duration = time.time() - start_time
            logger.error(f"Refund verification timeout - took {duration:.2f}s")
            return jsonify({"error": "Service timeout", "details": "Upstream service unavailable"}), 504
        except requests.exceptions.ConnectionError as e:
            duration = time.time() - start_time
            logger.error(f"Unable to complete refund verification - connection issue: {str(e)}")
            return jsonify({"error": "Service unavailable", "details": "Upstream dependency error"}), 503
    
    # Process refund
    refund_id = f"ref_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Save refund to database
    if engine:
        try:
            with engine.connect() as conn:
                conn.execute(
                    text("""
                        INSERT INTO transactions (transaction_id, customer_id, amount, currency, 
                                                transaction_type, status, fraud_check_status)
                        VALUES (:tid, :cid, :amount, 'USD', 'refund', 'success', 'passed')
                    """),
                    {
                        "tid": refund_id,
                        "cid": original_txn.get('customer_id'),
                        "amount": original_txn.get('amount')
                    }
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to save refund to database: {e}")
    
    refund = {
        "refund_id": refund_id,
        "transaction_id": transaction_id,
        "amount": original_txn.get('amount'),
        "status": "success",
        "created_at": datetime.utcnow().isoformat()
    }
    
    logger.info("Refund processed successfully")
    return jsonify(refund), 200

@app.route('/api/accounts/<customer_id>/balance', methods=['GET'])
def get_account_balance(customer_id):
    """Get customer account balance - works fine"""
    logger.info(f"Fetching account balance for {customer_id}")
    
    if not engine:
        return jsonify({"error": "Database unavailable"}), 503
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT customer_id, balance, currency, last_updated
                    FROM account_balances
                    WHERE customer_id = :cid
                """),
                {"cid": customer_id}
            )
            row = result.fetchone()
            
            if row:
                balance = {
                    "customer_id": row[0],
                    "balance": float(row[1]),
                    "currency": row[2],
                    "last_updated": row[3].isoformat() if row[3] else None
                }
                return jsonify(balance), 200
            else:
                return jsonify({"error": "Account not found"}), 404
    except Exception as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get service statistics - works fine"""
    logger.info("Fetching stats")
    
    stats = {
        "uptime_seconds": int(time.time() % 86400),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if engine:
        try:
            with engine.connect() as conn:
                # Get transaction count
                result = conn.execute(text("SELECT COUNT(*) FROM transactions"))
                stats["total_transactions"] = result.fetchone()[0]
                
                # Get customer count
                result = conn.execute(text("SELECT COUNT(*) FROM customers"))
                stats["total_customers"] = result.fetchone()[0]
                
                # Get recent transaction stats
                result = conn.execute(text("""
                    SELECT status, COUNT(*) 
                    FROM transactions 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                    GROUP BY status
                """))
                stats["last_hour"] = {row[0]: row[1] for row in result}
                
                # Add some noise - check connection pool (benign warning)
                if random.random() < 0.3:
                    logger.warning("Connection pool usage at 40% - within normal range")
        except Exception as e:
            logger.error(f"Database error fetching stats: {e}")
            stats["database_error"] = str(e)
    
    return jsonify(stats), 200

@app.route('/api/webhooks/payment-gateway', methods=['POST'])
def payment_gateway_webhook():
    """Webhook endpoint for payment gateway - works fine"""
    data = request.get_json()
    logger.info(f"Received webhook: {data.get('event_type')}")
    time.sleep(0.02)
    
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
