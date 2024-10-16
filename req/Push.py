import asyncio
import time
import os
import shutil

from aiogram import Router, Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bs4 import BeautifulSoup

import html
import config
import req.req as req
import db.db as db



API_TOKEN = config.API_TOKEN
bot = Bot(token = API_TOKEN, parse_mode="HTML")
clear = False


router = Router()
async def send_push(result_text):
    await asyncio.sleep(5)
    await clear_comments()
    telegram_info = await db.take_telegram()
    for username, chat_id in telegram_info:
        for item in result_text:
            number = item.get("number")
            state = item.get("state")
            employe =item.get("UUID")
            if state == "resolved":
                last_comment = item.get("resultDescr")
                last_comment = await remove_html_tags(last_comment) 
                last_comment = html.escape(last_comment) 
                message_text = f"🚩🚩🚩 Ваша заявка  {number} , была закрыта. Решение: 🚩🚩🚩\n🗒️ {last_comment}"
                revive_button = InlineKeyboardButton(text="Возобновить заявку", callback_data=f"revive_{employe}")
                mark_buttons_row1 = [InlineKeyboardButton(text=str(i), callback_data=f"mark_{employe}_{i}") for i in range(1, 6)]

                revive_kb = InlineKeyboardMarkup(inline_keyboard=[
                    [revive_button],
                    mark_buttons_row1])
                revive = revive_kb
            else:
                last_comment = item.get("lastComment")
                last_comment = await remove_html_tags(last_comment) 
                last_comment = html.escape(last_comment) 
                message_text = f"🚩🚩🚩В заявке  {number} новый комментарий 🚩🚩🚩 \n🗒️ {last_comment}"
                revive = None
            client = item.get("client")
            if client is not None:
                uuid = client.get("UUID")
                user_username = await req.find_telegram(uuid)
                if user_username:
                    user_username = user_username[0]['telegram']
                sent_message = await db.take_message(message_text)
                if username == user_username and sent_message != "1":
                    try:
                        await db.write_message(message_text)
                        await bot.send_message(chat_id=chat_id, text=message_text, reply_markup=revive)
                    except Exception as e:
                        print(f"Ошибка при отправке сообщения: {e}")
            else:
                task_id = item.get('UUID')
                current_chat_id = db.find_task(task_id)
                if current_chat_id:
                    sent_message = await db.take_message(message_text)
                    if sent_message != "1":
                        try:
                            await db.write_message(message_text)
                            await bot.send_message(chat_id=current_chat_id, text=message_text, reply_markup=revive)
                        except Exception as e:
                            print(f"Ошибка при отправке сообщения: {e}")


async def remove_html_tags(text):
    if text is None:
        return ""
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()


# Асинхронная функция для очистки папки template
async def clear_template_folder():
    folder_path = "template"  # Путь к папке template
    if os.path.exists(folder_path):  # Проверяем существует ли папка
        shutil.rmtree(folder_path)  # Рекурсивно удаляем содержимое папки
        os.makedirs(folder_path)  # Создаем пустую папку template
    else:
        os.makedirs(folder_path)  # Если папка не существует, просто создаем пустую папку template

# Асинхронная функция для очистки комментариев
async def clear_comments():
    global clear
    if clear == False:
        current_time = time.localtime()
        if current_time.tm_hour == 12 and current_time.tm_min == 00:
            await db.clear_table()
            await clear_template_folder()  # Вызываем функцию для очистки папки template
            clear = True
    elif clear == True:
        current_time = time.localtime()
        if current_time.tm_hour == 12 and current_time.tm_min == 0:
            clear = False
