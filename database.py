import json
import os

DB_FILE = "orders.json"

def load_orders():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_orders(orders):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(orders, f, ensure_ascii=False, indent=2)

def add_order(order_id: str, data: dict):
    orders = load_orders()
    orders[order_id] = data
    save_orders(orders)

def get_order(order_id: str):
    orders = load_orders()
    return orders.get(order_id)

def update_order(order_id: str, key: str, value):
    orders = load_orders()
    if order_id in orders:
        orders[order_id][key] = value
        save_orders(orders)

def get_all_orders():
    return load_orders()
