import asyncio
import os
from dotenv import load_dotenv
from Commands import commands
from Handlers import Callback_handlers, Callback_new, Callback_watch
import req.Push as Push
import db.db as db

from aiogram import Bot, Dispatcher

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
accesskey = os.getenv("accesskey")
bot = Bot(token = API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

            
async def main():
    dp.include_routers(
        commands.router,
        Callback_handlers.router,
        Callback_new.router,
        Callback_watch.router,
        Push.router
    )
    db.new_sql()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())