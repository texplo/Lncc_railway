
import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

BASE_URLS = [
    "https://www.ln-cc.com/en-fi/sale-two/men-s-sale-two/",
    "https://www.ln-cc.com/en-fi/sale-two/women-s-sale/"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_items(url):
    items = []
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    for item in soup.select(".product-tile"):
        try:
            brand = item.select_one(".brand-name").text.strip()
            name = item.select_one(".product-name").text.strip()
            price_tag = item.select_one(".price-sales")
            old_price_tag = item.select_one(".price-standard")
            if price_tag and old_price_tag:
                price = float(price_tag.text.replace("€", "").strip())
                old_price = float(old_price_tag.text.replace("€", "").strip())
                discount = round(100 * (old_price - price) / old_price)
            else:
                price = old_price = discount = None
            code = item.get("data-product-code", "")
            link = item.select_one("a")["href"]
            items.append((code, brand, name, old_price, price, discount, link))
        except Exception as e:
            print("Error parsing item:", e)
    return items

def save_to_db(items):
    conn = sqlite3.connect("database/discounts.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            code TEXT PRIMARY KEY,
            brand TEXT,
            name TEXT,
            original_price REAL,
            current_price REAL,
            discount_percent INTEGER,
            url TEXT,
            last_seen TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT,
            price REAL,
            discount_percent INTEGER,
            date TEXT
        )
    """)

    today = datetime.now().strftime("%Y-%m-%d")

    for item in items:
        code, brand, name, old_price, price, discount, link = item
        cur.execute("SELECT current_price FROM products WHERE code = ?", (code,))
        row = cur.fetchone()
        if row:
            if row[0] != price:
                cur.execute("UPDATE products SET current_price=?, discount_percent=?, last_seen=? WHERE code=?",
                            (price, discount, today, code))
                cur.execute("INSERT INTO price_history (code, price, discount_percent, date) VALUES (?, ?, ?, ?)",
                            (code, price, discount, today))
        else:
            cur.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (code, brand, name, old_price, price, discount, link, today))
            cur.execute("INSERT INTO price_history (code, price, discount_percent, date) VALUES (?, ?, ?, ?)",
                        (code, price, discount, today))

    conn.commit()
    conn.close()

def run():
    all_items = []
    for url in BASE_URLS:
        print(f"Fetching: {url}")
        all_items.extend(fetch_items(url))
    save_to_db(all_items)
    print(f"Saved {len(all_items)} items to database.")

if __name__ == "__main__":
    run()
