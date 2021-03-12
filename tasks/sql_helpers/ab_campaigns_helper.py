from .database import Database


class AbCampaignsHelper(Database):

    def __init__(self, *args):
        super(AbCampaignsHelper, self).__init__(*args)

    def create_ab_campaigns_parent(self, campaign_name, list_id, user_id,
                                   campaign_type, percentage=None,
                            rate=None, time_after=None, time_type=None, ab_campaign_count=None):
        data = {"name": campaign_name, "list_id": list_id,
                "user_id": user_id, "campaign_type": campaign_type,
                "test_percentage": percentage,
                "rate": rate, "time_after": time_after,
                "time_type": time_type, "ab_campaign_count": ab_campaign_count}
        sql_cursor = self.insert("ab_campaigns_parent", data=data)
        return sql_cursor

    def get_ab_parent_campaign(self, id):
        fields = {'id', 'list_id', 'name', 'ab_campaign_count'}
        where = ('id = %s', [id])
        return self.getOne('ab_campaigns_parent', fields=fields, where=where)

    def update_ab_winning_cambination(self, campaign_id, percentage, rate,
                                      time_after, time_type, campaign_count):
        data = {'test_percentage': percentage, 'rate': rate,
                'time_after': time_after, 'time_type': time_type,
                "ab_campaign_count": campaign_count}
        where = ('id = %s', [campaign_id])
        self.update('ab_campaigns_parent', data=data, where=where)

    def create_ab_campaigns(self, ab_campaign_parent_id, user_id,
                            email_subject, preview_text, status, campaign_state,
                            templates_id=None, send_time=None):

        data = {"ab_campaign_parent_id": ab_campaign_parent_id,
                "user_id": user_id, "status": status,
                "campaign_state": campaign_state, "email_subject": email_subject,
                "preview_text": preview_text, "templates_id": templates_id,
                "send_time": send_time}
        sql_cursor = self.insert('ab_campaigns', data=data)
        return sql_cursor

    def get_ab_campagin_by_id(self, id):
        fields = {"id", "ab_campaign_parent_id", "user_id", "email_subject",
                  "preview_text", "templates_id", "send_time", "status", "campaign_state"}
        where = ('ab_campaign_parent_id = %s', [id])
        return self.getAll('ab_campaigns', fields=fields, where=where)

    def update_ab_campaign_template(self, id, templates_id):
        data = {'templates_id': templates_id}
        where = ('id = %s', [id])
        self.update('ab_campaigns', data=data, where=where)

    def update_ab_send_time(self, id, send_time, state):
        data = {'send_time': send_time, 'campaign_state': state}
        where = ('id = %s', [id])
        self.update('ab_campaigns', data=data, where=where)

    def check_if_campaign_already_exist(self, campaign_id):
        fields = ('id', 'email_subject')
        where = ('ab_campaign_parent_id=%s', [campaign_id])
        response = self.getAll('ab_campaigns', fields=fields, where=where)
        if response:
            return True
        return False

    def get_all_ab_campaign(self):
        query = "select ab_parent.id, ab_parent.name, ab_parent.list_id, " \
                "ab_parent.ab_campaign_count, ab.send_time, ab_parent.test_percentage," \
                "ab_parent.campaign_type, ab.email_subject, ab.templates_id, " \
                "ab.preview_text, ab.send_time, ab.campaign_state, ab.status " \
                "from ab_campaigns_parent ab_parent inner join ab_campaigns ab " \
                "on ab_parent.id = ab.ab_campaign_parent_id " \
                "where (ab.status='ACTIVE' or ab.status='PROCESSING')and ab.campaign_state='PUBLISHED'"
        return self.query(query)

    # def get_all_ab_campaign(self):
    #     fields = {''}
    #     where = ()
    #     return self.getAll('ab_campaigns_parent', fields=fields, where=where)

    # def get_ab_campaigns(self):
    #     query = "select ab.id, ab_parent.name, ab_parent.list_id, " \
    #             "ab_parent.campaign_type, ab.email_subject, ab.templates_id, " \
    #             "ab.preview_text, ab.send_time, ab.campaign_state, ab.status " \
    #             "from ab_campaigns_parent ab_parent inner join ab_campaigns ab " \
    #             "on ab_parent.id = ab.ab_campaign_parent_id " \
    #             "where (ab.status='ACTIVE' or ab.status='PROCESSING')and ab.campaign_state='PUBLISHED'"
    #     return self.query(query)

    def update_email_configration_status(self, id, status):
        data = {"status": status}
        where = ('id = %s', [id])
        self.update("ab_campaigns", data, where)

    def update_parenet_campaign_status(self, id, status):
        data = {"status": status}
        where = ('id = %s', [id])
        self.update("ab_campaigns_parent", data, where)

    def update_email_configration_queued_time(self, id, status, queued_time):
        data = {"status": status, 'queued_time': queued_time}
        where = ('id = %s', [id])
        self.update("ab_campaigns_parent", data, where)

    def get_email_configurations_processing(self):
        query = "select ab.id, ab_parent.list_id, ab.templates_id, ab.status, ab_parent.name, " \
                "ab.created_on, ab_parent.campaign_type, ab.email_subject, ab.ab_campaign_parent_id  " \
                "from ab_campaigns_parent ab_parent inner join ab_campaigns ab " \
                "on ab_parent.id = ab.ab_campaign_parent_id where ab.status='QUEUED' and ab_parent.status='QUEUED'"
        return self.query(query)
