from .database import Database


class EmailResultHelper(Database):

    def __init__(self, *args):
        super(EmailResultHelper, self).__init__(*args)

    def create_email_result(self, list_id, list_segment_id, templates_id, result,
                            result_description, campaign_id=None,
                            ab_campaign_id=None):
        data = {"campaign_id": campaign_id, "ab_campaign_id": ab_campaign_id, "list_id": list_id,
                "list_segment_id": list_segment_id, "templates_id": templates_id,
                "result": result, "result_description": result_description}
        sql_cursor = self.insert("email_results", data)
        return sql_cursor

    def create_ab_email_result(self, ab_campaign_id, list_id, list_segment_id, templates_id, result, result_description):
        data = {"ab_campaign_id": ab_campaign_id, "list_id": list_id,
                "list_segment_id": list_segment_id, "templates_id": templates_id,
                "result": result, "result_description": result_description}
        sql_cursor = self.insert("email_results", data)
        return sql_cursor

    # def get_email_result_by_campaign_segment_id(self, segment_id, campaign_id):
    #     query = "Select id, list_id from email_results where list_segment_id=%s" \
    #                      " and campaign_id=%s" % (segment_id, campaign_id)
    #
    #     return self.fetch_all(query)

    def check_if_all_emails_processed_for_campaign(self, campaign_id):
        fields = ('id', 'list_id')
        where = ("(result='SENT' or result='ERROR') and campaign_id=%s", [campaign_id])
        return self.getAll('email_results', fields=fields, where=where)

    def check_if_all_emails_processed_for_ab_campaign(self, campaign_id):
        fields = ('id', 'list_id')
        where = ("(result='SENT' or result='ERROR') and ab_campaign_id=%s", [campaign_id])
        return self.getAll('email_results', fields=fields, where=where)

    # def get_email_results_by_campaign_id(self, campaign_id):
    #     query = "Select em.id, em.list_id, em.list_segment_id, em.templates_id, em.result, em.result_description, " \
    #             "ls.list_name, lsg.email from email_results em" \
    #             " inner join list ls on ls.id=em.list_id" \
    #             " inner join list_segments lsg on lsg.id=em.list_segment_id" \
    #             " where campaign_id=%s" % (campaign_id)
    #
    #     return self.fetch_all(query)

    # def check_is_email_already_sent(self, list_segment_id, campaign_id):
    #     query = "Select * from email_results where list_segment_id=%s and campaign_id=%s" \
    #             % (list_segment_id, campaign_id)
    #
    #     emails_sent = self.fetch_all(query)
    #     if emails_sent and len(emails_sent) > 0:
    #         return True
    #     return False
