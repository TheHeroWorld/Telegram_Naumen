from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


main_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Создать заявку", callback_data="New",),
                                                InlineKeyboardButton(text="Посмотреть свои заявки",callback_data="Watch")]]
                               )
main_kb_key = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Создать заявку", callback_data="New",),
                                                InlineKeyboardButton(text="Посмотреть свои заявки",callback_data="Watch")],
                                                [InlineKeyboardButton(text="Посмотреть заявки компании",callback_data="Watch_all")]]
                               )

main_kb_unauth = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Создать заявку", callback_data="New",),
                                                InlineKeyboardButton(text="Посмотреть свои заявки",callback_data="Watch_unauth")]]
                               )


request_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Добавить комментарий", callback_data=f"add_comment",),
                                                InlineKeyboardButton(text="Посмотреть комментарии",callback_data="Watch_comment")]]
                               )


critical_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔥Остановка продаж🔥", callback_data="Critical",),
                                                    InlineKeyboardButton(text="Прочее",callback_data="NoCritical",),
                                                    InlineKeyboardButton(text="Отмена", callback_data="cancel")]])


cancel_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="cancel")]])


unauth_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Нет подходящих", callback_data="Chose_")]])


contact_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отправить контакт", request_contact=True)]],resize_keyboard=True, one_time_keyboard= True)
refresh_contact_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Обновить данные", request_contact=True)]],resize_keyboard=True, one_time_keyboard= True)



async def chose_board(office_data_list):
    builder = InlineKeyboardBuilder()
    for item in office_data_list:
        comment_message = item.get("comment_message")
        ofiiceuuid = item.get("ofiiceuuid")
        builder.button(text=comment_message, callback_data=f"Chose_{ofiiceuuid}")
    return builder.as_markup()
