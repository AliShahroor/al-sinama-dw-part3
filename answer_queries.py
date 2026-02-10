#!/usr/bin/env python3
"""
Al Sinama Cinema Data Warehouse - Part 3
Query Runner and Result Formatter for Q11 to Q18

Author: Ali Shahroor - 210034060
Course: Advanced Data Management Systems
Date: February 2026

This script connects to the PostgreSQL data warehouse, executes all 8 queries
(Q11 through Q18), formats and displays the results, and optionally saves
them to CSV files for inclusion in the report.
"""

import psycopg2
import csv
import os
import sys
from decimal import Decimal

# ---- Database connection settings ----
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "al_sinama_dw",
    "user": "admin",
    "password": "admin123"
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def get_connection():
    """Create and return a database connection."""
    return psycopg2.connect(**DB_CONFIG)


def run_query(cursor, sql, description):
    """Execute a query and return column names and rows."""
    cursor.execute(sql)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return columns, rows


def format_value(val):
    """Format a value for display."""
    if val is None:
        return "N/A"
    if isinstance(val, Decimal):
        return f"{val:,.2f}"
    if isinstance(val, float):
        return f"{val:,.2f}"
    return str(val)


def print_table(columns, rows, title="", max_rows=30):
    """Print a formatted table to the console."""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)

    if not rows:
        print("  (No results)")
        return

    # Calculate column widths
    widths = [len(c) for c in columns]
    display_rows = rows[:max_rows]
    for row in display_rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(format_value(val)))

    # Print header
    header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    print(f"  {header}")
    print("  " + "-+-".join("-" * w for w in widths))

    # Print rows
    for row in display_rows:
        line = " | ".join(format_value(v).ljust(widths[i]) for i, v in enumerate(row))
        print(f"  {line}")

    if len(rows) > max_rows:
        print(f"  ... ({len(rows) - max_rows} more rows)")

    print(f"\n  Total rows: {len(rows)}")


def save_csv(columns, rows, filename):
    """Save query results to a CSV file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([format_value(v) for v in row])
    print(f"  Saved to {filepath}")


# ===========================================================================
# QUERY DEFINITIONS
# ===========================================================================

Q11 = """
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
"""

Q12 = """
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
"""

Q13 = """
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
"""

Q14_COMBINED = """
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
"""

Q15 = """
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
"""

Q16 = """
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
"""

Q17 = """
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
"""

Q18 = """
WITH city_weekly_sales AS (
    SELECT 
        cin.cinema_city,
        d.year,
        d.week_of_year,
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
"""


def main():
    """Run all queries and display results."""
    print("=" * 80)
    print("  Al Sinama Cinema Data Warehouse")
    print("  Part 3: Query Results (Q11 to Q18)")
    print("=" * 80)

    try:
        conn = get_connection()
        cur = conn.cursor()
        print("\n  Connected to database successfully.\n")
    except Exception as e:
        print(f"\n  ERROR: Could not connect to database: {e}")
        print("  Make sure the Docker container is running and the database exists.")
        sys.exit(1)

    queries = [
        ("Q11", "Rank cinemas per city by total sales in 2018", Q11, "q11_cinema_rank_by_city.csv"),
        ("Q12", "Rank movies per director by sales (customers under 40)", Q12, "q12_movies_per_director.csv"),
        ("Q13", "Rank browsers per city by online transactions", Q13, "q13_browsers_per_city.csv"),
        ("Q14", "Top 10 movies in 2018 by tickets (Male and Female)", Q14_COMBINED, "q14_top10_movies_gender.csv"),
        ("Q15", "Top 5 cinemas per city by tickets (2014 to 2018)", Q15, "q15_top5_cinemas_per_city.csv"),
        ("Q16", "8 week moving average of total sales in 2018", Q16, "q16_moving_avg_8week.csv"),
        ("Q17", "Largest three 4 week moving averages in 2018", Q17, "q17_top3_moving_avg_4week.csv"),
        ("Q18", "Largest 4 week moving average per city (2010 to 2018)", Q18, "q18_largest_4week_avg_per_city.csv"),
    ]

    for qnum, desc, sql, csv_file in queries:
        try:
            columns, rows = run_query(cur, sql, desc)
            print_table(columns, rows, title=f"{qnum}: {desc}")
            save_csv(columns, rows, csv_file)
        except Exception as e:
            print(f"\n  ERROR running {qnum}: {e}")
            conn.rollback()

    cur.close()
    conn.close()
    print("\n" + "=" * 80)
    print("  All queries executed. Results saved to:", OUTPUT_DIR)
    print("=" * 80)


if __name__ == "__main__":
    main()
