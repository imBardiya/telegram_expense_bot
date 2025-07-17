from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from handlers import router
from notes import API_TOKEN as ApiTk
from scheduler import setup_scheduler

BOT_TOKEN = ApiTk

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)


async def main():
    print('start')
    await bot.set_my_commands([
        BotCommand(command="start", description="شروع"),
    ])
    setup_scheduler(bot)
    print('ربات راه اندازی شد')
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())