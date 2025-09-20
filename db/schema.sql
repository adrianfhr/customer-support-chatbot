-- Customer Support Chatbot Database Schema
-- PostgreSQL compatible DDL

-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Messages table for conversation history
CREATE TABLE IF NOT EXISTS messages (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    turn_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_turn_index ON messages(turn_index);
CREATE INDEX IF NOT EXISTS idx_messages_session_turn ON messages(session_id, turn_index);

-- Orders table for order status lookups
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
    last_update_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    eta_date TIMESTAMP WITH TIME ZONE,
    carrier VARCHAR(100),
    tracking_number VARCHAR(100)
);

-- Index for order lookups
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Products table for product information
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    features TEXT,
    price NUMERIC(12, 2),
    stock INTEGER
);

-- Index for product name searches
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

-- Policies table for warranty and other policies
CREATE TABLE IF NOT EXISTS policies (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    type VARCHAR(50) NOT NULL,
    content_markdown TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for policy type lookups
CREATE INDEX IF NOT EXISTS idx_policies_type ON policies(type);

-- Create a function to update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_policies_updated_at 
    BEFORE UPDATE ON policies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
