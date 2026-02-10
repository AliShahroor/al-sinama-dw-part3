# Al-Sinema DW — Midterm Project (Part 3)

content available:
- `create_schema_revised.sql` — revised star schema
- `generate_data.py` — synthetic data generator (1.1M rows)
- `queries.sql` — SQL for Q11–Q18
- `answer_queries.py` — runs queries and exports CSVs

Quick start
1. Create and activate a virtual environment:

   python -m venv venv
   source venv/bin/activate

2. Install minimal dependencies:

   pip install psycopg2-binary faker numpy

3. Generate data (expects a PostgreSQL database running):

   python generate_data.py

4. Run the queries and export results:

   python answer_queries.py

# Midterm Project Part 3: Advanced Queries and Synthetic Data

**Author**: Ali Shahroor - 210034060  
**Course**: Advanced Data Management Systems  

## Overview

This folder contains Part 3 of the Midterm Project. It includes a revised data warehouse schema, a synthetic data generator that populates over 1.1 million fact table rows, and eight analytical SQL queries (Q11 through Q18) covering ranking, top N analysis, and moving averages.

## Files

| File | Description |
|------|-------------|
| `create_schema_revised.sql` | Revised star schema DDL (adds `cinema_city` to dim_cinema) |
| `generate_data.py` | Python script to generate synthetic data for all tables |
| `queries.sql` | All 8 SQL queries (Q11 through Q18) |
| `answer_queries.py` | Python script that runs all queries and exports results to CSV |
| `report.tex` | LaTeX report for Overleaf |
| `README.md` | This file |
