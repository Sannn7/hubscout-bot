-- Initialize database schema
CREATE TABLE IF NOT EXISTS property_listings (
    id SERIAL PRIMARY KEY,
    listing_id VARCHAR(50) UNIQUE NOT NULL,
    neighborhood VARCHAR(100) NOT NULL,
    property_type VARCHAR(50),
    bedrooms INTEGER,
    bathrooms INTEGER,
    sqft INTEGER,
    price NUMERIC(12, 2),
    listing_date TIMESTAMP,
    description TEXT,
    has_parking BOOLEAN,
    pet_friendly BOOLEAN,
    near_transit BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_neighborhood ON property_listings(neighborhood);
CREATE INDEX idx_price ON property_listings(price);
CREATE INDEX idx_listing_date ON property_listings(listing_date);

-- Query performance tracking
CREATE TABLE IF NOT EXISTS query_metrics (
    id SERIAL PRIMARY KEY,
    query_text TEXT,
    response_time_ms FLOAT,
    precision_score FLOAT,
    sources_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);