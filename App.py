from aiogram import executor

from Database.dbConnection import Sqlite
from Handlers.bot_service import dp
from config import db_name

if __name__ == '__main__':
    Sqlite(db_name).create_user_table()
    executor.start_polling(dp)
