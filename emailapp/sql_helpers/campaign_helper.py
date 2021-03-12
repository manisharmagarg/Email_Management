from .database import Database


class CampaignHelper(Database):

    def __init__(self, *args):
        super(CampaignHelper, self).__init__(*args)
    #
    # def create_campaign(self, name, templates_id, status, user_id, state,
    #                     percentage, list_id=None, campaign_type=None,
    #                     is_ab_campaign=False, parent_campaign_id=None):

    def create_campaign(self, name, status, type,
                        user_id, templates_id=None,
                        campaign_type=None,
                        list_id=None, send_time=None,
                        email_subject=None, preview_text=None,
                        percentage=None, is_ab_campaign=False,
                        parent_campaign_id=None):
        data = {"name": name, "list_id": list_id, "templates_id": templates_id,
                "status": str(status), "user_id": user_id, 'type': type,
                "parent_campaign_id": parent_campaign_id, "email_subject": email_subject,
                "preview_text": preview_text, "send_time": send_time,
                "is_ab_campaign": is_ab_campaign, "test_percentage": percentage, "campaign_type": campaign_type}
        sql_cursor = self.insert("campaigns", data)
        return sql_cursor

        # query = "INSERT INTO campaigns(name, list_id, templates_id, status, user_id, " \
        #         "campaign_state, parent_campaign_id, is_ab_campaign, test_percentage) " \
        #         "VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # campaign_id = self.add(query, (name, list_id, str(templates_id), str(status),
        #                                user_id, str(state), parent_campaign_id, is_ab_campaign, percentage))
        # return campaign_id
        # self.insert("campaigns", data)

    def get_lastId(self):
        return self.lastId()

    def get_last_record(self, campaign_type, is_ab_campaign=None):
        fields = ('id', 'name')
        where = ('campaign_type = %s and is_ab_campaign = %s', [campaign_type, is_ab_campaign])
        order = ['id', 'DESC']
        last_record = self.getOne('campaigns', fields=fields,
                                  where=where, order=order)
        return last_record

    def get_latest_campaign(self):

        fields = ('id', 'list_id', 'templates_id', 'status', 'created_on', 'name')
        where = ('is_ab_campaign = %s', [False])
        campaigns = self.getAll("campaigns", fields, where, ['id', 'desc'])
        if campaigns:
            return campaigns[0]
        return None

    def get_campaign_by_id(self, id):
        fields = ('id', 'list_id', 'templates_id', 'status', 'created_on',
                  'name', 'parent_campaign_id', 'test_percentage',
                  'is_ab_campaign', 'campaign_type', 'name', 'email_subject',
                  'preview_text', 'campaign_state', 'type', 'send_time')

        where = ("id = %s and campaign_type = 'One-time'", [id])
        return self.getOne("campaigns", fields, where)

    def get_campaign_by_id_and_status(self, id, params):
        fields = ('id', 'list_id', 'templates_id', 'status', 'created_on',
                  'name', 'parent_campaign_id', 'test_percentage',
                  'is_ab_campaign', 'campaign_type', 'name', 'email_subject',
                  'preview_text', 'campaign_state', 'type', 'queued_time')
        where = ("id = %s and campaign_type = %s", [id, params])
        return self.getOne("campaigns", fields, where)

    def get_one_time_campaign_by_id(self, id, params):
        fields = ('id', 'list_id', 'templates_id', 'status', 'created_on',
                  'name', 'parent_campaign_id', 'test_percentage',
                  'is_ab_campaign', 'campaign_type', 'name',
                  'email_subject', 'preview_text', )
        where = ("id = %s and campaign_type = %s", [id, params])
        return self.getOne("campaigns", fields, where)

    def get_campaign_by_parent_campaign_id(self, id):
        fields = ('id', 'list_id', 'templates_id', 'status', 'created_on', 'name', 'parent_campaign_id')
        where = ('parent_campaign_id = %s', [id])
        return self.getOne("campaigns", fields, where)

        # query = "SELECT id, list_id, templates_id, status, created_on, name, " \
        #         "parent_campaign_id FROM campaigns " \
        #         "WHERE parent_campaign_id=%s" % id
        #
        # return self.fetch_one(query)

    def get_email_configurations(self):
        fields = ('id', 'list_id', 'templates_id', 'status', 'created_on', 'name')
        where = ('status = %s and status = %s', ['ACTIVE', 'PROCESSING'])
        return self.getAll("campaigns", fields, where)

        # query = "SELECT id, list_id, templates_id, status, created_on, name FROM campaigns " \
        #         "WHERE status='ACTIVE' or status='PROCESSING'"
        # return self.fetch_all(query)

    def get_email_configurations_processing(self):
        fields = ('id', 'list_id', 'templates_id', 'status', 'created_on', 'name')
        where = ('status = %s', ['PROCESSING'])
        return self.getAll("campaigns", fields, where)

        # query = "SELECT id, list_id, templates_id, status, created_on, name FROM campaigns " \
        #         "WHERE status='PROCESSING'"
        # return self.fetch_all(query)

    def update_email_configration_status(self, id, status):
        data = {"status": status}
        where = ('id = %s', [id])
        self.update("campaigns", data, where)

        # query = "UPDATE campaigns SET status = '%s' WHERE id = '%s'" % (status, id)
        # self.update_email_config(query)

    def get_all_non_ab_campaigns(self, user_id):
        tables = ('campaigns', 'list')
        fields = (['id', 'list_id', 'name', 'status', 'campaign_state', 'created_on'],
                  ['list_name'])
        join_fields = ('list_id', 'id')
        where = ("campaigns.is_ab_campaign=%s and campaigns.user_id= %s", [False, user_id])
        order = ['id', 'DESC']
        data = self.leftJoin(tables=tables, fields=fields, join_fields=join_fields,
                             where=where, order=order, limit=None)
        return data

        # fields = ('cp.id', 'cp.list_id', 'cp.name', 'cp.status', 'cp.campaign_state',
        #           'cp.created_on', 'ls.list_name')
        #
        # where = ('is_ab_campaign=%s and cp.user_id=%s', [False, user_id])
        #
        # self.getAll("campaigns", fields, where, ['id', 'desc'])

    def get_all_ab_campaigns(self, user_id):
        tables = ('campaigns', 'list')
        fields = (['id', 'list_id', 'name', 'status', 'campaign_state', 'created_on'],
                  ['list_name'])
        join_fields = ('list_id', 'id')
        where = ("is_ab_campaign=%s and campaigns.user_id=%s and parent_campaign_id is null", [True, user_id])
        order = ['id', 'DESC']
        data = self.leftJoin(tables=tables, fields=fields, join_fields=join_fields,
                             where=where, order=order, limit=None)
        return data

        # query = "SELECT cp.id, cp.list_id, cp.name, cp.status, " \
        #         "cp.campaign_state, cp.created_on, ls.list_name FROM campaigns " \
        #         "cp left join list ls on ls.id=cp.list_id " \
        #         "where is_ab_campaign=%s and cp.user_id=%s and parent_campaign_id is null" \
        #         " order by cp.id desc" \
        #         % (True, user_id)

        # return self.fetch_all(query)

    def get_total_send_time(self, campaign_id):
        query = "SELECT TIMESTAMPDIFF(SECOND, queued_time, created_on) AS seconds FROM campaigns " \
                "where id={}".format(campaign_id)
        return self.query(query)

    def get_ab_total_send_time(self, campaign_id):
        query = "SELECT TIMESTAMPDIFF(SECOND, queued_time, created_on) AS seconds FROM ab_campaigns_parent " \
                "where id={}".format(campaign_id)
        return self.query(query)

    def update_campaign(self, list_id, campaign_name, campaign_id, campaign_type, state=None):
        data = {"list_id": list_id, "name": campaign_name, "campaign_state": state,
                "campaign_type": campaign_type}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

    def update_campaigns(self, list_id, campaign_name, campaign_id, campaign_type):
        data = {"list_id": list_id, "name": campaign_name,
                "campaign_type": campaign_type}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

        # query = "UPDATE campaigns SET list_id = '%s', name = '%s', campaign_state = '%s'
        # WHERE id = '%s'" % (list_id, campaign_name, state, campaign_id)
        # self.update_email_config(query)

    def get_campaign(self, campaign_id, user_id):
        where = ('id = %s and user_id = %s', [campaign_id, user_id])
        return self.getOne("campaigns", fields='*', where=where)

        # query = "SELECT * FROM campaigns WHERE id=%s and user_id=%s" % (campaign_id, user_id)
        # return self.fetch_one(query)

    def delete_campaign(self, id, user_id):
        campaign = self.get_campaign(id, user_id)
        if campaign:
            self.delete("campaigns", where=('id = %s and user_id = %s', [id, user_id]))
            self.delete("email_results", where=('campaign_id = %s ', [id]))

            # campaign_query = "DELETE FROM campaigns WHERE id = '%s' and user_id=%s" % (id, user_id)
            # email_result_query = "DELETE FROM email_results WHERE campaign_id = '%s'" % id
            # self.delete_record(campaign_query)
            # self.delete_record(email_result_query)

    def update_campagin_name_by_id(self, name, id):
        self.update("campaigns", data={"name": name}, where=('id = %s', [id]))

        # query = "UPDATE campaigns SET name = '%s' WHERE id = '%s'" % (name, id)
        # self.update_email_config(query)

    def update_campagin_state_by_id(self, status, campaign_id):
        data = {'campaign_state': status}
        where = ('id=%s', [campaign_id])
        self.update("campaigns", data, where)

        # query = "UPDATE campaigns SET campaign_state = '%s'WHERE id = '%s'" % (status, campaign_id)
        # self.update_email_config(query)

    def update_campagin_list_id(self, list_id, id):
        self.update("campaigns", data={"list_id": list_id}, where=('id = %s', [id]))

        # query = "UPDATE campaigns SET list_id = '%s' WHERE id = '%s'" % (list_id, id)
        # self.update_email_config(query)

    def get_queued_time(self, id):
        return self.getOne("campaigns", fields=('id', 'queued_time'), where=('id=%s ', [id]))

        # query = "SELECT queued_time FROM campaigns WHERE id=%s" % id
        # return self.fetch_one(query)

    def get_test_percentage(self, campaign_id):
        fields = ('test_percentage', 'created_on')
        where = ('id = %s', [campaign_id])
        return self.getOne("campaigns", fields, where)

        # return self.getOne("campaigns", fields='test_percentage', where=('id = %s ', [campaign_id]))

        # query = "SELECT test_percentage FROM campaigns WHERE id=%s " % campaign_id
        # return self.fetch_one(query)

    def check_is_ab_campaign(self, campaign_id):
        fields = ('is_ab_campaign', 'created_on')
        where = ('id=%s', [campaign_id])
        return self.getAll("campaigns", fields=fields, where=where)
        # query = "SELECT is_ab_campaign FROM campaigns where id=%s" % campaign_id
        # return self.fetch_all(query)

    def get_campaign_by_parent_id(self, parent_campaign_id):
        fields = ('parent_campaign_id', 'id')
        where = ('id = %s', [parent_campaign_id])
        return self.getAll("campaigns", fields, where)

        # query = "SELECT parent_campaign_id FROM campaigns " \
        #         "WHERE id=%s" % parent_campaign_id
        # return self.fetch_all(query)

    def get_campaign_id_by_parent_id(self, campaign_a_id):
        fields = ('id', 'templates_id')
        return self.getAll("campaigns", fields, where=('parent_campaign_id = %s', [campaign_a_id]))
        # query = "SELECT id, templates_id FROM campaigns " \
        #         "WHERE parent_campaign_id=%s" % campaign_a_id
        # return self.fetch_all(query)

    def update_ab_campaign(self, campaign_name, templates_id_a, list_id_a,
                           state, campaign_id=None, percentage=None):
        data = {'name': campaign_name, 'templates_id': templates_id_a, 'list_id': list_id_a,
                'campaign_state': state, 'test_percentage': percentage}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

        # query = "UPDATE campaigns SET name = '%s', templates_id = %s, " \
        #         "list_id = %s, test_percentage = '%s', campaign_state = '%s' " \
        #         "WHERE id = %s" % (campaign_name, templates_id_a, list_id_a,
        #                            percentage, state, campaign_id)
        # self.update_email_config(query)

    def update_campagin_name_and_list(self, campaign_id, campaign_name, list_id):
        data = {"name": campaign_name, "list_id": list_id}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

    def update_campaign_setup(self, campaign_id, email_subject, preview_text, campaign_state):
        data = {"email_subject": email_subject, "preview_text": preview_text,
                "campaign_state": campaign_state}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

    def update_template(self, campaign_id, template_id):
        data = {"templates_id": template_id}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

    def update_send_time(self, campaign_id, send_time, state=None):
        data = {"send_time": send_time, "campaign_state": state}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

    def get_campaigns(self):
        fields = ('id, name', 'status', 'campaign_state', 'campaign_type',
                  'email_subject', 'preview_text', 'list_id')
        where = ('(campaign_state = %s or campaign_state = %s) '
                 'and campaign_type = %s and parent_campaign_id is null', ['DRAFT', 'PUBLISHED', 'One-time'])
        order = ('id', 'DESC')
        return self.getAll('campaigns', fields, where, order)

    def get_ab_campaign_content(self, id):
        fields = ('id', 'templates_id', 'email_subject', 'preview_text', 'send_time')
        where = ('id = %s', [id])
        return self.getOne("campaigns", fields, where)

    def update_ab_test_percentage_by_id(self, percentage, state, campaign_id):
        data = {'test_percentage': percentage, 'campaign_state': state}
        where = ('id = %s', [campaign_id])
        self.update("campaigns", data, where)

    def delete_campaigns(self, id):
        where = ('id = %s', [id])
        self.delete('campaigns', where=where)

    def get_status_by_id(self, campaign_id):
        fields = {'id', 'status'}
        where = ("id = %s", [campaign_id])

        get_campaign_data =  self.getOne('campaigns', fields=fields, where=where)
        get_status = get_campaign_data['status']
        if get_status == 'PROCESSED':
            return True
        return False