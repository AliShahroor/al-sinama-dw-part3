-- =============================================================================
-- Al Sinama Cinema Data Warehouse - Part 3 (Revised Schema)
-- ROLAP Schema Creation Script for PostgreSQL
-- =============================================================================

-- Drop existing tables and views
DROP VIEW IF EXISTS vw_ticket_sales_analysis CASCADE;
DROP TABLE IF EXISTS fact_ticket_sales CASCADE;
DROP TABLE IF EXISTS dim_movie_star CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_time_of_day CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_movie CASCADE;
DROP TABLE IF EXISTS dim_cinema CASCADE;
DROP TABLE IF EXISTS dim_promotion CASCADE;
DROP TABLE IF EXISTS dim_transaction_type CASCADE;
DROP TABLE IF EXISTS dim_age_group CASCADE;

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- dim_date
CREATE TABLE dim_date (
    date_key SERIAL PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    day_name VARCHAR(20) NOT NULL,
    day_of_month INTEGER NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    day_of_year INTEGER NOT NULL CHECK (day_of_year BETWEEN 1 AND 366),
    week_of_year INTEGER NOT NULL CHECK (week_of_year BETWEEN 1 AND 53),
    month_number INTEGER NOT NULL CHECK (month_number BETWEEN 1 AND 12),
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    weekend_indicator VARCHAR(10) NOT NULL CHECK (weekend_indicator IN ('Weekend', 'Weekday'))
);

CREATE INDEX idx_dim_date_year ON dim_date(year);
CREATE INDEX idx_dim_date_month ON dim_date(month_number);
CREATE INDEX idx_dim_date_weekend ON dim_date(is_weekend);
CREATE INDEX idx_dim_date_week ON dim_date(week_of_year);

-- dim_time_of_day
CREATE TABLE dim_time_of_day (
    time_of_day_key SERIAL PRIMARY KEY,
    time_period VARCHAR(20) NOT NULL UNIQUE,
    start_hour INTEGER NOT NULL,
    end_hour INTEGER NOT NULL,
    description VARCHAR(100)
);

INSERT INTO dim_time_of_day (time_period, start_hour, end_hour, description) VALUES
    ('Morning', 6, 11, 'Morning showings from 6:00 AM to 11:59 AM'),
    ('Afternoon', 12, 17, 'Afternoon showings from 12:00 PM to 5:59 PM'),
    ('Night', 18, 5, 'Night showings from 6:00 PM to 5:59 AM');

-- dim_customer
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    customer_name VARCHAR(100),
    gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other', 'Unknown')),
    date_of_birth DATE,
    address VARCHAR(255)
);

CREATE INDEX idx_dim_customer_gender ON dim_customer(gender);
CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id);

-- dim_movie
CREATE TABLE dim_movie (
    movie_key SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    movie_name VARCHAR(200) NOT NULL,
    genre VARCHAR(50),
    release_date DATE,
    language VARCHAR(50),
    cost DECIMAL(15,2),
    country VARCHAR(100),
    director_id INTEGER,
    director_name VARCHAR(100),
    director_gender VARCHAR(10),
    director_dob DATE
);

CREATE INDEX idx_dim_movie_genre ON dim_movie(genre);
CREATE INDEX idx_dim_movie_director ON dim_movie(director_name);
CREATE INDEX idx_dim_movie_id ON dim_movie(movie_id);

-- dim_movie_star (Bridge Table)
CREATE TABLE dim_movie_star (
    movie_star_key SERIAL PRIMARY KEY,
    movie_key INTEGER NOT NULL REFERENCES dim_movie(movie_key),
    star_id INTEGER NOT NULL,
    star_name VARCHAR(100) NOT NULL,
    star_gender VARCHAR(10),
    star_dob DATE
);

CREATE INDEX idx_dim_movie_star_movie ON dim_movie_star(movie_key);
CREATE INDEX idx_dim_movie_star_name ON dim_movie_star(star_name);

-- =============================================================================
-- REVISED: dim_cinema now includes cinema_city
-- This is the key schema change for Part 3
-- =============================================================================
CREATE TABLE dim_cinema (
    cinema_key SERIAL PRIMARY KEY,
    cinema_id INTEGER NOT NULL,
    cinema_name VARCHAR(100),
    cinema_address VARCHAR(255),
    cinema_city VARCHAR(100),             -- NEW: city for city level analysis
    cinema_state VARCHAR(100),
    hall_id INTEGER NOT NULL,
    hall_name VARCHAR(100),
    hall_size INTEGER,
    hall_size_category VARCHAR(20) CHECK (hall_size_category IN ('Small', 'Mid Size', 'Large'))
);

CREATE INDEX idx_dim_cinema_state ON dim_cinema(cinema_state);
CREATE INDEX idx_dim_cinema_city ON dim_cinema(cinema_city);   -- NEW index
CREATE INDEX idx_dim_cinema_size ON dim_cinema(hall_size_category);

