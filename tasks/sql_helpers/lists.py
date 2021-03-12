from .database import Database


class Lists(Database):

    def __init__(self, *args):
        super(Lists, self).__init__(*args)

    def create_list(self, list_name, user_id):
        data = {'list_name': list_name, 'user_id': user_id}
        self.insert('list', data=data)

    def get_list_segment_by_listid(self, list_id):
        fields = ('id', 'email')
        where = ("list_id = %s LIMIT 100", [list_id])
        return self.getAll('list_segments', fields=fields, where=where)

    def get_segments_mails_by_campaing_id(self, campaign_id):
        sql = "SELECT cp.id from list_segments ls inner join campaigns cp " \
                "on cp.list_id = ls.list_id where cp.id = %s"
        return self.query(sql, [campaign_id])
