from .database import Database


class User(Database):

    def __init__(self, *args):
        super(User, self).__init__(*args)

    def get_email_user(self):
        fields = ('name', 'email', 'created_on')
        return self.getAll('email_user', fields=fields)

