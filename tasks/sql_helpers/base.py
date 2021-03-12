import mysql.connector


class SqlHelper(object):

    my_sql_cursor = None

    auto_commit = True

    def __init__(self, **kwargs):
        self.my_sql_cursor = kwargs.get('my_sql_cursor')
        # self.my_sql_cursor.autocommit = False

    def fetch_one(self, query):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query)
            data = cursor.fetchone()
            # self.my_sql_cursor.commit()
            return data
        except Exception as e:
            print(e)
            raise e

    def fetch_all(self, query):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query)
            data = cursor.fetchall()
            # self.my_sql_cursor.commit()
            return data
        except Exception as e:
            print(e)
            raise e

    def add(self, query, data):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query, data)
            # self.commit()
        except Exception as e:
            print(e)
            raise e

    def delete_record(self, query):
        try:
            cursor = self.my_sql_cursor.cursor()
            cursor.execute(query)
            # self.commit()
        except Exception as e:
            print(e)
            #raise e

    def get_user_auth_id(self, query):
        cursor = self.my_sql_cursor.cursor()
        cursor.execute(query)
        data = cursor.fetchone()
        # self.commit()
        return data[0]

    def update_email_config(self, query):
        cursor = self.my_sql_cursor.cursor()
        cursor.execute(query)
        # self.commit()

    def commit(self):
        self.my_sql_cursor.commit()

    def force_commit(self):
        self.my_sql_cursor.commit()
