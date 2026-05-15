"""
database.py - MongoDB backend for the ShopVerse Tkinter E-Commerce App
Requires: pip install pymongo

By default connects to a local MongoDB instance:
    mongodb://localhost:27017

To use MongoDB Atlas (cloud), replace MONGO_URI with your connection string:
    MONGO_URI = "mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/"
"""

import hashlib
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from bson import ObjectId
import re

# ── Connection config ─────────────────────────────────────────────────────────
MONGO_URI = "mongodb://localhost:27017/"   # ← change to Atlas URI if needed
DB_NAME   = "shopverse"

_client = None
_db     = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        _db = _client[DB_NAME]
    return _db


def _oid(val):
    if isinstance(val, ObjectId):
        return val
    try:
        return ObjectId(str(val))
    except Exception:
        return val


def _clean(doc: dict) -> dict:
    if doc is None:
        return None
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.strftime("%Y-%m-%d %H:%M:%S")
        else:
            out[k] = v
    if "_id" in out and "id" not in out:
        out["id"] = out["_id"]
    return out


def _next_id(collection_name: str) -> int:
    db = get_db()
    result = db.counters.find_one_and_update(
        {"_id": collection_name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return result["seq"]


def init_db():
    db = get_db()

    db.users.create_index("username", unique=True)
    db.users.create_index("email",    unique=True)
    db.products.create_index("id",    unique=True)
    db.categories.create_index("id",  unique=True)
    db.categories.create_index("name", unique=True)
    db.orders.create_index("id",      unique=True)
    db.cart.create_index([("user_id", ASCENDING), ("product_id", ASCENDING)], unique=True)
    db.wishlist.create_index([("user_id", ASCENDING), ("product_id", ASCENDING)], unique=True)
    db.comments.create_index([("product_id", ASCENDING), ("created_at", DESCENDING)])

    if db.categories.count_documents({}) == 0:
        cats = [
            ("Electronics", "⚡"), ("Clothing", "👕"), ("Books", "📚"),
            ("Home & Garden","🏡"), ("Sports","⚽"), ("Beauty","💄"),
            ("Toys","🧸"), ("Food","🍕"),
        ]
        for name, icon in cats:
            db.categories.insert_one({"id": _next_id("categories"), "name": name, "icon": icon})

    cat_map = {c["name"]: c["id"] for c in db.categories.find()}

    if db.users.count_documents({"username": "admin"}) == 0:
        db.users.insert_one({
            "username": "admin", "password": hash_password("admin123"),
            "email": "admin@shop.com", "full_name": "Admin User",
            "role": "admin", "created_at": datetime.now(),
        })

    if db.products.count_documents({}) == 0:
        raw = [
            ("Wireless Headphones","Premium noise-cancelling over-ear headphones with 30h battery",89.99,50,"Electronics","🎧",4.7, "images/headphones.webp"),
            ("Smart Watch","Fitness tracker with heart rate monitor and GPS",199.99,30,"Electronics","⌚",4.5, "images/watch.webp"),
            ("Laptop Stand","Adjustable aluminum laptop stand for ergonomic working",39.99,100,"Home & Garden","💻",4.6, "images/stand.webp"),
            ("Mechanical Keyboard","RGB backlit mechanical keyboard with Cherry MX switches",129.99,25,"Electronics","⌨️",4.8, "images/keyboard.webp"),
            ("Running Shoes","Lightweight breathable mesh running shoes, all sizes",74.99,80,"Clothing","👟",4.4, "images/shoes.webp"),
            ("Yoga Mat","Non-slip eco-friendly yoga and exercise mat 6mm thick",29.99,120,"Sports","🧘",4.6, "images/yogamat.webp"),
            ("Python Cookbook","Expert recipes for writing clean, efficient Python code",44.99,60,"Books","📘",4.9, "images/pythoncook.webp"),
            ("Coffee Maker","12-cup programmable drip coffee maker with thermal carafe",59.99,40,"Home & Garden","☕",4.3, "images/coffeemaker.webp"),
            ("Skincare Set","5-piece hydrating skincare routine set with SPF moisturizer",49.99,70,"Beauty","🧴",4.5, "images/skincare.webp"),
            ("LEGO City Set","800-piece LEGO city skyline building set for ages 12+",79.99,35,"Toys","🧱",4.8, "images/lego.webp"),
            ("Bluetooth Speaker","Waterproof portable speaker with 360 surround sound",54.99,90,"Electronics","🔊",4.6, "images/speaker.webp"),
            ("Denim Jacket","Classic slim-fit denim jacket, multiple washes available",64.99,45,"Clothing","🧥",4.3, "images/denim.webp"),
            ("Air Fryer","5.5L digital air fryer with 8 preset cooking programs",89.99,55,"Home & Garden","🍟",4.7, "images/airfryer.webp"),
            ("Resistance Bands","Set of 5 latex resistance bands for strength training",19.99,150,"Sports","💪",4.5, "images/resbands.webp"),
            ("Dark Chocolate Box","Assorted premium dark chocolates from Belgium, 500g",24.99,200,"Food","🍫",4.9, "images/chocolate.webp"),
            ("Sunglasses","UV400 polarized aviator sunglasses with metal frame",34.99,60,"Clothing","🕶️",4.2, "images/sunglasses.webp"),
            ("Desk Lamp","LED desk lamp with wireless charging pad and USB port",49.99,75,"Home & Garden","💡",4.6, "images/lamp.webp"),
            ("Protein Powder","Whey protein isolate, chocolate flavor, 2kg tub",54.99,40,"Sports","🥤",4.4, "images/protein.webp"),
        ]
        for name, desc, price, stock, cat_name, emoji, rating, image_url in raw:
            db.products.insert_one({
                "id": _next_id("products"), "name": name, "description": desc,
                "price": price, "stock": stock, "category_id": cat_map.get(cat_name),
                "image_emoji": emoji, "image_url": image_url, "rating": rating, "created_at": datetime.now(),
            })

    print("[ShopVerse] MongoDB connected and ready")


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def register_user(username, password, email, full_name):
    try:
        get_db().users.insert_one({
            "username": username, "password": hash_password(password),
            "email": email, "full_name": full_name,
            "role": "customer", "created_at": datetime.now(),
        })
        return True, "Account created successfully!"
    except DuplicateKeyError:
        return False, "Username or email already exists."


def login_user(username, password):
    doc = get_db().users.find_one({"username": username, "password": hash_password(password)})
    return _clean(doc) if doc else None


def get_products(search="", category_id=None):
    db = get_db()
    query = {}
    if search:
        pattern = re.compile(search, re.IGNORECASE)
        query["$or"] = [{"name": pattern}, {"description": pattern}]
    if category_id is not None:
        query["category_id"] = category_id

    cat_map = {c["id"]: c for c in db.categories.find()}
    results = []
    for p in db.products.find(query).sort("id", ASCENDING):
        doc = _clean(p)
        cat = cat_map.get(doc.get("category_id"))
        doc["category_name"] = cat["name"] if cat else ""
        doc["category_icon"] = cat["icon"] if cat else "📦"
        results.append(doc)
    return results


def get_product(product_id):
    db = get_db()
    p = db.products.find_one({"id": int(product_id)})
    if not p:
        return None
    doc = _clean(p)
    cat = db.categories.find_one({"id": doc.get("category_id")})
    doc["category_name"] = cat["name"] if cat else ""
    doc["category_icon"] = cat["icon"] if cat else "📦"
    return doc


def get_categories():
    return [_clean(c) for c in get_db().categories.find().sort("name", ASCENDING)]


def add_to_cart(user_id, product_id, quantity=1):
    get_db().cart.update_one(
        {"user_id": str(user_id), "product_id": int(product_id)},
        {"$inc": {"quantity": quantity}},
        upsert=True,
    )


def get_cart(user_id):
    db = get_db()
    items = []
    for c in db.cart.find({"user_id": str(user_id)}):
        p = db.products.find_one({"id": c["product_id"]})
        if not p:
            continue
        items.append({
            "id": str(c["_id"]), "quantity": c["quantity"],
            "product_id": p["id"], "name": p["name"],
            "price": p["price"], "image_emoji": p["image_emoji"], "stock": p["stock"],
        })
    return items


def update_cart_qty(cart_id, quantity):
    db = get_db()
    if quantity <= 0:
        db.cart.delete_one({"_id": _oid(cart_id)})
    else:
        db.cart.update_one({"_id": _oid(cart_id)}, {"$set": {"quantity": quantity}})


def remove_from_cart(cart_id):
    get_db().cart.delete_one({"_id": _oid(cart_id)})


def clear_cart(user_id):
    get_db().cart.delete_many({"user_id": str(user_id)})


def get_cart_count(user_id):
    return sum(c.get("quantity", 0) for c in get_db().cart.find({"user_id": str(user_id)}))


def place_order(user_id, address):
    cart = get_cart(user_id)
    if not cart:
        return None
    total    = sum(i["price"] * i["quantity"] for i in cart)
    order_id = _next_id("orders")
    db       = get_db()

    items_docs = []
    for item in cart:
        items_docs.append({
            "product_id": item["product_id"], "quantity": item["quantity"],
            "price": item["price"], "name": item["name"], "image_emoji": item["image_emoji"],
        })
        db.products.update_one({"id": item["product_id"]}, {"$inc": {"stock": -item["quantity"]}})
        db.products.update_one({"id": item["product_id"], "stock": {"$lt": 0}}, {"$set": {"stock": 0}})

    db.orders.insert_one({
        "id": order_id, "user_id": str(user_id), "total": total,
        "status": "pending", "address": address,
        "items": items_docs, "created_at": datetime.now(),
    })
    clear_cart(user_id)
    return order_id


def get_orders(user_id):
    return [_clean(o) for o in get_db().orders.find({"user_id": str(user_id)}).sort("created_at", DESCENDING)]


def get_order_items(order_id):
    order = get_db().orders.find_one({"id": int(order_id)})
    return order.get("items", []) if order else []


def toggle_wishlist(user_id, product_id):
    db  = get_db()
    key = {"user_id": str(user_id), "product_id": int(product_id)}
    if db.wishlist.find_one(key):
        db.wishlist.delete_one(key)
        return False
    db.wishlist.insert_one(key)
    return True


def get_wishlist(user_id):
    db      = get_db()
    cat_map = {c["id"]: c for c in db.categories.find()}
    items   = []
    for w in db.wishlist.find({"user_id": str(user_id)}):
        p = db.products.find_one({"id": w["product_id"]})
        if not p:
            continue
        doc = _clean(p)
        cat = cat_map.get(doc.get("category_id"))
        doc["category_name"] = cat["name"] if cat else ""
        items.append(doc)
    return items


def is_wishlisted(user_id, product_id):
    return get_db().wishlist.find_one({"user_id": str(user_id), "product_id": int(product_id)}) is not None


def admin_add_product(name, description, price, stock, category_id, emoji):
    pid = _next_id("products")
    get_db().products.insert_one({
        "id": pid, "name": name, "description": description,
        "price": float(price), "stock": int(stock),
        "category_id": category_id, "image_emoji": emoji,
        "image_url": "", "rating": 4.0, "created_at": datetime.now(),
    })


def admin_update_product(product_id, name, description, price, stock, category_id, emoji):
    get_db().products.update_one(
        {"id": int(product_id)},
        {"$set": {"name": name, "description": description, "price": float(price),
                  "stock": int(stock), "category_id": category_id, "image_emoji": emoji}},
    )


def admin_delete_product(product_id):
    get_db().products.delete_one({"id": int(product_id)})


def admin_get_all_orders():
    db = get_db()
    results = []
    for o in db.orders.find().sort("created_at", DESCENDING):
        doc  = _clean(o)
        user = db.users.find_one({"_id": _oid(doc["user_id"])}) if ObjectId.is_valid(str(doc["user_id"])) else None
        doc["username"] = user["username"] if user else doc.get("user_id", "unknown")
        results.append(doc)
    return results


def admin_update_order_status(order_id, status):
    get_db().orders.update_one({"id": int(order_id)}, {"$set": {"status": status}})


# ── Comments ──────────────────────────────────────────────────────────────────

def init_comments_index():
    """Call once during init_db to ensure the comments index exists."""
    db = get_db()
    db.comments.create_index([("product_id", ASCENDING), ("created_at", DESCENDING)])


def add_comment(user_id, product_id, text, rating=None):
    """Add a comment (and optional 1-5 star rating) to a product."""
    doc = {
        "user_id":    str(user_id),
        "product_id": int(product_id),
        "text":       text.strip(),
        "created_at": datetime.now(),
    }
    if rating is not None:
        doc["rating"] = max(1, min(5, int(rating)))
    get_db().comments.insert_one(doc)


def get_comments(product_id):
    """Return all comments for a product, newest first."""
    db = get_db()
    results = []
    for c in db.comments.find({"product_id": int(product_id)}).sort("created_at", DESCENDING):
        doc = _clean(c)
        user = db.users.find_one({"_id": _oid(doc["user_id"])}) if ObjectId.is_valid(str(doc["user_id"])) else None
        doc["username"]  = user["username"]  if user else "unknown"
        doc["full_name"] = user["full_name"] if user else "Unknown User"
        results.append(doc)
    return results


def delete_comment(comment_id):
    """Delete a comment by its _id string."""
    get_db().comments.delete_one({"_id": _oid(comment_id)})


def admin_get_stats():
    db  = get_db()
    rev = list(db.orders.aggregate([
        {"$match": {"status": {"$ne": "cancelled"}}},
        {"$group": {"_id": None, "total": {"$sum": "$total"}}},
    ]))
    return {
        "revenue":  rev[0]["total"] if rev else 0.0,
        "orders":   db.orders.count_documents({}),
        "users":    db.users.count_documents({"role": "customer"}),
        "products": db.products.count_documents({}),
    }