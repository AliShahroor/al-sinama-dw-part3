-- =============================================================================
-- Al Sinama Cinema Data Warehouse - Part 3
-- SQL Queries for Q11 to Q18 (Ranking, Top-N, Moving Averages)
-- =============================================================================

-- =============================================================================
-- QUERY 11: For each city, rank cinemas by total sales in 2018 (descending)
-- =============================================================================

SELECT 
    cin.cinema_city,
    cin.cinema_name,
    SUM(f.total_transaction_price) AS total_sales,
    RANK() OVER (
        PARTITION BY cin.cinema_city 
        ORDER BY SUM(f.total_transaction_price) DESC
    ) AS sales_rank
FROM fact_ticket_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_cinema cin ON f.cinema_key = cin.cinema_key
WHERE d.year = 2018
GROUP BY cin.cinema_city, cin.cinema_name
ORDER BY cin.cinema_city, sales_rank;


-- =============================================================================
-- QUERY 12: For each director, rank movies by total sales for customers
--           with ages under 40 at time of purchase (descending)
-- =============================================================================

SELECT 
    m.director_name,
    m.movie_name,
    SUM(f.total_transaction_price) AS total_sales,
    RANK() OVER (
        PARTITION BY m.director_name 
        ORDER BY SUM(f.total_transaction_price) DESC
    ) AS movie_rank
FROM fact_ticket_sales f
JOIN dim_movie m ON f.movie_key = m.movie_key
WHERE f.customer_age < 40
GROUP BY m.director_name, m.movie_name
ORDER BY m.director_name, movie_rank;


-- =============================================================================
-- QUERY 13: For each city, rank browsers by total number of online
--           transactions (descending)
-- =============================================================================

SELECT 
    cin.cinema_city,
    tt.browser,
    COUNT(DISTINCT f.transaction_id) AS total_transactions,
    RANK() OVER (
        PARTITION BY cin.cinema_city 
        ORDER BY COUNT(DISTINCT f.transaction_id) DESC
    ) AS browser_rank
FROM fact_ticket_sales f
JOIN dim_cinema cin ON f.cinema_key = cin.cinema_key
JOIN dim_transaction_type tt ON f.transaction_type_key = tt.transaction_type_key
WHERE tt.transaction_type = 'Online'
  AND tt.browser IS NOT NULL
GROUP BY cin.cinema_city, tt.browser
ORDER BY cin.cinema_city, browser_rank;


-- =============================================================================
-- QUERY 14: Top 10 movies in 2018 by total tickets sold, for Male and 
--           Female customers respectively
-- =============================================================================

-- Male customers top 10
SELECT * FROM (
    SELECT 
        m.movie_name,
        c.gender,
        SUM(f.ticket_count) AS total_tickets,
        RANK() OVER (ORDER BY SUM(f.ticket_count) DESC) AS movie_rank
    FROM fact_ticket_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_movie m ON f.movie_key = m.movie_key
    JOIN dim_customer c ON f.customer_key = c.customer_key
    WHERE d.year = 2018 AND c.gender = 'Male'
    GROUP BY m.movie_name, c.gender
) ranked
WHERE movie_rank <= 10
ORDER BY movie_rank;

-- Female customers top 10
SELECT * FROM (
    SELECT 
        m.movie_name,
        c.gender,
        SUM(f.ticket_count) AS total_tickets,
        RANK() OVER (ORDER BY SUM(f.ticket_count) DESC) AS movie_rank
    FROM fact_ticket_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_movie m ON f.movie_key = m.movie_key
    JOIN dim_customer c ON f.customer_key = c.customer_key
    WHERE d.year = 2018 AND c.gender = 'Female'
    GROUP BY m.movie_name, c.gender
) ranked
WHERE movie_rank <= 10
ORDER BY movie_rank;

-- Combined version (both genders in one query)
SELECT * FROM (
    SELECT 
        c.gender,
        m.movie_name,
        SUM(f.ticket_count) AS total_tickets,
        RANK() OVER (
            PARTITION BY c.gender 
            ORDER BY SUM(f.ticket_count) DESC
        ) AS movie_rank
    FROM fact_ticket_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_movie m ON f.movie_key = m.movie_key
    JOIN dim_customer c ON f.customer_key = c.customer_key
    WHERE d.year = 2018 AND c.gender IN ('Male', 'Female')
    GROUP BY c.gender, m.movie_name
) ranked
WHERE movie_rank <= 10
ORDER BY gender, movie_rank;


