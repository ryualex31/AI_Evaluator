import sqlite3
import random
from datetime import datetime, timedelta

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db/data.db")

def create_table(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financials (
        id INTEGER PRIMARY KEY,
        date TEXT,
        month TEXT,
        year INTEGER,
        region TEXT,
        country TEXT,
        product TEXT,
        category TEXT,
        revenue REAL,
        cost REAL,
        profit REAL,
        customer_type TEXT
    );
    """)

def generate_data(num_rows=800):
    regions = ["North America", "Europe", "Asia"]
    countries = {
        "North America": ["USA", "Canada"],
        "Europe": ["Germany", "France", "UK"],
        "Asia": ["India", "Singapore", "Japan"]
    }

    products = ["Product A", "Product B", "Product C"]
    categories = {
        "Product A": "Software",
        "Product B": "Hardware",
        "Product C": "Services"
    }

    customer_types = ["Enterprise", "SMB", "Startup"]

    start_date = datetime(2024, 1, 1)

    data = []

    for i in range(1, num_rows + 1):
        date = start_date + timedelta(days=random.randint(0, 365))

        region = random.choice(regions)
        country = random.choice(countries[region])
        product = random.choice(products)

        revenue = random.randint(8000, 25000)
        cost = random.randint(4000, revenue - 1000)
        profit = revenue - cost

        row = (
            i,
            date.strftime("%Y-%m-%d"),
            date.strftime("%B"),
            date.year,
            region,
            country,
            product,
            categories[product],
            revenue,
            cost,
            profit,
            random.choice(customer_types)
        )

        data.append(row)

    return data

def insert_data(cursor, data):
    cursor.executemany("""
        INSERT INTO financials VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

def main():
    print("📦 Creating database and inserting data...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_table(cursor)

    data = generate_data(num_rows=800)
    insert_data(cursor, data)

    conn.commit()
    conn.close()

    print("✅ Database setup complete with 800 rows!")
    print(f"DB is being created at: {DB_PATH}")

if __name__ == "__main__":
    main()
