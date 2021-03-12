from .database import Database


class CampaignWinningHelper(Database):

    def __init__(self, *args):
        super(CampaignWinningHelper, self).__init__(*args)

    def create_campaign_winning_combination(self, campaign_id, rate, time_after, time_type):

        data = {"campaign_id": campaign_id, "rate": rate, "time_after": time_after, "time_type": time_type}
        return self.insert("campaigns_winning_combination", data)

        # query = "INSERT INTO campaigns_winning_combination(campaign_id, rate, time_after, time_type) " \
        #         "VALUE (%s, %s, %s, %s)"
        # return self.add(query, (campaign_id, rate, time_after, time_type))

    def get_all_combinations(self, campaign_id):
        fields = ('rate', 'time_after', 'time_type')
        where = ("campaign_id=%s", [campaign_id])
        return self.getOne('campaigns', fields=fields, where=where)

        # query = "SELECT rate, time_after, time_type FROM campaigns_winning_combination " \
        #         "WHERE campaign_id=%s" % campaign_id
        # return self.fetch_one(query)

    def update_campaign_winning_combination(self, rate, time_after, time_type, campaign_id):
        data = {"rate": rate, "time_after": time_after, "time_type": time_type}
        where = ('campaign_id = %s', [campaign_id])
        self.update("campaigns_winning_combination", data=data, where=where)

        # query = "UPDATE campaigns_winning_combination SET rate = '%s', " \
        #         "time_after = %s, time_type = '%s' WHERE campaign_id=%s" % \
        #         (rate, time_after, time_type, campaign_id)
        #
        # self.update_email_config(query)

