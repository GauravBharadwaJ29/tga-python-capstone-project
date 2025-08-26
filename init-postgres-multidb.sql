-- Create all needed databases if not exist
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'orders') THEN CREATE DATABASE orders; END IF;
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'inventory') THEN CREATE DATABASE inventory; END IF;
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'store_onboarding') THEN CREATE DATABASE store_onboarding; END IF;
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'payments') THEN CREATE DATABASE payments; END IF;
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'billing') THEN CREATE DATABASE billing; END IF;
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'delivery') THEN CREATE DATABASE delivery; END IF;
END $$;

-- Orders DB
\connect orders
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    customer_contact VARCHAR(50),
    delivery_address TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

-- Inventory DB
\connect inventory
CREATE TABLE IF NOT EXISTS inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_id, store_id)
);

-- Store Onboarding DB
\connect store_onboarding
CREATE TABLE IF NOT EXISTS store (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    status VARCHAR(50),
    onboarded_at TIMESTAMP
);

-- Payments DB
\connect payments
CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Billing DB
\connect billing
CREATE TABLE IF NOT EXISTS billing (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    billing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    due_date TIMESTAMP,
    paid_date TIMESTAMP
);

-- Delivery DB
\connect delivery
CREATE TABLE IF NOT EXISTS delivery (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    delivery_address TEXT NOT NULL,
    delivery_status VARCHAR(50) NOT NULL,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    tracking_number VARCHAR(100)
);
