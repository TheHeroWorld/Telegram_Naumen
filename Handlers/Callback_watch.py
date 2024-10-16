import base64  # Модуль для кодирования и декодирования данных в формате Base64
import re  # Модуль для работы с регулярными выражениями
import uuid  # Модуль для генерации уникальных идентификаторов UUID

from aiogram import Router, types, F, Bot # Модуль для работы с Telegram API
from aiogram.fsm.context import FSMContext  # Контекст конечного автомата для управления состояниями
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup  # Типы данных и кнопки для Telegram API

from bs4 import BeautifulSoup  # Модуль для парсинга HTML и XML документов

import KeyBord.Keybord as Keybord  # Клавиатура 
import db.db as db  # База данных
import req.req as req  # rest запросы
from utils.states import add_comment  # Машина состояний 


sent = False

router = Router()





@router.callback_query(F.data == "Watch")
async def Watch(callback: types.CallbackQuery, bot: Bot,  state: FSMContext):
    global user_uuid
    login = callback.from_user.username
    auth = await db.auth(login)
    if auth == 1:
        await un_Watch(callback, bot,state)
    else:
        user_uuid = await db.take_userUUID(login)
        requests = await req.view_requests(user_uuid)
        if requests:
            for request in requests:
                            unauth = False
                            uuid = request.get('UUID', 'N/A') 
                            number = request.get('number', 'N/A')
                            shortDescr = request.get('shortDescr', 'N/A')
                            descriptionRTF = request.get('descriptionRTF', 'N/A')
                            responsible = request.get('responsible', {})
                            state_service = request.get('state', {})
                            if state_service == "registered":
                                state_message = "🔴Новая"
                            elif state_service == "waitClientAnswer":
                                state_message = "🟡В ожидании вашего ответа"
                            elif state_service == "deferred":
                                state_message = "🔵Отложена"
                            else:
                                state_message = "🟢В работе"
                            if responsible is not None:
                                responsible_title = responsible.get('title', 'N/A')
                            else:
                                responsible_title = 'Еще не назначен'
                            if descriptionRTF is not None:
                                soup = BeautifulSoup(descriptionRTF, 'html.parser')
                                description_text = soup.get_text()
                            else:
                                description_text = " "
                            output_message = f"📌Заявка №{number}\n" \
                                            f"{state_message}\n" \
                                            f"📝Тема: {shortDescr}\n" \
                                            f"📖Описание: {description_text}\n" \
                                            f"👨‍💻Ответственный: {responsible_title}\n\n"\
                                            f"ℹ️ Выберите действие на сообщении с нужно заявкой, или вернитесь в главное меню"
                                            
                            request_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Добавить комментарий", callback_data=f"add_comment_{uuid}_{number}",),
                                                                            InlineKeyboardButton(text="Посмотреть комментарии",callback_data=f"watch_comment_{uuid}_{unauth}_{number}")]]
                                                        )
                            await bot.send_message(callback.message.chat.id,(output_message), reply_markup=request_kb)
                            await state.update_data(user_uuid=user_uuid)
        else:
            output_message = "У вас нет открытых заявок "
            await bot.send_message(callback.message.chat.id,(output_message), reply_markup=Keybord.main_kb)


@router.callback_query(F.data == "Watch_unauth")
async def un_Watch(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    login = callback.from_user.username
    requests = await db.find_tasks_by_login(login)
    print(requests)
    found_requests = False  # Флаг, указывающий, были ли найдены заявки
    for item in requests:
        item = item[0]
        info = await req.find_task(item)
        if info:
            found_requests = True  # Установка флага, если найдены заявки
            unauth = True
            number = info[0]['number']
            shortDescr = info[0]['shortDescr']
            descriptionRTF = info[0]['descriptionRTF']
            responsible_title = info[0]['responsible']['title']
            uuid = info[0]['UUID']
            state_service = info[0]['state']
            if state_service == "registered":
                state_message = "🔴Новая"
            elif state_service == "waitClientAnswer":
                state_message = "🟡В ожидании вашего ответа"
            elif state_service == "deferred":
                state_message = "🔵Отложена"
            else:
                state_message = "🟢В работе"
            if descriptionRTF is not None:
                soup = BeautifulSoup(descriptionRTF, 'html.parser')
                description_text = soup.get_text()
            output_message = f"📌Заявка №{number}\n" \
                             f"{state_message}\n" \
                             f"📝Тема: {shortDescr}\n" \
                             f"📖Описание:{description_text}\n" \
                             f"👨‍💻Ответственный: {responsible_title}\n\n"\
                             f"ℹ️ Выберите действие на сообщении с нужно заявкой, или вернитесь в главное меню"
            request_kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Добавить комментарий", callback_data=f"add_comment_{uuid}_{number}"),
                 InlineKeyboardButton(text="Посмотреть комментарии",
                                      callback_data=f"watch_comment_{uuid}_{unauth}_{number}")]]
            )
            await state.update_data(user_uuid="0")
            await bot.send_message(callback.message.chat.id, output_message, reply_markup=request_kb)
    if not found_requests:
        output_message = "У вас нет открытых заявок "
        await bot.send_message(callback.message.chat.id, output_message, reply_markup=Keybord.main_kb)





