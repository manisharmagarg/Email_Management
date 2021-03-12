from .database import Database


class User(Database):

    def __init__(self, *args):
        super(User, self).__init__(*args)

    def get_email_user(self):
        return self.getAll("email_user", fields=('name', 'email', 'created_on'))
        # query = "SELECT name, email, created_on FROM email_user"
        # return self.fetch_all(query)

    def insert_email_user(self, name, email, user_id):
        data ={'name': name, 'email': email, 'user_id': user_id}
        return self.insert_email_user("email_user", data)
