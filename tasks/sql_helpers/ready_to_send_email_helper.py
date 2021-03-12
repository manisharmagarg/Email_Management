from .database import Database


class ReadyToSendEmailsHelper(Database):

    def __init__(self, *args):
        super(ReadyToSendEmailsHelper, self).__init__(*args)

    def add_ready_to_emails(self, email_address, template_html, subject,
                            status, list_segment_id, campaign_type, campaign_id=None,
                            ab_campaign_id=None):

        data = {"email_address": email_address, "campaign_id": campaign_id,
                "ab_campaign_id": ab_campaign_id,
                "template_html": template_html, "subject": subject,
                "status": status, "list_segment_id": list_segment_id,
                'campaign_type': campaign_type}
        sql_cursor = self.insert("ready_to_send_emails", data)
        return sql_cursor

    def update_ready_to_send_status(self, campaign_id, email_address, status):
        data = {"status": status}
        where = ('campaign_id=%s and email_address=%s', [campaign_id, email_address])
        self.update("ready_to_send_emails", data, where)

    def update_ab_ready_to_send_status(self, ab_campaign_id, email_address, status):
        data = {"status": status}
        where = ('ab_campaign_id=%s and email_address=%s', [ab_campaign_id, email_address])
        self.update("ready_to_send_emails", data, where)

    # def get_ready_to_send_emails__by_asc_order(self):
    #     query = "SELECT * FROM ready_to_send_emails ORDER BY id ASC LIMIT 10"
    #     return self.fetch_all(query)

    def check_is_emails_records(self, email_address, campaign_id):
        # query = "Select id from ready_to_send_emails where " \
        #         "email_address='%s' and campaign_id='%s'" \
        #         % (str(email_address), campaign_id)
        #
        # emails_records = self.fetch_all(query)
        # if emails_records and len(emails_records) > 0:
        #     return True
        #
        # return False

        sql = "Select id from ready_to_send_emails where " \
                "email_address=%s and campaign_id=%s"

        emails_records = self.query(sql, [email_address, campaign_id])
        record_list = []
        for emails_record in emails_records:
            record_list.append(emails_record)
        if record_list and len(record_list) > 0:
            return True
        return False

    def check_is_ab_emails_records(self, email_address, campaign_id):
        # query = "Select id from ready_to_send_emails where " \
        #         "email_address='%s' and campaign_id='%s'" \
        #         % (str(email_address), campaign_id)
        #
        # emails_records = self.fetch_all(query)
        # if emails_records and len(emails_records) > 0:
        #     return True
        #
        # return False

        sql = "Select id from ready_to_send_emails where " \
                "email_address=%s and ab_campaign_id=%s"

        emails_records = self.query(sql, [email_address, campaign_id])
        record_list = []
        for emails_record in emails_records:
            record_list.append(emails_record)
        if record_list and len(record_list) > 0:
            return True
        return False

    def check_if_email_already_queued(self, email_address, campaign_id):
        sql = "Select id from ready_to_send_emails where status='QUEUED' and " \
              "email_address = %s and campaign_id = %s"

        # emails_records = self.fetch_all(query)
        emails_records = self.query(sql, [email_address, campaign_id])
        record_list = []
        for emails_record in emails_records:
            record_list.append(emails_record)
        if record_list and len(record_list) > 0:
            return True
        return False

    def check_if_ab_email_already_queued(self, email_address, ab_campaign_id):
        sql = "Select id from ready_to_send_emails where status='QUEUED' and " \
              "email_address = %s and ab_campaign_id = %s"

        # emails_records = self.fetch_all(query)
        emails_records = self.query(sql, [email_address, ab_campaign_id])
        record_list = []
        for emails_record in emails_records:
            record_list.append(emails_record)
        if record_list and len(record_list) > 0:
            return True
        return False

    def get_all_ready_to_send_emails(self):
        sql = "SELECT rs.id, rs.email_address, rs.campaign_id, rs.template_html, rs.subject," \
              " rs.list_segment_id, rs.status, cp.list_id, cp.templates_id" \
              " FROM ready_to_send_emails rs inner join campaigns cp on cp.id = rs.campaign_id" \
              " where rs.status='READY_TO_SEND'"
        # sql = "SELECT rs.id, rs.email_address, rs.campaign_id, rs.template_html, rs.subject, " \
        #       "rs.list_segment_id, rs.status, cp.list_id, cp.templates_id " \
        #       "FROM ready_to_send_emails rs inner join campaigns cp on cp.id = rs.campaign_id " \
        #       "where rs.status='READY_TO_SEND' and cp.status = 'QUEUED'"
        return self.query(sql)

    def get_campaign_status(self, campaign_id):
        fields = {'id', 'status'}
        where = ('id = %s', [campaign_id])
        return self.getAll('campaigns', fields=fields, where=where)

    def get_ab_campaign_parent(self, campaign_id):
        fields = {'id', 'ab_campaign_parent_id'}
        where = ('id = %s', [campaign_id])
        return self.getAll('ab_campaigns', fields=fields, where=where)

    def get_ab_campaign_status(self, campaign_id):
        fields = {'id', 'status'}
        where = ('id = %s', [campaign_id])
        return self.getAll('ab_campaigns_parent', fields=fields, where=where)

    def get_all_ready_to_ab_send_emails(self):
        sql = "SELECT rs.id, rs.email_address, rs.ab_campaign_id, rs.template_html, rs.subject, rs.status, " \
              "rs.list_segment_id, ab.list_id, cp.templates_id FROM ready_to_send_emails rs " \
              "left join ab_campaigns cp on cp.id = rs.ab_campaign_id left join ab_campaigns_parent ab " \
              "on cp.ab_campaign_parent_id = ab.id where rs.status='READY_TO_SEND' " \
              "and rs.ab_campaign_id IS NOT NULL"
        return self.query(sql)

    def get_all_ab_ready_to_send_emails(self):
        sql = "SELECT rs.id, rs.email_address, rs.campaign_id, rs.template_html, rs.subject," \
                " rs.list_segment_id, cp.list_id, cp.templates_id" \
                " FROM ready_to_send_emails rs inner join ab_campaigns ab_cp on ab_cp.id = rs.campaign_id" \
                " where rs.status='READY_TO_SEND'"
        return self.query(sql)

    # def get_all_ready_to_send_emails_by_status_readytosend(self):
    #     query = "Select * from ready_to_send_emails where status='READY_TO_SEND'"
    #     return self.fetch_all(query)

    def get_all_ready_to_send_emails_by_status(self):
        sql = "Select id from ready_to_send_emails where created_on > NOW() - INTERVAL 1 HOUR"
        return self.query(sql, params=None)
        # return self.fetch_all(query)
        # fields = ('id')
        # where = ("created_on > NOW() - INTERVAL 1 HOUR")
        # return self.getAll('ready_to_send_emails', fields=fields, where=where)

    def get_all_emails_by_campaign(self, campaign_id):
        fields = ('id', 'campaign_id')
        where = ("campaign_id = %s ", [campaign_id])
        return self.getAll('ready_to_send_emails', fields=fields, where=where)

    def get_all_emails_by_campaigns(self, campaign_id):
        fields = ('id', 'list_segment_id')
        where = ("(status = 'SENT' or status = 'ERROR') and campaign_id = %s ", [campaign_id])
        return self.getAll('ready_to_send_emails', fields=fields, where=where)

    def get_all_emails_by_AB_campaign(self, campaign_id):
        fields = ('id', 'list_segment_id')
        where = ("(status = 'SENT' or status = 'ERROR') and ab_campaign_id = %s ", [campaign_id])
        return self.getAll('ready_to_send_emails', fields=fields, where=where)

