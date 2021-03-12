import mysql.connector
from conf.config import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, DBNAME


class SqlHelper(object):

    my_sql_cursor = mysql.connector.connect(user=MYSQL_USER,
                                            password=MYSQL_PASS,
                                            host=MYSQL_HOST,
                                            database=DBNAME)

    def __init__(self):
        pass

    def create_table(self, query):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query)
            cursor.commit()
            print("Models created successfully")
            cursor.close()
        except Exception as e:
            print('[base] :: create_table() :: Got exception: %s' % e)

    def fetch_one(self, query):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query)
            data = cursor.fetchone()
            self.my_sql_cursor.commit()
            cursor.close()
            return data
        except Exception as e:
            print('[base] :: fetch_one() :: Got exception: %s' % e)
            raise e

    def fetch_all(self, query):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            self.my_sql_cursor.commit()
            cursor.close()
            return data
        except Exception as e:
            print('[base] :: fetch_all() :: Got exception: %s' % e)
            raise e

    def add(self, query, data):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query, data)
            self.my_sql_cursor.commit()
            inserted_id = cursor.lastrowid
            cursor.close()
            return inserted_id
        except Exception as e:
            print('[base] :: add() :: Got exception: %s' % e)
            raise e

    def delete_record(self, query):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query)
            self.my_sql_cursor.commit()
            cursor.close()
        except Exception as e:
            print('[base] :: delete_record() :: Got exception: %s' % e)
            raise e

    def get_user_auth_id(self, query):
        cursor = self.my_sql_cursor.cursor()
        cursor.execute(query)
        data = cursor.fetchone()
        self.my_sql_cursor.commit()
        cursor.close()
        return data[0]

    def update_email_config(self, query):
        cursor = self.my_sql_cursor.cursor()
        cursor.execute(query)
        self.my_sql_cursor.commit()
        cursor.close()
