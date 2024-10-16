import base64  # Модуль для кодирования и декодирования данных в формате Base64
import uuid  # Модуль для генерации уникальных идентификаторов UUID

from aiogram import Router, types, F, Bot # Модуль для работы с Telegram API
from aiogram.fsm.context import FSMContext  # Контекст конечного автомата для управления состояниями

import KeyBord.Keybord as Keybord  # Клавиатура 
import db.db as db  # База данных
import req.req as req  # rest запросы
from utils.states import new_service  # Машина состояний 

sent = False

router = Router()

@router.callback_query(F.data == "New")
async def New_service(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    login = callback.from_user.username
    send_message = (
    f'''📋@{login}, Выберите из списка торговое предприятие , по которому хотите создать заявку.\n\n'''
    f'''ℹ️ Если у вас нет нужного торгового предприятия мы все равно примем ваше обращение, но не забудьте указать его в описании проблемы.''')
    user_uuid = await db.take_userUUID(login)
    if user_uuid != "0":
        ou_uid = await db.take_OUUID(user_uuid)
        office_response = await req.office_request(ou_uid)
        office_data_list = [] 
        for company in office_response["childOUs"]:
            comment_message = company["title"]
            ofiiceuuid = company["UUID"]
            office_data_list.append({"comment_message": comment_message, "ofiiceuuid": ofiiceuuid})
        keyboard = await Keybord.chose_board(office_data_list)
        await bot.send_message(callback.message.chat.id, (send_message), reply_markup=keyboard)
        await state.update_data(office=office_data_list, user_uuid=user_uuid, ou_uid=ou_uid)
    else:
        await bot.send_message(callback.message.chat.id, (send_message), reply_markup=Keybord.unauth_kb)
        ou_uid = "0"
        office_data_list = "0"
        await state.update_data(office=office_data_list, user_uuid=user_uuid, ou_uid=ou_uid)
    await state.set_state(new_service.add_short)

        
        
@router.callback_query(new_service.add_short, F.data.contains("Chose"))
async def add_short(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    login = callback.from_user.username
    message_send = f"📝@{login}, Для начала кратко напишите суть проблемы, я запомню это как тему заявки"
    uuid = callback.data.split('_')[1]
    await state.set_state(new_service.add_descr)
    await state.update_data(office=uuid)
    await bot.send_message(callback.message.chat.id,(message_send), reply_markup=Keybord.cancel_kb)
    
    
@router.message(new_service.add_descr)
async def add_descr(message: types.Message, bot: Bot, state:FSMContext):
    login = message.from_user.username
    send_message = (
    f'''📖@{login}, Теперь напишите полную информацию по вашей заявке. Пожалуйста, отнеситесь серьезно к описанию. Чем подробнее будет описание — тем быстрее специалисты вам помогут.\n\n'''
    f'''ℹ️ Можно использовать любой контент (фото, голосовые сообщения, видео) 📝''')

    await state.update_data(short=message.text)
    await state.set_state(new_service.add_critical)
    await bot.send_message(message.chat.id,(send_message), reply_markup=Keybord.cancel_kb)

@router.message(new_service.add_critical)
async def add_critical(message: types.Message, bot: Bot, state: FSMContext):
    global sent
    login = message.from_user.username
    send_message = (
        f'''📩@{login}, Почти все готово, осталось выбрать тип заявки.\n\n'''
        f'''ℹ️ SLA по типам заявок:\n'''
        f'''Остановка продаж — круглосуточно без выходных\n'''
        f'''Прочее — ежедневно, с 8:00 до 20:00 (МСК)'''
    )
    if message.photo:
        photo_info = message.photo[-1]
        unique_filename = str(uuid.uuid4()) + ".jpg"
        photo = await bot.download(photo_info, destination=f"template/{unique_filename}")
        with open(f"template/{unique_filename}", "rb") as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        await state.update_data(image=base64_image)
        await state.update_data(descr=message.caption)
        await state.set_state(new_service.add_request)
        if sent == False:
            sent = True
            await state.set_state(new_service.add_request)
            await bot.send_message(message.chat.id, send_message, reply_markup=Keybord.critical_kb)
    else:
        await state.update_data(descr=message.text)
        await state.set_state(new_service.add_request)
        await bot.send_message(message.chat.id, send_message, reply_markup=Keybord.critical_kb)
    
    
    
@router.callback_query(new_service.add_request)
async def add_service(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    login = callback.from_user.username
    number = await db.find_number(login)
    message_send = f"✅@{login}, Заявка успешно создана"
    if callback.data == "Critical":
        critical = "agreement$2352101"
    else:
        critical = "agreement$605301"
    data = await state.get_data()  
    result = await req.send_service_to_api(short=data["short"], descr= data["descr"], critical = critical , ou_uid=data["ou_uid"], user_uuid=data["user_uuid"], office=data["office"], number = number, login = login,  image=data.get("image"))
    if result == True:
        if data["user_uuid"] == "0":
            await bot.send_message(callback.message.chat.id,(message_send), reply_markup=Keybord.main_kb)
        else:
            key = await db.key(login)
            if key == 0:
                await bot.send_message(callback.message.chat.id,(message_send), reply_markup=Keybord.main_kb_key)
            else:
                await bot.send_message(callback.message.chat.id,(message_send), reply_markup=Keybord.main_kb)     
        await state.clear()