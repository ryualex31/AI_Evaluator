import sqlite3
import random
from datetime import datetime, timedelta
import os

# ---------------- DB PATH ---------------- #
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "data.db")

os.makedirs(DB_DIR, exist_ok=True)

# ---------------- TABLE ---------------- #
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
        customer_type TEXT,
        supplier TEXT,
        units_sold INTEGER,
        discount REAL,
        revenue REAL,
        cost REAL,
        profit REAL,
        profit_margin REAL
    );
    """)

# ---------------- MASTER DATA ---------------- #
regions = ["North America", "Europe", "Asia-Pacific"]

countries = {
    "North America": ["USA", "Canada"],
    "Europe": ["Germany", "France", "UK"],
    "Asia-Pacific": ["India", "Singapore", "Australia"]
}

products = [
    "Cloud Infrastructure",
    "AI Analytics Platform",
    "Cybersecurity Suite",
    "ERP System",
    "CRM Software"
]

categories = {
    "Cloud Infrastructure": "Cloud",
    "AI Analytics Platform": "AI",
    "Cybersecurity Suite": "Security",
    "ERP System": "Enterprise Software",
    "CRM Software": "SaaS"
}

customer_types = ["Enterprise", "Mid-Market", "SMB"]

suppliers = [
    "AWS",
    "Microsoft Azure",
    "Google Cloud",
    "Snowflake",
    "Databricks"
]

# ---------------- FACTORS ---------------- #
region_factor = {
    "North America": 1.2,
    "Europe": 1.0,
    "Asia-Pacific": 1.3
}

product_factor = {
    "Cloud Infrastructure": 1.3,
    "AI Analytics Platform": 1.25,
    "Cybersecurity Suite": 1.1,
    "ERP System": 1.0,
    "CRM Software": 0.9
}

customer_factor = {
    "Enterprise": 1.5,
    "Mid-Market": 1.1,
    "SMB": 0.8
}

supplier_cost_factor = {
    "AWS": 1.2,
    "Microsoft Azure": 1.1,
    "Google Cloud": 1.15,
    "Snowflake": 1.25,
    "Databricks": 1.2
}

# ---------------- DATA GENERATION ---------------- #
def generate_data():
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    delta = end_date - start_date

    data = []
    id_counter = 1

    for i in range(delta.days):

        date = start_date + timedelta(days=i)

        # 📈 Growth trend
        month_factor = 1 + (date.month / 12)

        # 🎯 Seasonality (Q4 boost)
        seasonality = 1.2 if date.month in [10, 11, 12] else 1.0

        for region in regions:
            for product in products:
                for customer_type in customer_types:

                    country = random.choice(countries[region])
                    supplier = random.choice(suppliers)

                    base = 10000

                    revenue = int(
                        base *
                        month_factor *
                        seasonality *
                        region_factor[region] *
                        product_factor[product] *
                        customer_factor[customer_type] *
                        random.uniform(0.9, 1.1)
                    )

                    # 💰 Discount (0–20%)
                    discount = round(random.uniform(0.0, 0.2), 2)

                    # Apply discount
                    revenue_after_discount = int(revenue * (1 - discount))

                    # 📦 Units sold
                    units_sold = int(revenue_after_discount / random.randint(200, 800))

                    # 💸 Cost influenced by supplier
                    cost_ratio = random.uniform(0.55, 0.75)
                    cost = int(
                        revenue_after_discount *
                        cost_ratio *
                        supplier_cost_factor[supplier]
                    )

                    profit = revenue_after_discount - cost

                    # 📊 Profit margin
                    profit_margin = round((profit / revenue_after_discount) * 100, 2) if revenue_after_discount else 0

                    row = (
                        id_counter,
                        date.strftime("%Y-%m-%d"),
                        date.strftime("%B"),
                        date.year,
                        region,
                        country,
                        product,
                        categories[product],
                        customer_type,
                        supplier,
                        units_sold,
                        discount,
                        revenue_after_discount,
                        cost,
                        profit,
                        profit_margin
                    )

                    data.append(row)
                    id_counter += 1

    return data

# ---------------- INSERT ---------------- #
def insert_data(cursor, data):
    cursor.executemany("""
        INSERT INTO financials VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

# ---------------- MAIN ---------------- #
def main():
    print("📦 Generating realistic financial dataset...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_table(cursor)

    data = generate_data()
    insert_data(cursor, data)

    conn.commit()
    conn.close()

    print(f"✅ Done! Inserted {len(data)} rows into financials table.")

if __name__ == "__main__":
    main()