from .database import Database


class AbCampaignsHelper(Database):

    def __init__(self, *args):
        super(AbCampaignsHelper, self).__init__(*args)

    def create_ab_campaigns_parent(self, campaign_name, list_id,
                                   user_id, campaign_type,
                                   status, type,
                                   percentage=None,
                                   rate=None, time_after=None,
                                   time_type=None, ab_campaign_count=None):
        data = {"name": campaign_name, "list_id": list_id,
                "user_id": user_id, "campaign_type": campaign_type,
                "status": status, 'type': type,
                "test_percentage": percentage,
                "rate": rate, "time_after": time_after,
                "time_type": time_type, "ab_campaign_count": ab_campaign_count}
        sql_cursor = self.insert("ab_campaigns_parent", data=data)
        return sql_cursor

    def get_ab_parent_campaign(self, id):
        fields = {'id', 'list_id', 'name', 'ab_campaign_count', 'test_variable', 
                  'test_percentage', 'rate', 'time_type', 'time_after',
                  'type', 'campaign_type'}
        where = ('id = %s', [id])
        return self.getOne('ab_campaigns_parent', fields=fields, where=where)

    def get_ab_parent_campaigns(self, id, params):
        fields = {'id', 'list_id', 'name', 'ab_campaign_count',
                  'test_percentage', 'rate', 'time_type', 'time_after',
                  'type', 'campaign_type', 'test_variable', 'queued_time', 'campaign_state'}
        where = ("id = %s and campaign_type = %s", [id, params])
        return self.getOne('ab_campaigns_parent', fields=fields, where=where)

    def update_ab_parent_campaign(self, campaign_id,
                                  campaign_name,
                                  list_id):
        data = {'name': campaign_name, 'list_id': list_id}
        where = ('id = %s', [campaign_id])
        self.update('ab_campaigns_parent', data=data, where=where)

    def update_ab_winning_cambination(self, campaign_id, percentage,
                                      test_variable, rate,
                                      time_after, time_type, campaign_count):
        data = {'test_percentage': percentage,
                'test_variable': test_variable, 'rate': rate,
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
                  "preview_text", "templates_id", "send_time"}
        where = ('ab_campaign_parent_id = %s', [id])
        return self.getAll('ab_campaigns', fields=fields, where=where)

    def get_ab_send_emails(self, campaign_id):
        query = "select ab_campaign_id, email_address from email_management_db.ready_to_send_emails " \
                "where ab_campaign_id = {} and status = %s".format(campaign_id, 'SENT')
        return self.query(query)

    def update_parent_status(self, campaign_state, id):
        data = {'campaign_state': campaign_state}
        where = ('id = %s', [id])
        self.update('ab_campaigns_parent', data=data, where=where)

    def update_parent_campaign_status(self, id, status):
        data = {'status': status}
        where = ('id = %s', [id])
        self.update('ab_campaigns_parent', data=data, where=where)

    def update_ab_emails_subjects(self, id, email_subject, preview_text):
        data = {'email_subject': email_subject, 'preview_text': preview_text}
        where = ('id = %s', [id])
        self.update('ab_campaigns', data=data, where=where)

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
        return response
        # if response:
        #     return True
        # return False

    def update_parnet_campaign(self, list_id, campaign_name, campaign_id, campaign_type):
        data = {'name': campaign_name, 'list_id': list_id,
                'campaign_type': campaign_type}
        where = ('id = %s', [campaign_id])
        self.update('ab_campaigns_parent', data=data, where=where)

    def get_parent_by_ab_campaign_id(self, id):
        query = 'select ab.id, ab_parent.name, ab_parent.list_id, ab_parent.campaign_type, ' \
                'ab_parent.ab_campaign_count, ab.email_subject, ab.preview_text ' \
                'from ab_campaigns ab inner join ab_campaigns_parent ab_parent ' \
                'on ab.ab_campaign_parent_id = ab_parent.id where ab_parent.id={}'.format(id)
        return self.query(query)

    def get_parnet_by_id(self, id):
        fields = {'id', 'name', 'list_id', 'campaign_type', 'status',
                  'campaign_state', 'campaign_type'}
        where = ('id = %s', [id])
        return self.getOne('ab_campaigns_parent', fields=fields, where=where)
    # def get_all_ab_campaign(self):
    #     query = "select ab_parent.id, ab_parent.name, ab_parent.list_id, " \
    #             "ab_parent.campaign_type, ab.email_subject, ab.templates_id, " \
    #             "ab.preview_text, ab.send_time, ab.campaign_state, ab.status " \
    #             "from ab_campaigns_parent ab_parent inner join ab_campaigns ab " \
    #             "on ab_parent.id = ab.ab_campaign_parent_id"
    #     return self.query(query)

    def get_all_ab_campaign(self):
        fields = {'id', 'campaign_state', 'campaign_type',
                  'name', 'status', 'list_id', 'ab_campaign_count', 'test_percentage'}
        where = ("(campaign_state = %s or campaign_state = %s) "
                 "and (status = %s or status = %s or "
                 "status = %s or status = %s or status = %s)", ['PUBLISHED', 'DRAFT',
                                                                'ACTIVE', 'PROCESSING',
                                                                'QUEUED', 'PROCESSED',
                                                                'PAUSE'])
        order = ('id', 'DESC')
        return self.getAll('ab_campaigns_parent', fields=fields, where=where, order=order)

    def get_last_record(self):
        fields = ('id', 'name', 'list_id', 'test_percentage',
                  'rate', 'time_after', 'time_type', 'ab_campaign_count', 'test_variable', 'queued_time')
        where = ('campaign_state = %s', ['PUBLISHED'])
        order = ['id', 'DESC']
        last_record = self.getOne('ab_campaigns_parent', fields=fields,
                                  where=where, order=order)
        return last_record

    def get_email_configurations_processing(self):
        query = "select ab.id, ab_parent.list_id, ab.templates_id, ab.status, ab_parent.name, " \
                "ab.created_on, ab_parent.campaign_type, ab.email_subject" \
                "from ab_campaigns_parent ab_parent inner join ab_campaigns ab" \
                "on ab_parent.id = ab.ab_campaign_parent_id where status='QUEUED'"
        return query

    def delete_ab_campaigns(self, id):
        where = ('id = %s', [id])
        self.delete('ab_campaigns_parent', where=where)

    def get_status_by_id(self, campaign_id):
        fields = {'id', 'status'}
        where = ("id = %s", [campaign_id])

        get_campaign_data = self.getOne('ab_campaigns_parent', fields=fields, where=where)
        get_status = get_campaign_data['status']
        if get_status == 'PROCESSED':
            return True
        return False

    def get_all_combinations(self, campaign_id):
        fields = ('rate', 'time_after', 'time_type')
        where = ("id=%s", [campaign_id])
        return self.getOne('ab_campaigns_parent', fields=fields, where=where)
