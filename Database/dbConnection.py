import sqlite3


class Sqlite:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()

    def create_user_table(self):
        self.cur.execute('Create table if not exists users('
                         'id integer PRIMARY KEY AUTOINCREMENT NOT NULL,'
                         'chat_id integer,'
                         'barcode varchar(255),'
                         'password varchar(255),'
                         'purpose int,'
                         'st_group varchar(255))')

    def new_user(self, chat_id, barcode, password):
        self.cur.execute(f'Insert into users(chat_id, barcode, password) values("{chat_id}","{barcode}","{password}")')
        self.conn.commit()

    def get_log_info_by_chat_id(self, chat_id):
        self.cur.execute(f'Select barcode, password from users where chat_id="{chat_id}"')
        return self.cur.fetchone()

    def exists_user(self, chat_id):
        self.cur.execute(f'Select count(*) from users where chat_id="{chat_id}"')
        return self.cur.fetchone()[0] == 0
