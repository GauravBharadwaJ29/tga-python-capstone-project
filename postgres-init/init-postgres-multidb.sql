
-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_contact VARCHAR(50),
    delivery_address TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE orders ADD COLUMN customer_id INTEGER;
ALTER TABLE orders ADD COLUMN amount NUMERIC(10,2);
ALTER TABLE orders ADD COLUMN payment_method VARCHAR(50);
ALTER TABLE orders ADD COLUMN store_id INTEGER NOT NULL DEFAULT 1;


-- Order items table
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

-- Inventory table
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR NOT NULL,
    store_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, store_id)
);

-- Note: Default 0 is placeholder; adjust as needed.
-- Also, add UNIQUE constraint if not present:
ALTER TABLE inventory ADD CONSTRAINT unique_product_store UNIQUE (product_id, store_id);


-- Store table
CREATE TABLE IF NOT EXISTS store (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    status VARCHAR(50),
    onboarded_at TIMESTAMP
);
ALTER TABLE store RENAME TO stores;

INSERT INTO stores (name, address, contact_email, contact_phone, status)
VALUES ('India Store', 'Delhi', 'delhi@example.com', '1234567890', 'active');
INSERT INTO stores (name, address, contact_email, contact_phone, status)
VALUES ('Canada', 'Toronto', 'toronto@example.com', '2234567890', 'active');



CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payment_items (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER REFERENCES payments(id) ON DELETE CASCADE,
    product_id VARCHAR(100),
    quantity INTEGER,
    price FLOAT
);

-- Billing table
CREATE TABLE IF NOT EXISTS billing (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    billing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    due_date TIMESTAMP,
    paid_date TIMESTAMP
);
ALTER TABLE billing
    ADD COLUMN IF NOT EXISTS customer_id INTEGER,
    ADD COLUMN IF NOT EXISTS customer_name VARCHAR,
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR;
   ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS billing_items (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES billing(id) ON DELETE CASCADE,
    product_id VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    price FLOAT NOT NULL
);
ALTER TABLE billing_items RENAME COLUMN bill_id TO billing_id;
CREATE TABLE IF NOT EXISTS billing_audit_log (
    id SERIAL PRIMARY KEY,
    billing_id INTEGER NOT NULL REFERENCES billing(id) ON DELETE CASCADE,
    old_status VARCHAR(50) NOT NULL,
    new_status VARCHAR(50) NOT NULL,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Delivery table
CREATE TABLE IF NOT EXISTS deliveries (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    delivery_address TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP    
);
ALTER TABLE deliveries ADD COLUMN assigned_to VARCHAR;
CREATE TABLE IF NOT EXISTS delivery_items (
    id SERIAL PRIMARY KEY,
    delivery_id INTEGER REFERENCES deliveries(id) ON DELETE CASCADE,
    product_id VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL -- or FLOAT if you change your model field to Float
);
