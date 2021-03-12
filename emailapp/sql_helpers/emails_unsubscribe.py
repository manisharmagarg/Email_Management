from .database import Database

class EmailUnsubscribeHelper(Database):

    def __init__(self, *args):
        super(EmailUnsubscribeHelper, self).__init__(*args)

    def create_email_unsubscribe(self, email_address, campaign_id):
        data = {"email_address": email_address, "campaign_id": campaign_id}
        unsubscribe_id = self.insert("unsubscribe", data)

        # query = "INSERT INTO unsubscribe(email_address, campaign_id) " \
        #         "VALUE (%s, %s)"
        # unsubscribe_id = self.add(query, (email_address, campaign_id))
        return unsubscribe_id

    def check_unsubscribe_emails(self, email_address):
        fields = ('id', 'email_address')
        where = ('email_address = %s', [email_address])
        emails = self.getOne("unsubscribe", fields, where)
        # return emails
        if emails:
            return True
        return False

    def check_emails_record(self, email_address):
        fields = ('id', 'email_address')
        where = ("email_address = %s", [email_address])
        return self.getAll('unsubscribe', fields=fields, where=where)

