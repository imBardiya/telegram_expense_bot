import sqlite3

# اتصال مستقیم یا ایمپورت از فایل database.py
conn = sqlite3.connect("finance.db", check_same_thread=False)
c = conn.cursor()


def generate_weekly_report(user_id: int) -> str:
    c.execute("""
        SELECT type, amount, period FROM transactions WHERE user_id = ?
    """, (user_id,))
    txns = c.fetchall()

    income = 0
    expense = 0

    # ضریب تبدیل به هفته
    factor_map = {
        "روزانه": 1 / 7,
        "هفتگی": 1,
        "ماهانه": 1 / 4
    }

    for t_type, amount, period in txns:
        factor = factor_map.get(period, 0)
        norm_amount = amount * factor
        if t_type == "income":
            income += norm_amount
        elif t_type == "expense":
            expense += norm_amount

    balance = income - expense

    return (
        f"📊 گزارش هفتگی خودکار:\n"
        f"➕ درآمد: {income:.0f} تومان\n"
        f"➖ هزینه: {expense:.0f} تومان\n"
        f"💰 مانده: {balance:.0f} تومان"
    )