from .database import Database


class Authenticate(Database):

    def __init__(self, *args):
        super(Authenticate, self).__init__(*args)

    def create_account(self, firstname, lastname, email, pw_hash):
        data = {"firstname": firstname, "lastname": lastname, "email": email, "password": pw_hash}
        return self.insert("user", data)

    def authenticate(self, email):
        fields = ('id', 'password', 'firstname', 'lastname')
        where = ('email = %s', [email])
        return self.getOne("user", fields, where)
