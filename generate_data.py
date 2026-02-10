"""
Al Sinama Cinema Data Warehouse - Synthetic Data Generator

Generates synthetic data for the Al Sinama cinema data warehouse.
Data spans 2014 to 2026 with at least 1,000,000 fact table rows.

Requirements: pip install psycopg2-binary faker numpy
"""

import psycopg2
import random
import numpy as np
from datetime import datetime, timedelta, date
from faker import Faker
import sys
import time

# ============================================================================
# Configuration
# ============================================================================

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "al_sinama_dw",
    "user": "admin",
    "password": "admin123"
}

FACT_TABLE_TARGET = 1_100_000  # target rows in fact table
BATCH_SIZE = 10_000            # insert batch size
START_YEAR = 2014
END_YEAR = 2026

fake = Faker()
random.seed(42)
np.random.seed(42)

# ============================================================================
# Reference Data
# ============================================================================

CITIES_AND_STATES = [
    ("Cairo", "Cairo Governorate"),
    ("Alexandria", "Alexandria Governorate"),
    ("Giza", "Giza Governorate"),
    ("Luxor", "Luxor Governorate"),
    ("Aswan", "Aswan Governorate"),
    ("Mansoura", "Dakahlia Governorate"),
    ("Tanta", "Gharbia Governorate"),
    ("Ismailia", "Ismailia Governorate"),
    ("Port Said", "Port Said Governorate"),
    ("Suez", "Suez Governorate"),
    ("Hurghada", "Red Sea Governorate"),
    ("Sharm El Sheikh", "South Sinai Governorate"),
]

CINEMA_NAMES = [
    "Al Sinama Grand", "Al Sinama Royal", "Al Sinama Palace",
    "Al Sinama Star", "Al Sinama Diamond", "Al Sinama Gold",
    "Al Sinama Silver", "Al Sinama Plaza", "Al Sinama Mall",
    "Al Sinama Central", "Al Sinama City", "Al Sinama Park",
    "Al Sinama Tower", "Al Sinama Bay", "Al Sinama Oasis",
    "Al Sinama Nile", "Al Sinama Corniche", "Al Sinama Sphinx",
    "Al Sinama Pyramid", "Al Sinama Metro",
]

GENRES = [
    "Action", "Comedy", "Drama", "Horror", "Sci-Fi",
    "Romance", "Thriller", "Animation", "Documentary", "Adventure"
]

LANGUAGES = ["Arabic", "English", "French", "Hindi", "Turkish"]
COUNTRIES = ["Egypt", "USA", "UK", "France", "India", "Turkey", "Lebanon"]

DIRECTORS = [
    ("Mohamed Khan", "Male"),
    ("Youssef Chahine", "Male"),
    ("Daoud Abdel Sayed", "Male"),
    ("Kamla Abu Zekry", "Female"),
    ("Hala Khalil", "Female"),
    ("Marwan Hamed", "Male"),
    ("Sherif Arafa", "Male"),
    ("Khairy Beshara", "Male"),
    ("Sandra Nashaat", "Female"),
    ("Ahmed Nader Galal", "Male"),
    ("Tarek Alarian", "Male"),
    ("Mohamed Diab", "Male"),
    ("Amr Salama", "Male"),
    ("Peter Mimi", "Male"),
    ("Hadi El Bagoury", "Male"),
]

STARS = [
    ("Omar Sharif", "Male"),
    ("Adel Imam", "Male"),
    ("Ahmed Zaki", "Male"),
    ("Ahmed Helmy", "Male"),
    ("Karim Abdel Aziz", "Male"),
    ("Mona Zaki", "Female"),
    ("Yousra", "Female"),
    ("Hend Sabry", "Female"),
    ("Nelly Karim", "Female"),
    ("Asser Yassin", "Male"),
    ("Amr Youssef", "Male"),
    ("Mohamed Ramadan", "Male"),
    ("Menna Shalaby", "Female"),
    ("Yasmine Raeis", "Female"),
    ("Tamer Hosny", "Male"),
    ("Ruby", "Female"),
    ("Ahmed Ezz", "Male"),
    ("Ghada Adel", "Female"),
    ("Nour El Sherif", "Male"),
    ("Laila Elwi", "Female"),
]

