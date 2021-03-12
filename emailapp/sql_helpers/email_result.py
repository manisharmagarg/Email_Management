from .database import Database


class EmailResultHelper(Database):

    def __init__(self, *args):
        super(EmailResultHelper, self).__init__(*args)

    def create_email_results(self, campaign_id, list_id, list_segment_id,
                            template_id, result, result_desc):

        data = {"campaign_id": campaign_id, "list_id": list_id, "list_segment_id": list_segment_id,
                "templates_id": template_id,"result": result, "result_description": result_desc,}
        self.insert("email_results", data)

        # query = "INSERT INTO email_results(campaign_id, list_id, " \
        #         "list_segment_id, templates_id, result, result_description) " \
        #         "VALUE (%s, %s, %s, %s, %s, %s)"
        # self.add(query, (campaign_id, list_id, list_segment_id, template_id,
        #                  str(result), str(result_desc)))

    def get_email_result_by_campaign_segment_id(self, segment_id, campaign_id):
        fields = ('id', 'list_id')
        where = ('list_segment_id=%s and campaign_id=%s', [segment_id, campaign_id])
        return self.getAll("email_results", fields, where)

        # query = "Select id, list_id from email_results where list_segment_id=%s" \
        #                  " and campaign_id=%s" % (segment_id, campaign_id)
        # return self.fetch_all(query)

    def check_is_email_already_sent(self, list_segment_id, campaign_id):
        emails_sent = self.getAll("email_results", fields='*',
                                  where=('list_segment_id=%s and campaign_id=%s', [list_segment_id, campaign_id]))

        # query = "Select * from email_results where list_segment_id=%s and campaign_id=%s" \
        #         % (list_segment_id, campaign_id)
        # emails_sent = self.fetch_all(query)
        if emails_sent and len(emails_sent) > 0:
            return True
        return False

    def get_email_results_by_campaign_id(self, campaign_id):

        query = "Select em.id, em.list_id, em.list_segment_id, em.templates_id," \
                " em.result, em.result_description, " \
                "ls.list_name, lsg.email from email_results em" \
                " inner join list ls on ls.id=em.list_id" \
                " inner join list_segments lsg on lsg.id=em.list_segment_id" \
                " where campaign_id=%s"

        return self.query(query, [campaign_id])

    def get_sent_emails_by_date(self, date):
        fields = ('id', 'result')
        where = ("DATE(created_on) = %s and result = 'SENT' ", [date])

        return self.getAll('email_results', fields, where)

    def insert_delivery_notifications(self, notification_type, email_address, source_address,
                                      source_arn, source_ip, sending_account_id, remoteMtaIp,
                                      send_timestamp, message_id, subject):

        data = {"notification_type": notification_type,
                "email_address": email_address,
                "source_address":source_address,
                "source_arn":source_arn,
                "source_ip":source_ip,
                "sendingAccountId":sending_account_id,
                "remoteMtaIp":remoteMtaIp,
                "send_timestamp":send_timestamp,
                "message_id":message_id,
                "subject":subject,}
        return self.insert("delivery", data)

    def insert_bounce_notifications(self, notification_type, email_address, source_address,
                                    source_arn, source_ip, sending_account_id, remoteMtaIp,
                                    send_timestamp, message_id, subject):

        data = {"notification_type": notification_type,
                "email_address": email_address,
                "source_address":source_address,
                "source_arn":source_arn,
                "source_ip":source_ip,
                "sendingAccountId":sending_account_id,
                "remoteMtaIp":remoteMtaIp,
                "send_timestamp":send_timestamp,
                "message_id":message_id,
                "subject": subject, }
        return self.insert("bounce", data)


    def insert_complaint_notifications(self, notification_type, email_address, source_address,
                                    source_arn, source_ip, sending_account_id,
                                    send_timestamp, message_id, subject):

        data = {"notification_type": notification_type,
                "email_address": email_address,
                "source_address":source_address,
                "source_arn":source_arn,
                "source_ip":source_ip,
                "sendingAccountId":sending_account_id,
                "send_timestamp":send_timestamp,
                "message_id":message_id,
                "subject": subject, }
        return self.insert("complaint", data)

    def get_bounce_notifications(self):
        fields = ('notification_type', 'email_address', 'source_address', 'source_arn',
                  'source_ip', 'sendingAccountId', 'remoteMtaIp', 'send_timestamp', 'message_id', 'subject')

        return self.getAll('bounce', fields)

    def get_reject_notifications(self):
        fields = ('notification_type', 'email_address', 'source_address', 'source_arn',
                  'source_ip', 'sendingAccountId', 'send_timestamp', 'message_id', 'subject')

        return self.getAll('complaint', fields)

    def check_delivery_message_id(self, message_id):
        message_id = self.getAll("delivery", fields='*',
                                  where=('message_id=%s', [message_id]))

        if message_id and len(message_id) > 0:
            return True
        return False

    def check_bounce_message_id(self, message_id):
        message_id = self.getAll("bounce", fields='*',
                                  where=('message_id=%s', [message_id]))

        if message_id and len(message_id) > 0:
            return True
        return False

    def check_complaint_message_id(self, message_id):
        message_id = self.getAll("complaint", fields='*',
                                  where=('message_id=%s', [message_id]))

        if message_id and len(message_id) > 0:
            return True
        return False

    def get_bounce_emails(self):
        fields = ('email_address', 'subject')
        return self.getAll('bounce', fields)

