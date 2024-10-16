import asyncio
from aiogram import Router, types, Bot
from aiogram.filters import Command
import KeyBord.Keybord as Keybord
import req.req as req
import db.db as db

router = Router()
push_called = False


@router.message(Command("start"))
async def start(message: types.Message):
    global push_called
    login = message.from_user.username
    chat = message.chat.id
    user = message.from_user.first_name
    send_message = (
    f'''🤖Привет, {user}!\n'''
    '''Этот бот для общения с поддержкой 🔥 SPRT-service 🔥\n\n'''
    '''ℹ️ Бот отвечает только тому, кто начал диалог через кнопки. Если бот молчит — что-то пошло не так.\n'''
    '''Чтобы перезапустить, нажмите /start@tp_sprt_bot.\n\n'''
    '''🏠 Для начала выберите пункт из главного меню ⤵️'''
)

    if not push_called:
        asyncio.create_task(req.loop_push())
        push_called = True
    new_user = await db.find_new_user(login)
    
    
    if new_user == True:  # Проверяем, новый ли пользователь
        if message.chat.type == "group" or "supergroup":
            await message.answer(f"Сначала авторизуйтесь через личные сообщения https://t.me/tp_sprt_bot")
        else:
            write_user = await db.find_telegram(login, chat)
            if write_user == False:
                send_message = (
                    '''🤔 К сожалению мы не смогли найти связанной учётной записи.\n\n'''
                    '''Вы можете подать обращение не связанное с компанией, сотрудники 💪  рассмотрят его в общем порядке.\n\n'''
                    '''ℹ️ Если вы связаны с каким либо клиентом SPRT - обязательно укажите это в описании заявки, мы добавим вас в нужную организацию.\n\n''')
                await message.answer(send_message, reply_markup=Keybord.contact_kb)
    else:
        auth = await db.auth(login)
        if auth == 0:
            key = await db.key(login)
            if key == 0:
                await message.answer(send_message, reply_markup=Keybord.main_kb_key)
            else:
                await message.answer(send_message, reply_markup=Keybord.main_kb)
        else:
            await message.answer(send_message, reply_markup=Keybord.main_kb_unauth)



@router.message(Command("refresh"))
async def start(message: types.Message):
    if message.chat.type == "group":
        await message.answer(f"Это команда работает только в личных сообщениях с ботом")
    else:
        number = await message.answer("Поделитесь контактом для обновления данных", reply_markup=Keybord.refresh_contact_kb)

