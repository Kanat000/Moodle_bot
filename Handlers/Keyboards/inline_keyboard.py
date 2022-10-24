from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Handlers.Keyboards import callback_data
from Handlers.bot_message import btn_msg, lesson_btn_message


def generator_main_menu():
    main_menu = InlineKeyboardMarkup(row_width=1)
    for key in btn_msg.keys():
        main_menu.insert(
            InlineKeyboardButton(text=f'{btn_msg.get(key)}',
                                 callback_data=callback_data.main_menu_callback.new(chosen=key))
        )
    return main_menu


def generator_lesson_menu(courses):
    lesson_menu = InlineKeyboardMarkup(row_width=1)
    for course in courses:
        lesson_menu.insert(
            InlineKeyboardButton(text=f'{course[0]}', callback_data=callback_data.lesson_menu_callback.new(
                id=course[1]
            ))
        )
    return lesson_menu


def generator_course_instruct_menu(course_id):
    instruct_menu = InlineKeyboardMarkup(row_width=1)
    for key in lesson_btn_message.keys():
        instruct_menu.insert(
            InlineKeyboardButton(text=f'{lesson_btn_message.get(key)}',
                                 callback_data=callback_data.course_instruct_menu_callback.new(
                                     function=key, id=course_id
                                 ))
        )
    return instruct_menu
