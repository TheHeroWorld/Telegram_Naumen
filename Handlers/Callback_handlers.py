from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
import KeyBord.Keybord as Keybord 
import db.db as db 
import req.req as req 


sent = False

router = Router()


@router.callback_query(F.data == "cancel")
async def cancel(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    message_send = """❌ Действие отменено\n
🏠 Выберите пункт из главного меню ⤵️"""
    await bot.send_message(callback.message.chat.id,(message_send), reply_markup=Keybord.main_kb)
    await state.clear()
    
    
    
@router.message(F.contact)
async def handler_contact(message: types.Message, bot: Bot):
    test = message.reply_to_message.text
    user_contact = message.contact.phone_number.replace("+", "")
    if test.startswith("🤔 К сожалению мы не смогли найти связанной учётной записи."):
        await req.handle_user(message, user_contact=user_contact)
        await bot.send_message(message.chat.id, "Спасибо за авторизацию", reply_markup=Keybord.main_kb)
    else:
        login = message.from_user.username
        chat = message.chat.id
        await bot.send_message(message.chat.id, "Данные обновлены, нажмите сюда /start")
        refresh = await db.refresh(login, chat, user_contact)

    
@router.callback_query(F.data.contains("revive"))
async def revive(callback: types.CallbackQuery, bot: Bot):
    uuid = callback.data.split('_')[1]
    await req.revive(uuid)
    await bot.send_message(callback.message.chat.id,("зяавка возобновлена "), reply_markup=Keybord.main_kb)
    
    
@router.callback_query(F.data.contains("mark"))
async def mark(callback: types.CallbackQuery, bot: Bot):
    uuid = callback.data.split('_')[1]
    mark = callback.data.split('_')[2]
    await req.mark(uuid, mark)
    await bot.send_message(callback.message.chat.id,("Спасибо за оценку🙏"), reply_markup=Keybord.main_kb)
    
    
@router.message(F.state == None)
async def Handle_comment(message: types.Message, bot: Bot):
    login = message.from_user.username
    auth = await db.auth(login)
    if auth == "1":
        await bot.send_message(message.chat.id, "Выберите что требуется сделать", reply_markup=Keybord.main_kb)
    else:
        await bot.send_message(message.chat.id, "Выберите что требуется сделать", reply_markup=Keybord.main_kb_unauth)

        
        
        


