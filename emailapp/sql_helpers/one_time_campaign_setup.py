from .database import Database


class OneTimeCampaignSetupHelper(Database):

    def __init__(self, *args):
        super(OneTimeCampaignSetupHelper, self).__init__(*args)

    def create_one_time_campaign_setup(self, campaign_name, user_id, list_id,
                                       segment_id, campaign_type):
        data = {"campaign_name": campaign_name, "user_id": user_id,
                "list_id": list_id, "segment_id": segment_id,
                "campaign_type": campaign_type}
        one_time_campaign_id = self.insert('one_time_campaign_setup', data)
        return one_time_campaign_id

    def get_campaigns(self, campaign_type):
        fields = ('id', 'campaign_name', 'user_id', 'list_id', 'campaign_type')
        where = ('campaign_type = %s', [campaign_type])
        one_time_campaign = self.getAll('one_time_campaign_setup', fields=fields, where=where)
        return one_time_campaign

    def get_all_campaigns(self):
        fields = ('id', 'campaign_name', 'user_id', 'list_id', 'campaign_type')
        all_campaign = self.getAll('one_time_campaign_setup', fields=fields)
        return all_campaign