-- =============================================================================
-- QUERY 15: For each city, top 5 cinemas by total tickets sold (2014 to 2018)
-- =============================================================================

SELECT * FROM (
    SELECT 
        cin.cinema_city,
        cin.cinema_name,
        SUM(f.ticket_count) AS total_tickets,
        RANK() OVER (
            PARTITION BY cin.cinema_city 
            ORDER BY SUM(f.ticket_count) DESC
        ) AS cinema_rank
    FROM fact_ticket_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_cinema cin ON f.cinema_key = cin.cinema_key
    WHERE d.year BETWEEN 2014 AND 2018
    GROUP BY cin.cinema_city, cin.cinema_name
) ranked
WHERE cinema_rank <= 5
ORDER BY cinema_city, cinema_rank;


-- =============================================================================
-- QUERY 16: 8 week moving average of total sales for each week in 2018
-- =============================================================================

WITH weekly_sales AS (
    SELECT 
        d.year,
        d.week_of_year,
        SUM(f.total_transaction_price) AS weekly_total
    FROM fact_ticket_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.year = 2018
    GROUP BY d.year, d.week_of_year
)
SELECT 
    year,
    week_of_year,
    weekly_total,
    AVG(weekly_total) OVER (
        ORDER BY week_of_year 
        ROWS BETWEEN 7 PRECEDING AND CURRENT ROW
    ) AS moving_avg_8_week
FROM weekly_sales
ORDER BY week_of_year;


-- =============================================================================
-- QUERY 17: Largest three 4 week moving averages among weeks in 2018
-- =============================================================================

WITH weekly_sales AS (
    SELECT 
        d.year,
        d.week_of_year,
        SUM(f.total_transaction_price) AS weekly_total
    FROM fact_ticket_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.year = 2018
    GROUP BY d.year, d.week_of_year
),
moving_avgs AS (
    SELECT 
        week_of_year,
        weekly_total,
        AVG(weekly_total) OVER (
            ORDER BY week_of_year 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS moving_avg_4_week,
        COUNT(*) OVER (
            ORDER BY week_of_year 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS window_size
    FROM weekly_sales
)
SELECT 
    week_of_year,
    weekly_total,
    moving_avg_4_week
FROM moving_avgs
WHERE window_size = 4
ORDER BY moving_avg_4_week DESC
LIMIT 3;


-- =============================================================================
-- QUERY 18: For each city, largest 4 week moving average of total sales
--           from 2010 to 2018
-- =============================================================================

WITH city_weekly_sales AS (
    SELECT 
        cin.cinema_city,
        d.year,
        d.week_of_year,
        -- Create a continuous week number for proper ordering across years
        (d.year - 2010) * 53 + d.week_of_year AS absolute_week,
        SUM(f.total_transaction_price) AS weekly_total
    FROM fact_ticket_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_cinema cin ON f.cinema_key = cin.cinema_key
    WHERE d.year BETWEEN 2010 AND 2018
    GROUP BY cin.cinema_city, d.year, d.week_of_year
),
city_moving_avgs AS (
    SELECT 
        cinema_city,
        year,
        week_of_year,
        weekly_total,
        AVG(weekly_total) OVER (
            PARTITION BY cinema_city 
            ORDER BY absolute_week 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS moving_avg_4_week,
        COUNT(*) OVER (
            PARTITION BY cinema_city 
            ORDER BY absolute_week 
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS window_size
    FROM city_weekly_sales
),
ranked AS (
    SELECT 
        cinema_city,
        year,
        week_of_year,
        moving_avg_4_week,
        RANK() OVER (
            PARTITION BY cinema_city 
            ORDER BY moving_avg_4_week DESC
        ) AS rk
    FROM city_moving_avgs
    WHERE window_size = 4
)
SELECT 
    cinema_city,
    year,
    week_of_year,
    moving_avg_4_week AS largest_4_week_moving_avg
FROM ranked
WHERE rk = 1
ORDER BY cinema_city;


-- =============================================================================
-- END OF QUERIES
-- =============================================================================
