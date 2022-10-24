from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from Database.dbConnection import Sqlite
from Handlers.Keyboards import inline_keyboard
from Handlers.Login import SignIn
from Handlers.Parser.parse_moodle import Parser
from Handlers.bot_message import text_msg
from Loader import dp, bot
from config import db_name

db = Sqlite(db_name)


class Form(StatesGroup):
    barcode = State()
    password = State()


@dp.message_handler(Command('start'))
async def start_bot(message: Message):
    try:
        await message.answer(text=str(text_msg.get('start')))
        if db.exists_user(message.chat.id):
            await message.answer(text=str(text_msg.get('write_barcode')))
            await Form.barcode.set()
        else:
            await message.answer(text=text_msg.get('already_registered'))
            await message.answer(text=text_msg.get('menu_title'), reply_markup=inline_keyboard.generator_main_menu())
    except Exception as e:
        print(e)


@dp.message_handler(state=Form.barcode)
async def get_login(message: Message, state: FSMContext):
    try:
        await state.reset_state()
        async with state.proxy() as data:
            data['barcode'] = message.text
            await state.finish()
            await message.answer(text=str(text_msg.get('write_password')))
            await Form.password.set()
    except Exception as e:
        print(e)


@dp.message_handler(state=Form.password)
async def get_password(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
        await state.finish()
        sign_in = SignIn(data)
        user_token = sign_in.auth_moodle()
        if user_token is not None:
            db.new_user(message.chat.id, data['barcode'], data['password'])
            await message.answer(text=text_msg.get('congratulation'))
            await message.answer(text=text_msg.get('menu_title'), reply_markup=inline_keyboard.generator_main_menu())
        else:
            await message.answer(text=text_msg.get('error_login'))
            await message.answer(text='Please write Barcode:')
            await Form.barcode.set()


@dp.callback_query_handler(text_contains='menu')
async def menu_guide_callback(call: CallbackQuery):
    await call.answer(cache_time=60)
    chosen_btn = call.data.split(':')[1]
    parser = Parser()
    if chosen_btn == 'grade_overview':
        await call.message.answer(text=parser.parse_overview_grade(call.message.chat.id))
    elif chosen_btn == 'attendance_overview':
        await call.message.answer(text=parser.parse_overview_attendance(call.message.chat.id))
    elif chosen_btn == 'deadlines_overview':
        await call.message.answer(text=parser.parse_overview_deadline(7, call.message.chat.id))
    elif chosen_btn == 'show_lessons':
        await call.message.answer(text='Your courses( choose one of them ):', reply_markup=inline_keyboard
                                  .generator_lesson_menu(parser.parse_lessons(call.message.chat.id)))
    else:
        pass


@dp.callback_query_handler(text_contains='lesson')
async def show_lesson_list(call: CallbackQuery):
    await call.answer(cache_time=60)
    lesson_info = call.data.split(':')
    parser = Parser()
    await call.message.answer(text='<b>' + parser.get_name_of_course_by_id(call.message.chat.id, lesson_info[1])
                                   + '</b>', reply_markup=inline_keyboard.
                              generator_course_instruct_menu(lesson_info[1]))


@dp.callback_query_handler(text_contains='course_instruct')
async def show_course_details(call: CallbackQuery):
    await call.answer(cache_time=60)
    parser = Parser()
    course_info = call.data.split(':')
    if course_info[1] == 'grade':
        await call.message.answer(text=parser.get_detailed_grades(
            call.message.chat.id, course_info[2]))
    else:
        pass
