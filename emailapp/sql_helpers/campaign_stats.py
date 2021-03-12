from .database import Database


class CampaignStatsHelper(Database):

    def __init__(self, *args):
        super(CampaignStatsHelper, self).__init__(*args)

    def add_campaign_open_stats(self, segment_id, template_id,
                                open, click, full_url, IPAddress,
                                campaign_id=None, ab_campaign_id=None):
        data = {'campaign_id': campaign_id, 'ab_campaign_id': ab_campaign_id,
                'segment_id': segment_id, 'template_id': template_id,
                'open': open, 'click': click, 'url': full_url, 'IPAddress': IPAddress}
        self.insert("campaign_stats", data)

    def add_campaign_click_stats(self, segment_id, template_id,
                                 open, click, full_url, campaign_id=None, ab_campaign_id=None):
        data = {'campaign_id': campaign_id, 'ab_campaign_id': ab_campaign_id,
                'segment_id': segment_id, 'template_id': template_id,
                'open': open, 'click': click, 'url': full_url}
        self.insert("campaign_stats", data)

    def get_campaign_stats(self, campaign_id):
        query = "SELECT cs.id, cs.campaign_id, cs.segment_id, cs.template_id, " \
                "cs.open, cs.click, cs.url, cs.created_on," \
                " ls.email, l.id, l.list_name, t.name, cs.IPAddress FROM campaign_stats cs" \
                " inner join list_segments ls on ls.id=cs.segment_id" \
                " inner join list l on l.id=ls.list_id" \
                " inner join templates t on t.id=cs.template_id" \
                " WHERE campaign_id=%s"

        return self.query(query, [campaign_id])

    def get_open_click_rate_by_date_and_campaign(self, date):
        fields = ('id', 'click', 'open', 'created_on')
        where = ('DATE(created_on) = %s', [date])

        return self.getAll('campaign_stats', fields, where)

    def get_open_click_rate_by_date_and_campaign_id(self, date, id):
        fields = ('id', 'click', 'open', 'created_on', 'campaign_id')
        where = ('DATE(created_on) = %s and campaign_id = %s', [date, id])

        return self.getAll('campaign_stats', fields, where)

    def get_ab_open_click_rate_by_date_and_campaign_id(self, date, id):
        fields = ('id', 'click', 'open', 'created_on', 'ab_campaign_id')
        where = ('DATE(created_on) = %s and ab_campaign_id = %s', [date, id])

        return self.getAll('campaign_stats', fields, where)

    def get_open_click_rate_by_campaign_id(self, id):
        query = "SELECT count(CASE WHEN open LIKE '%1%' THEN 1 END) AS open, " \
                "count(CASE WHEN click LIKE '%1%' THEN 1 END) AS click " \
                "FROM campaign_stats where campaign_id = {}".format(id)
        return self.query(query)

    def get_open_click_rate_by_ab_campaign_id(self, id):
        query = "SELECT count(CASE WHEN open LIKE '%1%' THEN 1 END) AS open, " \
                "count(CASE WHEN click LIKE '%1%' THEN 1 END) AS click " \
                    "FROM campaign_stats where ab_campaign_id = {}".format(id)
        return self.query(query)


    def get_unique_open(self, campaign_id):
        query = "SELECT segment_id, campaign_id, open from campaign_stats" \
                " group by segment_id, campaign_id, open Having open=1 and campaign_id=%s "

        return self.query(query, [campaign_id])

    def get_all_open_click(self):
        fields = ('id', 'click', 'open', 'created_on')
        return self.getAll("campaign_stats", fields=fields)

    def get_ab_campaign_stats(self, ab_campaign_id):
        # fields = {'open', 'click', 'ab_campaign_id'}
        # where = ('ab_campaign_id = %s', [ab_campaign_id])
        # return self.getAll('campaign_stats', fields=fields, where=where)
        query = "SELECT count(CASE WHEN open LIKE '%1%' THEN 1 END) AS open, " \
                "count(CASE WHEN click LIKE '%1%' THEN 1 END) AS click " \
                "FROM campaign_stats where ab_campaign_id = {}".format(ab_campaign_id)
        return self.query(query)
