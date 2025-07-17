import pandas as pd
import sqlite3
from aiogram.types import Message
from aiogram import Bot

# اتصال به دیتابیس
conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()

def get_user_transactions(user_id: int):
    c.execute("""
        SELECT id, type, amount, period, category, description
        FROM transactions
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))
    rows = c.fetchall()
    return rows


async def export_transactions_csv(user_id: int, message: Message, bot: Bot):
    rows = get_user_transactions(user_id)
    if not rows:
        await message.answer("📭 هنوز تراکنشی ثبت نکردی که بشه فایل ساخت.")
        return

    df = pd.DataFrame(rows, columns=["ID", "نوع", "مبلغ", "دوره", "دسته‌بندی", "توضیح"])

    filepath = f"transactions_{user_id}.csv"
    df.to_csv(filepath, index=False, encoding="utf-8-sig")  # با پشتیبانی از فارسی

    with open(filepath, "rb") as file:
        await bot.send_document(chat_id=message.chat.id, document=file, caption="📤 خروجی تراکنش‌ها (CSV)")