from .database import Database


class CampaignStatsHelper(Database):

    def __init__(self, *args):
        super(CampaignStatsHelper, self).__init__(*args)

    def add_campaign_open_stats(self, email_result_id):
        data = {"email_result_id": email_result_id, "opened": True}
        sql_cursor = self.insert("unsubscribe", data)
        return sql_cursor
