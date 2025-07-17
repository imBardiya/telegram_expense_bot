from apscheduler.schedulers.asyncio import AsyncIOScheduler
from reports import generate_weekly_report
from database import get_all_telegram_ids
from aiogram import Bot


def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()

    async def send_weekly_reports():
        users = get_all_telegram_ids()
        for user_id in users:
            try:
                report = generate_weekly_report(user_id)
                await bot.send_message(user_id, report)
            except Exception as e:
                print(f"❌ خطا در ارسال گزارش برای کاربر {user_id}: {e}")

    scheduler.add_job(send_weekly_reports, "cron", day_of_week="sun", hour=8)
    scheduler.start()