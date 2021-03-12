from .database import Database


class SystemEmailsHelper(Database):

    def __init__(self, *args):
        super(SystemEmailsHelper, self).__init__(*args)

    def insert_system_emails(self, user_id, email_type, status):
        data = {"user_id", "email_type", "status", [user_id, email_type, status]}
        return self.insert("system_emails", data)

        # query = "INSERT INTO system_emails(user_id, email_type, status) " \
        #         "VALUE (%s, %s, %s)"
        # return self.add(query, (user_id, email_type, status))
