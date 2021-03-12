from .database import Database


class ReadyToSendEmailsHelper(Database):

    def __init__(self, *args):
        super(ReadyToSendEmailsHelper, self).__init__(*args)

    def add_ready_to_emails(self, email_address, campaign_id, html_template, subject, status):
        data = {"email_address": email_address, "campaign_id": campaign_id, "html_template": html_template,
                "subject": subject, "status": status}
        self.insert("ready_to_send_emails", data)

        # query = "INSERT INTO ready_to_send_emails(email_address, campaign_id, html_template, subject, status) " \
        #         "VALUE (%s, %s, %s, %s, %s)"
        #
        # self.add(query, (email_address, campaign_id, html_template, subject, status))

    def get_all_emails_to_queued(self, campaign_id):
        fields = ('id', 'email_address', 'email_address', 'campaign_id', 'template_html', 'subject',
                  'status', 'list_segment_id', 'created_on')
        where = ('status=%s or status=%s ', ['READY_TO_SEND', ' '])
        return self.getAll("ready_to_send_emails", fields, where)

        # query = "Select * from ready_to_send_emails " \
        #         "where (status='READY_TO_SEND' or status='QUEUED') and campaign_id=%s;" % campaign_id
        # return self.fetch_all(query)

    def get_total_email_in_segment(self, list_id):
        fields = ('id', 'email', 'list_id', 'user_id', 'created_on')
        where = ('list_id=%s', [list_id])
        return self.getAll("list_segments", fields, where)

        # query = "Select * from list_segments where list_id=%s" % list_id
        # return self.fetch_all(query)

    def get_error_send_emails(self, campaign_id):
        fields = ('id', 'email_address', 'email_address', 'campaign_id', 'template_html', 'subject',
                  'status', 'list_segment_id', 'created_on')
        where = ('campaign_id=%s and status=%s ', [campaign_id, 'SENT'])
        return self.getAll("ready_to_send_emails", fields, where)

        # query = "Select * from ready_to_send_emails " \
        #         "where status='SENT' and campaign_id=%s;" % campaign_id
        # return self.fetch_all(query)

    def get_error_emails(self, campaign_id):
        fields = ('id', 'email_address', 'email_address', 'campaign_id', 'template_html', 'subject',
                  'status', 'list_segment_id', 'created_on')
        where = ('campaign_id=%s and status=%s ', [campaign_id, 'ERROR'])
        return self.getAll("ready_to_send_emails", fields, where)

        # query = "Select * from ready_to_send_emails " \
        #         "where status='ERROR' and campaign_id=%s;" % campaign_id
        # return self.fetch_all(query)

    def get_send_emails(self, campaign_id):
        fields = ('id', 'email_address', 'email_address', 'campaign_id', 'subject',
                  'status', 'list_segment_id', 'created_on')
        where = ('campaign_id=%s and status=%s ', [campaign_id, 'SENT'])
        return self.getAll("ready_to_send_emails", fields, where)

    def get_ab_campaign_send_emails(self, campaign_id):
        # query = "select ab_campaign_id, email_address from email_management_db.ready_to_send_emails " \
        #         "where ab_campaign_id = {} and status = %s".format(campaign_id, 'SENT')
        # return self.query(query)

        fields = ('id', 'email_address', 'email_address', 'ab_campaign_id', 'template_html', 'subject',
                  'status', 'list_segment_id', 'created_on')
        where = ('ab_campaign_id=%s and status=%s ', [campaign_id, 'SENT'])
        return self.getAll("ready_to_send_emails", fields, where)


        # query = "Select * from ready_to_send_emails " \
        #         "where status='SENT' and campaign_id=%s;" % campaign_id
        # return self.fetch_all(query)

    def get_unsubscribe_emails(self, campaign_id):
        fields = ('id', 'email_address')
        where = ('campaign_id=%s and status=%s ', [campaign_id, 'UNSUBSCRIBE'])
        return self.getAll("ready_to_send_emails", fields, where)

    def get_ab_unsubscribe_emails(self, campaign_id):
        fields = ('id', 'email_address')
        where = ('ab_campaign_id=%s and status=%s ', [campaign_id, 'UNSUBSCRIBE'])
        return self.getAll("ready_to_send_emails", fields, where)

    def get_sent_emails_by_date(self, date):
        fields = ('id', 'status')
        where = ("(status='SENT' or status = 'ERROR' or "
                 "status = 'READY_TO_SEND' or status = 'QUEUED' or "
                 "status = 'UNSUBSCRIBE') and DATE(created_on) = %s", [date])
        return self.getAll('ready_to_send_emails', fields, where)

    def get_sent_emails_by_date_campaign_id(self, date, id):
        fields = ('id', 'status')
        where = ("(status='SENT' or status = 'ERROR' or "
                 "status = 'READY_TO_SEND' or status = 'QUEUED' or "
                 "status = 'UNSUBSCRIBE') and DATE(created_on) = %s and campaign_id = %s", [date, id])
        return self.getAll('ready_to_send_emails', fields, where)

    def get_ab_sent_emails_by_date_campaign_id(self, date, id):
        fields = ('id', 'status')
        where = ("(status='SENT' or status = 'ERROR' or "
                 "status = 'READY_TO_SEND' or status = 'QUEUED' or "
                 "status = 'UNSUBSCRIBE') and DATE(created_on) = %s and ab_campaign_id = %s", [date, id])
        return self.getAll('ready_to_send_emails', fields, where)

    def get_sent_emails_by_id(self, id):
        fields = ('id', 'status')
        where = ("(status='SENT' or status = 'ERROR' or "
                 "status = 'READY_TO_SEND' or status = 'QUEUED' or "
                 "status = 'UNSUBSCRIBE') and campaign_id = %s", [id])
        return self.getAll('ready_to_send_emails', fields, where)

    def get_ab_sent_emails_by_id(self, id):
        fields = ('id', 'status')
        where = ("(status='SENT' or status = 'ERROR' or "
                 "status = 'READY_TO_SEND' or status = 'QUEUED' or "
                 "status = 'UNSUBSCRIBE') and ab_campaign_id = %s", [id])
        return self.getAll('ready_to_send_emails', fields, where)

    def get_all_emails_by_id(self, campaign_id=None):
        fields = ('id', 'status', )
        where = ("(status = 'READY_TO_SEND' or status = 'SENT' or status = 'ERROR' "
                 "or status = 'UNSUBSCRIBE') and campaign_id = %s", [campaign_id])
        return self.getAll('ready_to_send_emails', fields=fields, where=where)

    def check_status_by_ab_campaign_id(self, ab_campaign_id):
        query = "SELECT count(CASE WHEN status LIKE '%UNSUBSCRIBE%' THEN 1 END) AS unsubscribe " \
                "FROM ready_to_send_emails where ab_campaign_id ={}".format(ab_campaign_id)
        return self.query(query)

    def update_status_to_pause(self, campaign_id, campaign_type, status):
        data = {"status": status}
        where = ("status = %s and campaign_type = %s "
                 "and campaign_id = %s", ['READY_TO_SEND', campaign_type, campaign_id])
        self.update("ready_to_send_emails", data, where)

    def update_ab_status_to_pause(self, campaign_id, campaign_type, status):
        data = {"status": status}
        where = ("status = %s and campaign_type = %s "
                 "and ab_campaign_id = %s", ['READY_TO_SEND', campaign_type, campaign_id])
        self.update("ready_to_send_emails", data, where)

    def update_status_to_resume(self, campaign_id, campaign_type, status):
        data = {"status": status}
        where = ("status = %s and campaign_type = %s "
                 "and campaign_id = %s", ['PAUSE', campaign_type, campaign_id])
        self.update("ready_to_send_emails", data, where)

    def update_ab_status_to_resume(self, campaign_id, campaign_type, status):
        data = {"status": status}
        where = ("status = %s and campaign_type = %s "
                 "and ab_campaign_id = %s", ['PAUSE', campaign_type, campaign_id])
        self.update("ready_to_send_emails", data, where)

    def get_ab_send_emails(self, campaign_id):
        fields = ('id', 'email_address', 'email_address', 'campaign_id', 'template_html', 'subject',
                  'status', 'list_segment_id', 'created_on')
        where = ('campaign_id=%s and status=%s ', [campaign_id, 'SENT'])
        return self.getAll("ready_to_send_emails", fields, where)

    def check_ready_to_send_data_by_campaign_id(self, campaign_id):
        fields = {'id', 'campaign_id', 'email_address'}
        where = ("status = %s and campaign_id = %s", ['PAUSE', campaign_id])
        get_data = self.getAll('ready_to_send_emails', fields=fields, where=where)
        if get_data:
            return True
        return False

    def check_ready_to_send_data_by_ab_campaign_id(self, campaign_id):
        fields = {'id', 'campaign_id', 'email_address'}
        where = ("status = %s and ab_campaign_id = %s", ['PAUSE', campaign_id])
        get_data = self.getAll('ready_to_send_emails', fields=fields, where=where)
        if get_data:
            return True
        return False

    def get_sent_email_by_date(self, date):
        fields = ('email_address', 'subject')
        return self.getAll('ready_to_send_emails', fields)