@router.callback_query(F.data.contains("watch_comment"))
async def Watch_comment(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    uuid = callback.data.split('_')[2]
    unauth = callback.data.split('_')[3]
    number = callback.data.split('_')[4]
    comments = await req.view_comment(uuid)
    if not comments:
        message = f"😒 Нет комментариев к заявке {number}"
        await bot.send_message(callback.message.chat.id,(message), reply_markup=Keybord.main_kb)
    else:
        service_message = f"🖥 Комменатрии к заявки {number}"
        await bot.send_message(callback.message.chat.id,(service_message))
    for comment in comments:
        author = comment.get("author", None)
        private = comment.get("private")
        if private == False:
            if author is not None:
                author_title = author.get("title", "Автор не указан")
                author_id = author.get("UUID")
                if not unauth and author_id == user_uuid:
                    author_emoji = "👨‍💻"
                else:
                    author_emoji = "⚙️"
            else:
                author_title = "Автор"
                author_emoji = "😏" 

            text = comment.get("text", "Комментарий отсутствует")
            soup = BeautifulSoup(text, 'html.parser')
            comment_text = soup.get_text()
            file_match = re.search(r'file\$([\d]+)', text)
            if file_match:
                file_uuid = file_match.group(1)
                download = await req.download_photo(file_uuid)
                if download:
                    comment_message = f"{author_emoji}{author_title}\nКомментарий: {comment_text}\n"
                    photo = FSInputFile(f"template/{file_uuid}.jpg")
                    await bot.send_photo(callback.message.chat.id,photo=photo, caption=comment_message)
                else:
                    await bot.send_message(callback.message.chat.id, "Ошибка загрузки фото")
            else:
                comment_message = f"{author_emoji}{author_title}\nКомментарий: {comment_text}\n"
                await bot.send_message(callback.message.chat.id, comment_message)


    

@router.callback_query(F.data.contains("add_comment"))
async def handler_comment(callback: types.CallbackQuery, bot: Bot, state:FSMContext):
    global sent
    sent = False
    uuid = callback.data.split('_')[2]
    number = callback.data.split('_')[3]
    await state.update_data(uuid=uuid)
    comment_message = f"✍️ Напишите ваш комментарий к заявке {number} , я передам специалистам "
    await state.set_state(add_comment.progress)
    await bot.send_message(callback.message.chat.id, (comment_message), reply_markup=Keybord.cancel_kb)
    
@router.message(add_comment.progress)
async def handle_add_comment(message: types.Message, bot: Bot, state: FSMContext):
    login = message.from_user.username
    key = await db.key(login)
    global sent
    if message.photo:
        unique_filename = str(uuid.uuid4()) + ".jpg"
        photo_info = message.photo[-1]
        photo = await bot.download(photo_info, destination=f"template/{unique_filename}")
        with open(f"template/{unique_filename}", "rb") as image_file:
            image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        await state.update_data(image=base64_image)
        await state.update_data(comment=message.caption)
    else:
        await state.update_data(comment=message.text)
    data = await state.get_data()
    user = data["user_uuid"]
    result = await req.send_comment_to_api(
        uuid=data["uuid"],
        user_uuid=data["user_uuid"],
        user_comment=data["comment"],
        image=data.get("image")
    )
    if result == False:
        message_send = "Произошла ошибка, попробуйте еще раз"
        sent = False
    else:
        message_send = f"👌@{login}, Комментарий добавлен"
        if sent == False:
            if user != "0":
                if key == 0:
                    await bot.send_message(message.chat.id,(message_send), reply_markup=Keybord.main_kb_key)
                else:
                    await bot.send_message(message.chat.id, message_send, reply_markup=Keybord.main_kb)
                    sent = True
            else:
                await bot.send_message(message.chat.id, message_send, reply_markup=Keybord.main_kb_unauth)
                sent = True
            await state.clear()
        
        
@router.callback_query(F.data == "Watch_all")
async def Watch_all(callback: types.CallbackQuery, bot: Bot,  state: FSMContext):
    login = callback.from_user.username
    user_uuid = await db.take_userUUID(login)
    ou_uid = await db.take_OUUID(user_uuid)
    task = await req.take_task()
    found_request = False  # Флаг для отслеживания найденных заявок
    for request in task:
        uuid = request.get('UUID', 'N/A')
        number = request.get('number', 'N/A')
        shortDescr = request.get('shortDescr', 'N/A')
        descriptionRTF = request.get('descriptionRTF', 'N/A')
        responsible = request.get('responsible', {})
        if responsible is not None:
            responsible_title = responsible.get('title', 'N/A')
        else:
            responsible_title = 'Еще не назначен'
        if descriptionRTF is not None:
            soup = BeautifulSoup(descriptionRTF, 'html.parser')
            description_text = soup.get_text()
        else:
            description_text = " "
        clientOU = request.get('clientOU', {})
        try:
            clientOU_UUID = clientOU.get('UUID', 'N/A')
        except:
            clientOU_UUID = None
        if ou_uid == clientOU_UUID:
            found_request = True  # Устанавливаем флаг в True, если найдена подходящая заявка
            unauth = False
            output_message = f"📞Номер заявки: {number}\n" \
                             f"📝Описание заявки: {shortDescr}\n" \
                             f"📖Текст заявки: {description_text}\n" \
                             f"🪓Ответственный: {responsible_title}"
            request_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Добавить комментарий", callback_data=f"add_comment_{uuid}_{number}",),
                                                                InlineKeyboardButton(text="Посмотреть комментарии",callback_data=f"watch_comment_{uuid}_{unauth}_{number}")]]
                                            )
            await bot.send_message(callback.message.chat.id,(output_message), reply_markup=request_kb)
            await state.update_data(user_uuid = user_uuid)
    if not found_request:
        output_message = "У вас нет открытых заявок "
        await bot.send_message(callback.message.chat.id,(output_message), reply_markup=Keybord.main_kb)