BROWSERS = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
SYSTEMS = ["Windows", "macOS", "iOS", "Android", "Linux"]

PROMOTION_TYPES = [
    ("Student Discount", "Student", 15.0),
    ("Senior Citizen", "Senior", 20.0),
    ("Early Bird", "Early Bird", 10.0),
    ("Weekend Special", "Weekend", 12.0),
    ("Holiday Sale", "Holiday", 25.0),
    ("Family Pack", "Family", 18.0),
    ("Loyalty Reward", "Loyalty", 10.0),
    ("Flash Sale", "Flash", 30.0),
    ("Group Booking", "Group", 15.0),
    ("New Member", "New Member", 20.0),
]

HALL_CONFIGS = [
    ("Hall A", 40, "Small"),
    ("Hall B", 80, "Mid Size"),
    ("Hall C", 120, "Mid Size"),
    ("Hall D", 200, "Large"),
    ("Hall E", 300, "Large"),
    ("Hall F", 30, "Small"),
    ("Hall G", 100, "Mid Size"),
    ("Hall H", 250, "Large"),
]


def get_connection():
    """Create database connection."""
    return psycopg2.connect(**DB_CONFIG)


def print_progress(current, total, label="Progress"):
    """Print progress bar."""
    pct = current / total * 100
    bar_len = 40
    filled = int(bar_len * current // total)
    bar = "=" * filled + "-" * (bar_len - filled)
    print(f"\r{label}: [{bar}] {pct:.1f}% ({current:,}/{total:,})", end="", flush=True)
    if current == total:
        print()


# ============================================================================
# Populate Dimension Tables
# ============================================================================

def populate_customers(conn):
    """Generate 5000 customers."""
    print("Generating customers...")
    cur = conn.cursor()
    customers = []
    genders = ["Male", "Female"]
    
    for i in range(1, 5001):
        gender = random.choice(genders)
        if gender == "Male":
            name = fake.name_male()
        else:
            name = fake.name_female()
        
        dob = fake.date_of_birth(minimum_age=8, maximum_age=80)
        address = fake.address().replace("\n", ", ")
        customers.append((i, name, gender, dob, address))
    
    cur.executemany(
        """INSERT INTO dim_customer (customer_id, customer_name, gender, date_of_birth, address)
           VALUES (%s, %s, %s, %s, %s)""",
        customers
    )
    conn.commit()
    cur.close()
    print(f"  Inserted {len(customers)} customers")
    return len(customers)


def populate_movies(conn):
    """Generate 200 movies with directors and stars."""
    print("Generating movies...")
    cur = conn.cursor()
    
    movie_titles = set()
    while len(movie_titles) < 200:
        title = fake.catch_phrase() + " " + random.choice(["", "2", "Returns", "Rising", "Legacy"])
        movie_titles.add(title.strip())
    
    movie_titles = list(movie_titles)[:200]
    movies = []
    
    for i, title in enumerate(movie_titles, 1):
        genre = random.choice(GENRES)
        release_year = random.randint(2010, 2025)
        release_date = date(release_year, random.randint(1, 12), random.randint(1, 28))
        language = random.choice(LANGUAGES)
        cost = round(random.uniform(500000, 50000000), 2)
        country = random.choice(COUNTRIES)
        director_name, director_gender = random.choice(DIRECTORS)
        director_id = DIRECTORS.index((director_name, director_gender)) + 1
        director_dob = fake.date_of_birth(minimum_age=30, maximum_age=75)
        
        movies.append((
            i, title, genre, release_date, language, cost, country,
            director_id, director_name, director_gender, director_dob
        ))
    
    cur.executemany(
        """INSERT INTO dim_movie (movie_id, movie_name, genre, release_date, language, cost, 
           country, director_id, director_name, director_gender, director_dob)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        movies
    )
    conn.commit()
    
    # Now populate the bridge table for movie stars
    print("Generating movie stars...")
    movie_stars = []
    for i in range(1, 201):
        num_stars = random.randint(2, 5)
        selected_stars = random.sample(STARS, num_stars)
        for star_name, star_gender in selected_stars:
            star_id = STARS.index((star_name, star_gender)) + 1
            star_dob = fake.date_of_birth(minimum_age=25, maximum_age=70)
            movie_stars.append((i, star_id, star_name, star_gender, star_dob))
    
    cur.executemany(
        """INSERT INTO dim_movie_star (movie_key, star_id, star_name, star_gender, star_dob)
           VALUES (%s, %s, %s, %s, %s)""",
        movie_stars
    )
    conn.commit()
    cur.close()
    print(f"  Inserted {len(movies)} movies and {len(movie_stars)} movie star relationships")
    return len(movies)


def populate_cinemas(conn):
    """Generate cinemas across cities with multiple halls."""
    print("Generating cinemas...")
    cur = conn.cursor()
    cinemas = []
    cinema_id_counter = 1
    
    for city, state in CITIES_AND_STATES:
        num_cinemas = random.randint(2, 4)
        selected_names = random.sample(CINEMA_NAMES, min(num_cinemas, len(CINEMA_NAMES)))
        
        for cinema_name in selected_names:
            full_name = f"{cinema_name} {city}"
            address = f"{random.randint(1, 500)} {fake.street_name()}, {city}, {state}"
            
            num_halls = random.randint(3, 6)
            selected_halls = random.sample(HALL_CONFIGS, min(num_halls, len(HALL_CONFIGS)))
            
            for hall_name, hall_size, hall_category in selected_halls:
                cinemas.append((
                    cinema_id_counter, full_name, address, city, state,
                    random.randint(1, 1000), hall_name, hall_size, hall_category
                ))
            cinema_id_counter += 1
    
    cur.executemany(
        """INSERT INTO dim_cinema (cinema_id, cinema_name, cinema_address, cinema_city, 
           cinema_state, hall_id, hall_name, hall_size, hall_size_category)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        cinemas
    )
    conn.commit()
    cur.close()
    print(f"  Inserted {len(cinemas)} cinema/hall combinations")
    return len(cinemas)


def populate_transaction_types(conn):
    """Generate online and offline transaction types."""
    print("Generating transaction types...")
    cur = conn.cursor()
    
    # Clear existing
    cur.execute("DELETE FROM dim_transaction_type")
    
    types = []
    # Offline
    types.append(("Offline", None, None))
    
    # Online with different browser/system combos
    for browser in BROWSERS:
        for system in SYSTEMS:
            types.append(("Online", system, browser))
    
    cur.executemany(
        """INSERT INTO dim_transaction_type (transaction_type, system, browser)
           VALUES (%s, %s, %s)""",
        types
    )
    conn.commit()
    cur.close()
    print(f"  Inserted {len(types)} transaction types")
    return len(types)


def populate_promotions(conn):
    """Generate promotions."""
    print("Generating promotions...")
    cur = conn.cursor()
    
    # Clear existing
    cur.execute("DELETE FROM dim_promotion")
    
    promos = []
    # No promotion record
    promos.append((None, "No Promotion", "None", 0.00, None, None, False))
    
    promo_id = 1
    for desc, ptype, discount in PROMOTION_TYPES:
        for year in range(START_YEAR, END_YEAR + 1):
            start = date(year, random.randint(1, 6), 1)
            end = date(year, random.randint(7, 12), 28)
            promos.append((promo_id, f"{desc} {year}", ptype, discount, start, end, True))
            promo_id += 1
    
    cur.executemany(
        """INSERT INTO dim_promotion (promotion_id, promotion_description, promotion_type, 
           discount_percentage, start_date, end_date, has_promotion)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        promos
    )
    conn.commit()
    cur.close()
    print(f"  Inserted {len(promos)} promotions")
    return len(promos)


# ============================================================================
# Populate Fact Table
# ============================================================================

def populate_fact_table(conn):
    """Generate 1,100,000+ fact table rows."""
    print(f"\nGenerating {FACT_TABLE_TARGET:,} fact table rows...")
    print("This will take a few minutes...\n")
    
    cur = conn.cursor()
    
    # Load dimension keys
    cur.execute("SELECT date_key, full_date, year, week_of_year FROM dim_date WHERE year BETWEEN %s AND %s", (START_YEAR, END_YEAR))
    dates = cur.fetchall()
    date_lookup = {row[1]: (row[0], row[2], row[3]) for row in dates}
    date_list = [row[1] for row in dates]
    
    cur.execute("SELECT customer_key, date_of_birth FROM dim_customer")
    customers = cur.fetchall()
    
    cur.execute("SELECT movie_key FROM dim_movie")
    movie_keys = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT cinema_key FROM dim_cinema")
    cinema_keys = [row[0] for row in cur.fetchall()]
    
    cur.execute("SELECT promotion_key, has_promotion FROM dim_promotion")
    promotions = cur.fetchall()
    promo_with = [p[0] for p in promotions if p[1]]
    promo_none = [p[0] for p in promotions if not p[1]][0]
    
    cur.execute("SELECT transaction_type_key, transaction_type FROM dim_transaction_type")
    trans_types = cur.fetchall()
    online_keys = [t[0] for t in trans_types if t[1] == "Online"]
    offline_keys = [t[0] for t in trans_types if t[1] == "Offline"]
    
    cur.execute("SELECT time_of_day_key, time_period FROM dim_time_of_day")
    time_periods = {row[1]: row[0] for row in cur.fetchall()}
    
    transaction_id = 1
    total_inserted = 0
    batch = []
    
    start_time = time.time()
    
    while total_inserted < FACT_TABLE_TARGET:
        # Pick a random transaction date
        trans_date = random.choice(date_list)
        date_key, year, week = date_lookup[trans_date]
        
        # Showing date is same day or up to 7 days earlier
        showing_offset = random.randint(0, 7)
        showing_date = trans_date - timedelta(days=showing_offset)
        if showing_date in date_lookup:
            showing_date_key = date_lookup[showing_date][0]
        else:
            showing_date_key = date_key
        
        # Customer
        cust_key, cust_dob = random.choice(customers)
        customer_age = (trans_date - cust_dob).days // 365
        if customer_age < 0:
            customer_age = abs(customer_age)
        
        # Movie, Cinema
        movie_key = random.choice(movie_keys)
        cinema_key = random.choice(cinema_keys)
        
        # Online (60%) vs Offline (40%)
        if random.random() < 0.6:
            trans_type_key = random.choice(online_keys)
        else:
            trans_type_key = random.choice(offline_keys)
        
        # Promotion (25% chance)
        if random.random() < 0.25:
            promo_key = random.choice(promo_with)
            discount = round(random.uniform(2, 20), 2)
        else:
            promo_key = promo_none
            discount = 0.0
        
        # Time of day
        hour = random.choices(
            [random.randint(6, 11), random.randint(12, 17), random.randint(18, 23)],
            weights=[20, 35, 45],
            k=1
        )[0]
        if hour >= 6 and hour <= 11:
            tod_key = time_periods["Morning"]
        elif hour >= 12 and hour <= 17:
            tod_key = time_periods["Afternoon"]
        else:
            tod_key = time_periods["Night"]
        
        # Tickets per transaction (1 to 6)
        ticket_count = random.choices([1, 2, 3, 4, 5, 6], weights=[25, 35, 20, 10, 7, 3], k=1)[0]
        ticket_price = round(random.uniform(30, 150), 2)
        total_price = round(ticket_price * ticket_count - discount, 2)
        if total_price < 0:
            total_price = ticket_price
        
        batch.append((
            date_key, showing_date_key, cust_key, movie_key, cinema_key,
            promo_key, trans_type_key, tod_key, transaction_id,
            ticket_price, total_price, ticket_count, customer_age, discount
        ))
        
        transaction_id += 1
        total_inserted += 1
        
        # Insert in batches
        if len(batch) >= BATCH_SIZE:
            cur.executemany(
                """INSERT INTO fact_ticket_sales 
                   (date_key, showing_date_key, customer_key, movie_key, cinema_key,
                    promotion_key, transaction_type_key, time_of_day_key, transaction_id,
                    ticket_price, total_transaction_price, ticket_count, customer_age, discount_amount)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                batch
            )
            conn.commit()
            batch = []
            print_progress(total_inserted, FACT_TABLE_TARGET, "Fact table")
    
    # Insert remaining
    if batch:
        cur.executemany(
            """INSERT INTO fact_ticket_sales 
               (date_key, showing_date_key, customer_key, movie_key, cinema_key,
                promotion_key, transaction_type_key, time_of_day_key, transaction_id,
                ticket_price, total_transaction_price, ticket_count, customer_age, discount_amount)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            batch
        )
        conn.commit()
    
    print_progress(total_inserted, FACT_TABLE_TARGET, "Fact table")
    
    elapsed = time.time() - start_time
    cur.close()
    print(f"\n  Inserted {total_inserted:,} fact rows in {elapsed:.1f} seconds")
    return total_inserted


# ============================================================================
# Verification
# ============================================================================

def verify_data(conn):
    """Print verification statistics."""
    print("\n" + "=" * 60)
    print("DATA VERIFICATION")
    print("=" * 60)
    
    cur = conn.cursor()
    
    tables = [
        "dim_date", "dim_time_of_day", "dim_customer", "dim_movie",
        "dim_movie_star", "dim_cinema", "dim_promotion",
        "dim_transaction_type", "dim_age_group", "fact_ticket_sales"
    ]
    
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  {table:<30} {count:>12,} rows")
    
    print("\n--- Fact Table Summary ---")
    cur.execute("""
        SELECT 
            MIN(d.year) AS min_year,
            MAX(d.year) AS max_year,
            COUNT(DISTINCT f.transaction_id) AS transactions,
            SUM(f.total_transaction_price) AS total_sales,
            AVG(f.ticket_price) AS avg_ticket_price
        FROM fact_ticket_sales f
        JOIN dim_date d ON f.date_key = d.date_key
    """)
    row = cur.fetchone()
    print(f"  Year range:       {row[0]} to {row[1]}")
    print(f"  Total transactions: {row[2]:,}")
    print(f"  Total sales:      ${row[3]:,.2f}")
    print(f"  Avg ticket price: ${row[4]:,.2f}")
    
    print("\n--- Sales by Year ---")
    cur.execute("""
        SELECT d.year, COUNT(*) AS rows, SUM(f.total_transaction_price) AS sales
        FROM fact_ticket_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY d.year
        ORDER BY d.year
    """)
    for row in cur.fetchall():
        print(f"  {row[0]}: {row[1]:>10,} rows, ${row[2]:>15,.2f} sales")
    
    print("\n--- Gender Distribution ---")
    cur.execute("""
        SELECT c.gender, COUNT(*) AS cnt
        FROM fact_ticket_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        GROUP BY c.gender
        ORDER BY cnt DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:<10} {row[1]:>10,} transactions")
    
    print("\n--- Cities ---")
    cur.execute("""
        SELECT cin.cinema_city, COUNT(*) AS cnt
        FROM fact_ticket_sales f
        JOIN dim_cinema cin ON f.cinema_key = cin.cinema_key
        GROUP BY cin.cinema_city
        ORDER BY cnt DESC
    """)
    for row in cur.fetchall():
        print(f"  {row[0]:<25} {row[1]:>10,} transactions")
    
    cur.close()
    print("\n" + "=" * 60)


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 60)
    print("Al Sinama Data Warehouse - Synthetic Data Generator")
    print("=" * 60)
    print(f"Target: {FACT_TABLE_TARGET:,} fact table rows")
    print(f"Period: {START_YEAR} to {END_YEAR}")
    print()
    
    try:
        conn = get_connection()
        print("Connected to database successfully!\n")
    except Exception as e:
        print(f"ERROR: Cannot connect to database: {e}")
        print("\nMake sure PostgreSQL is running:")
        print("  cd /Users/alishahrour/Desktop/HBKU/Studies/Advance_DBMS/docker")
        print("  docker-compose up -d")
        print("\nAnd that you have run create_schema_revised.sql first.")
        sys.exit(1)
    
    try:
        # Step 1: Populate dimensions
        print("--- STEP 1: Populating Dimension Tables ---\n")
        populate_customers(conn)
        populate_movies(conn)
        populate_cinemas(conn)
        populate_transaction_types(conn)
        populate_promotions(conn)
        
        # Step 2: Populate fact table
        print("\n--- STEP 2: Populating Fact Table ---")
        populate_fact_table(conn)
        
        # Step 3: Verify
        print("\n--- STEP 3: Verifying Data ---")
        verify_data(conn)
        
        print("\nSynthetic data generation completed successfully!")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
