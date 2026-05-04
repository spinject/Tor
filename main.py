import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- DATABASE ----------
def load_db():
    with open("database.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("database.json", "w") as f:
        json.dump(data, f, indent=4)

# ---------- START ----------
@dp.message(Command("start"))
async def start(message: types.Message):
    db = load_db()
    uid = str(message.from_user.id)

    if uid not in db["users"]:
        db["users"][uid] = {"balance": 0}

    save_db(db)

    await message.answer(
        "🛍 Welcome to Shop Bot\n\n"
        "Commands:\n"
        "/shop - view products\n"
        "/buy <id> - buy product"
    )

# ---------- SHOP ----------
@dp.message(Command("shop"))
async def shop(message: types.Message):
    db = load_db()

    if not db["products"]:
        return await message.answer("❌ No products available")

    text = "🛒 PRODUCTS:\n\n"
    for pid, p in db["products"].items():
        text += f"{pid}. {p['name']} - {p['price']}৳\n"

    await message.answer(text)

# ---------- BUY ----------
@dp.message(Command("buy"))
async def buy(message: types.Message):
    db = load_db()
    uid = str(message.from_user.id)

    parts = message.text.split()

    if len(parts) < 2:
        return await message.answer("Usage: /buy <product_id>")

    pid = parts[1]

    if pid not in db["products"]:
        return await message.answer("❌ Invalid product ID")

    product = db["products"][pid]

    order_id = str(len(db["orders"]) + 1)

    db["orders"][order_id] = {
        "user": uid,
        "product": product["name"],
        "price": product["price"],
        "status": "pending"
    }

    save_db(db)

    await message.answer(
        f"✅ Order Created\n\n"
        f"Product: {product['name']}\n"
        f"Price: {product['price']}৳\n\n"
        "💳 Pay via bKash / Nagad / Rocket (manual)"
    )

# ---------- ADMIN ADD PRODUCT ----------
@dp.message(Command("add"))
async def add_product(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ You are not admin")

    try:
        _, name, price = message.text.split("|")
    except:
        return await message.answer("Format:\n/add|name|price")

    db = load_db()
    pid = str(len(db["products"]) + 1)

    db["products"][pid] = {
        "name": name,
        "price": price
    }

    save_db(db)

    await message.answer("✅ Product added successfully")

# ---------- MAIN ----------
async def main():
    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