-- dim_promotion
CREATE TABLE dim_promotion (
    promotion_key SERIAL PRIMARY KEY,
    promotion_id INTEGER,
    promotion_description VARCHAR(255),
    promotion_type VARCHAR(50),
    discount_percentage DECIMAL(5,2),
    start_date DATE,
    end_date DATE,
    has_promotion BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX idx_dim_promotion_type ON dim_promotion(promotion_type);
CREATE INDEX idx_dim_promotion_has ON dim_promotion(has_promotion);

INSERT INTO dim_promotion (promotion_id, promotion_description, promotion_type, discount_percentage, has_promotion)
VALUES (NULL, 'No Promotion', 'None', 0.00, FALSE);

-- dim_transaction_type
CREATE TABLE dim_transaction_type (
    transaction_type_key SERIAL PRIMARY KEY,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('Online', 'Offline')),
    system VARCHAR(50),
    browser VARCHAR(50)
);

CREATE INDEX idx_dim_trans_type ON dim_transaction_type(transaction_type);
CREATE INDEX idx_dim_trans_browser ON dim_transaction_type(browser);  -- NEW index

-- dim_age_group
CREATE TABLE dim_age_group (
    age_group_key SERIAL PRIMARY KEY,
    age_group_name VARCHAR(30) NOT NULL,
    min_age INTEGER NOT NULL,
    max_age INTEGER NOT NULL,
    age_range VARCHAR(20) NOT NULL,
    sort_order INTEGER NOT NULL
);

INSERT INTO dim_age_group (age_group_name, min_age, max_age, age_range, sort_order) VALUES
    ('Child', 0, 12, '0 to 12', 1),
    ('Teen', 13, 19, '13 to 19', 2),
    ('Young Adult', 20, 35, '20 to 35', 3),
    ('Adult', 36, 55, '36 to 55', 4),
    ('Senior', 56, 120, '56+', 5);

-- =============================================================================
-- FACT TABLE
-- =============================================================================
CREATE TABLE fact_ticket_sales (
    ticket_sales_id SERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    showing_date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    movie_key INTEGER NOT NULL REFERENCES dim_movie(movie_key),
    cinema_key INTEGER NOT NULL REFERENCES dim_cinema(cinema_key),
    promotion_key INTEGER NOT NULL REFERENCES dim_promotion(promotion_key),
    transaction_type_key INTEGER NOT NULL REFERENCES dim_transaction_type(transaction_type_key),
    time_of_day_key INTEGER NOT NULL REFERENCES dim_time_of_day(time_of_day_key),
    transaction_id INTEGER NOT NULL,
    ticket_price DECIMAL(10,2) NOT NULL,
    total_transaction_price DECIMAL(10,2) NOT NULL,
    ticket_count INTEGER NOT NULL,
    customer_age INTEGER,
    discount_amount DECIMAL(10,2) DEFAULT 0.00
);

CREATE INDEX idx_fact_date ON fact_ticket_sales(date_key);
CREATE INDEX idx_fact_showing_date ON fact_ticket_sales(showing_date_key);
CREATE INDEX idx_fact_customer ON fact_ticket_sales(customer_key);
CREATE INDEX idx_fact_movie ON fact_ticket_sales(movie_key);
CREATE INDEX idx_fact_cinema ON fact_ticket_sales(cinema_key);
CREATE INDEX idx_fact_promotion ON fact_ticket_sales(promotion_key);
CREATE INDEX idx_fact_trans_type ON fact_ticket_sales(transaction_type_key);
CREATE INDEX idx_fact_time_of_day ON fact_ticket_sales(time_of_day_key);
CREATE INDEX idx_fact_transaction_id ON fact_ticket_sales(transaction_id);

-- =============================================================================
-- POPULATE DATE DIMENSION (2010 to 2030)
-- =============================================================================
INSERT INTO dim_date (
    full_date, day_of_week, day_name, day_of_month, day_of_year,
    week_of_year, month_number, month_name, quarter, year,
    is_weekend, weekend_indicator
)
SELECT 
    date_val,
    EXTRACT(ISODOW FROM date_val)::INTEGER,
    TRIM(TO_CHAR(date_val, 'Day')),
    EXTRACT(DAY FROM date_val)::INTEGER,
    EXTRACT(DOY FROM date_val)::INTEGER,
    EXTRACT(WEEK FROM date_val)::INTEGER,
    EXTRACT(MONTH FROM date_val)::INTEGER,
    TRIM(TO_CHAR(date_val, 'Month')),
    EXTRACT(QUARTER FROM date_val)::INTEGER,
    EXTRACT(YEAR FROM date_val)::INTEGER,
    CASE WHEN EXTRACT(ISODOW FROM date_val) IN (6, 7) THEN TRUE ELSE FALSE END,
    CASE WHEN EXTRACT(ISODOW FROM date_val) IN (6, 7) THEN 'Weekend' ELSE 'Weekday' END
FROM generate_series('2010-01-01'::DATE, '2030-12-31'::DATE, '1 day'::INTERVAL) AS date_val;

-- =============================================================================
-- VERIFICATION
-- =============================================================================
\echo ''
\echo '=== Revised Schema Created Successfully ==='
\echo '=== Key Change: cinema_city added to dim_cinema ==='
\echo ''

\d dim_cinema
\d fact_ticket_sales
