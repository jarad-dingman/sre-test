-- Initialize payment processor database

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    account_balance DECIMAL(10, 2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    transaction_type VARCHAR(20) NOT NULL, -- 'payment', 'refund', 'transfer'
    status VARCHAR(20) NOT NULL, -- 'success', 'failed', 'pending'
    fraud_check_status VARCHAR(20), -- 'passed', 'failed', 'skipped', 'unavailable'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS payment_methods (
    payment_method_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    method_type VARCHAR(20) NOT NULL, -- 'card', 'bank_account', 'wallet'
    last4 VARCHAR(4),
    brand VARCHAR(50),
    exp_month INTEGER,
    exp_year INTEGER,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS account_balances (
    balance_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(customer_id),
    balance DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO customers (customer_id, name, email, account_balance, status) VALUES
    ('cust_001', 'Alice Johnson', 'alice@example.com', 1250.00, 'active'),
    ('cust_002', 'Bob Smith', 'bob@example.com', 3400.50, 'active'),
    ('cust_003', 'Carol White', 'carol@example.com', 890.25, 'active'),
    ('cust_004', 'David Brown', 'david@example.com', 0.00, 'active'),
    ('cust_005', 'Eve Davis', 'eve@example.com', 5600.00, 'active'),
    ('cust_123', 'Test Customer', 'test@example.com', 10000.00, 'active')
ON CONFLICT (customer_id) DO NOTHING;

INSERT INTO payment_methods (payment_method_id, customer_id, method_type, last4, brand, exp_month, exp_year, is_default) VALUES
    ('pm_001', 'cust_001', 'card', '4242', 'visa', 12, 2025, true),
    ('pm_002', 'cust_002', 'card', '5555', 'mastercard', 6, 2026, true),
    ('pm_003', 'cust_003', 'card', '3782', 'amex', 9, 2025, true),
    ('pm_004', 'cust_005', 'bank_account', '6789', 'chase', NULL, NULL, true),
    ('pm_123', 'cust_123', 'card', '4242', 'visa', 12, 2025, true)
ON CONFLICT (payment_method_id) DO NOTHING;

INSERT INTO transactions (transaction_id, customer_id, amount, currency, transaction_type, status, fraud_check_status, created_at) VALUES
    ('txn_001', 'cust_001', 150.00, 'USD', 'payment', 'success', 'passed', NOW() - INTERVAL '2 hours'),
    ('txn_002', 'cust_002', 250.00, 'USD', 'payment', 'success', 'passed', NOW() - INTERVAL '1 hour'),
    ('txn_003', 'cust_003', 75.50, 'USD', 'payment', 'success', 'passed', NOW() - INTERVAL '45 minutes'),
    ('txn_004', 'cust_001', 50.00, 'USD', 'refund', 'success', 'skipped', NOW() - INTERVAL '30 minutes'),
    ('txn_005', 'cust_005', 1200.00, 'USD', 'payment', 'success', 'passed', NOW() - INTERVAL '25 minutes')
ON CONFLICT (transaction_id) DO NOTHING;

INSERT INTO account_balances (customer_id, balance, currency) VALUES
    ('cust_001', 1250.00, 'USD'),
    ('cust_002', 3400.50, 'USD'),
    ('cust_003', 890.25, 'USD'),
    ('cust_004', 0.00, 'USD'),
    ('cust_005', 5600.00, 'USD'),
    ('cust_123', 10000.00, 'USD');

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_payment_methods_customer_id ON payment_methods(customer_id);
CREATE INDEX IF NOT EXISTS idx_account_balances_customer_id ON account_balances(customer_id);

-- Create a view for transaction summaries
CREATE OR REPLACE VIEW transaction_summary AS
SELECT 
    t.transaction_id,
    t.customer_id,
    c.name as customer_name,
    c.email as customer_email,
    t.amount,
    t.currency,
    t.transaction_type,
    t.status,
    t.fraud_check_status,
    t.created_at
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
ORDER BY t.created_at DESC;
