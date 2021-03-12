from .database import Database


class CampaignSetupHelper(Database):

    def __init__(self, *args):
        super(CampaignSetupHelper, self).__init__(*args)

    def create_campaign_setup(self, campaign_name, user_id, segment_id, status, state,
                              list_id=None, campaign_type=None,
                              email_subject=None, preview_text_subject=None,
                              template_id=None, send_time=None):
        data = {"campaign_name": campaign_name, "user_id": user_id,
                "segment_id": segment_id, "list_id": list_id,
                "status": status, "campaign_state": state,
                "campaign_type": campaign_type, "email_subject": email_subject,
                "preview_text_subject": preview_text_subject,
                "template_id": template_id, "send_time": send_time}
        one_time_campaign_id = self.insert('campaign_setup', data)
        return one_time_campaign_id

    def get_lastId(self):
        return self.lastId()

    def update_campaign_setup(self, campaign_id, email_subject, preview_text_subject):
        data = {"email_subject": email_subject, "preview_text_subject": preview_text_subject}
        where = ('id = %s', [campaign_id])
        self.update("campaign_setup", data, where)

    def update_template(self, campaign_id, template_id):
        data = {"template_id": template_id}
        where = ('id = %s', [campaign_id])
        self.update("campaign_setup", data, where)

    def update_send_time(self, campaign_id, send_time):
        data = {"send_time": send_time}
        where = ('id = %s', [campaign_id])
        self.update("campaign_setup", data, where)

    def get_last_record(self, campaign_type):
        fields = ('id', 'campaign_name')
        where = ('campaign_type = %s', [campaign_type])
        order = ['id', 'DESC']
        last_record = self.getOne('campaign_setup', fields=fields,
                                  where=where, order=order)
        return last_record

    def get_all_campaigns(self):
        fields = ('id, campaign_name', 'status', 'campaign_state', 'campaign_type',
                  'email_subject', 'preview_text_subject')
        return self.getAll('campaign_setup', fields)

    def get_campaigns(self, campaign_type):

        fields = ('campaign_name', 'status', 'campaign_state', 'campaign_type',
                  'email_subject', 'preview_text_subject', 'campaign_type')
        where = ('campaign_type = %s', [campaign_type])
        return self.getAll('campaign_setup', fields=fields, where=where)

