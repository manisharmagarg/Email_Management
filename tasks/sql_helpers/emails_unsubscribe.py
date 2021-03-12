from .database import Database


class EmailUnsubscribeHelper(Database):

    def __init__(self, *args):
        super(EmailUnsubscribeHelper, self).__init__(*args)

    def create_email_unsubscribe(self, email_address, created_on):
        data = {"email_address": email_address, "created_on": created_on}
        sql_cursor = self.insert("unsubscribe", data)
        return sql_cursor

    def check_emails_record(self, email_address):
        fields = ('id', 'email_address')
        where = ("email_address = %s", [email_address])
        return self.getAll('unsubscribe', fields=fields, where=where)
