from .database import Database


class CampaignHelper(Database):

    def __init__(self, *args):
        super(CampaignHelper, self).__init__(*args)

    def get_email_configurations(self, is_ab_campaign=False):
        fields = ('id', 'list_id', 'templates_id', 'status', 'name', 'email_subject', 'campaign_type', 'send_time', 'created_on')
        where = ("(status='ACTIVE' or status='PROCESSING') "
                 "and is_ab_campaign=%s and campaign_state='PUBLISHED'", [is_ab_campaign])
        return self.getAll('campaigns', fields=fields, where=where)

    def get_ab_campaigns(self):
        fields = ('id', 'list_id', 'templates_id', 'status', 'name', 'email_subject', 'created_on')
        where = ("(status='ACTIVE' or status='PROCESSING')and campaign_state='PUBLISHED'"
                 "and is_ab_campaign=%s and parent_campaign_id is null", [True])
        return self.getAll('campaigns', fields=fields, where=where)

    def get_email_configurations_processing(self, is_ab_campaign=False):
        fields = ('id', 'list_id', 'templates_id', 'status', 'name', 'created_on', 'is_ab_campaign')
        where = ("status='QUEUED' and is_ab_campaign=%s", [is_ab_campaign])
        return self.getAll('campaigns', fields=fields, where=where)

    def update_email_configration_status(self, id, status):
        data = {"status": status}
        where = ('id = %s', [id])
        self.update("campaigns", data, where)

    def update_email_configration_queued_time(self, id, status, queued_time):
        data = {"status": status, 'queued_time': queued_time}
        where = ('id = %s', [id])
        self.update("campaigns", data, where)

    def check_if_campaign_already_processing(self, campaign_id):
        fields = ('id', 'name')
        where = ("id=%s and (status='QUEUED')", [campaign_id])
        response = self.getOne('campaigns', fields=fields, where=where)
        if response:
            return True
        return False

    def get_test_percentage(self, campaign_id):
        fields = ('test_percentage', 'id')
        where = ("id = %s ", [campaign_id])
        return self.getOne('campaigns', fields=fields, where=where)

    def get_campaign_by_parent_id(self, campaign_id):
        fields = ('id', 'name', 'email_subject')
        where = ("parent_campaign_id = %s", [campaign_id])
        return self.getAll('campaigns', fields=fields, where=where)
