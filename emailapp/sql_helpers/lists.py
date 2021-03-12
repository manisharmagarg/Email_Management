from .database import Database

class Lists(Database):

    def __init__(self, *args):
        super(Lists, self).__init__(*args)

    def create_list(self, list_name, user_id):
        data = {"list_name": list_name, "user_id": user_id}
        list_id = self.insert("list", data)
        return list_id
        # query = "INSERT INTO list(list_name, user_id) VALUE (%s, %s)"
        # list_id = self.add(query, (list_name, user_id))

    def get_list(self, user_id):
        fields = ('id', 'list_name', 'user_id', 'created_on')
        where = ('user_id=%s', [user_id])
        return self.getAll("list", fields, where)
        # query = "SELECT id, list_name, user_id, created_on FROM list where user_id=%s" % user_id
        # return self.fetch_all(query)

    def get_list_segment(self):
        fields = ('id', 'email', 'list_id', 'user_id', 'created_on')
        return self.getAll("list_segments", fields)

        # query = "SELECT * FROM list_segments"
        # return self.fetch_all(query)

    def get_listsegment_count(self, id):
        data = self.getAll("list_segments", fields='*', where=('list_id=%s', [id]))
        count_data = []
        for id in data:
            values = id['id']
            count_data.append(values)
        # query = "SELECT COUNT(*) FROM list_segments WHERE list_id = '%s'" % id
        # query_data = self.fetch_one(query)
        # return query_data[0]
        return len(count_data)

    def delete_list(self, id):
        list = self.get_list_by_id(id)
        if list:
            self.delete("list", where=('id = %s', [id]))
            self.delete("list_segments", where=('list_id = %s', [id]))

            # query = "DELETE FROM list WHERE id = '%s'" % id
            # segment_query = "DELETE FROM list_segments WHERE list_id = '%s'" % id
            # self.delete_record(query)
            # self.delete_record(segment_query)

    def delete_listsegment(self, id):
        self.delete("list_segments", where=('id=%s', [id]))
        # query = "DELETE FROM list_segments WHERE id = '%s'" % id
        # self.delete_record(query)

    def delete_segments(self, id):
        self.delete("list", where=('id=%s', [id]))
        self.delete("list_segments", where=('list_id=%s', [id]))

        # list_query = "DELETE FROM list WHERE id = '%s'" % id
        # list_segment_query = "DELETE FROM list_segments WHERE list_id = '%s'" % id
        # self.delete_record(list_query)
        # self.delete_record(list_segment_query)

    def get_list_segment_by_listid(self, list_id):
        fields = ('id', 'email', 'list_id', 'user_id', 'created_on')
        where = ('list_id = %s', [list_id])
        return self.getAll("list_segments", fields, where)

    def get_list_name_by_listid(self, list_id):
        fields = ('id', 'list_name')
        where = ('id = %s', [list_id])
        return self.getOne("list", fields, where)

        # query = "SELECT id, email, list_id, user_id, created_on " \
        #         "FROM list_segments WHERE list_id = %s" % list_id
        # return self.fetch_all(query)

    def get_list_by_id(self, id, user_id):
        fields = ('id', 'list_name', 'user_id', 'created_on')
        where = ('id=%s and user_id=%s', [id, user_id])
        return self.getOne("list", fields, where)

        # query = "SELECT id, list_name, user_id, created_on " \
        #         "FROM list WHERE id = '%s' and user_id=%s" % (id, user_id)
        # return self.fetch_one(query)

    # def get_list_by_listname_user_id(self, list_name, user_id):
    #     query = "SELECT * FROM list WHERE list_name = '%s' and user_id=%s" % (list_name, user_id)
    #     return self.fetch_one(query)

    def update_segment_name_by_id(self, name, list_id):
        data = {'list_name': name}
        where = ('id=%s', [list_id])
        self.update("list", data, where)

        # query = "Update list set list_name=%s where id=%s"
        # self.add(query, (str(name), list_id))

    def add_list_by_id(self, email, list_id):
        data = {"email": email, "list_id": list_id}
        return self.insert("list_segments", data)

        # query = "INSERT INTO list_segments (email, list_id) VALUE (%s, %s)"
        # return self.add(query, (str(email), list_id))

    def check_exist_emails(self, email, list_id):
        return self.getOne("list_segments", fields=('email', 'id'),
                           where=('email = %s and list_id = %s', [email, list_id]))

        # query = "SELECT email FROM list_segments WHERE email = '%s' and list_id = '%s'" % (email, list_id)
        # return self.fetch_all(query)

    def check_first_insert_data(self, emails, list_id):
        data = {"email": emails, "list_id": list_id}
        where = ('email = %s', [emails])
        segment_id = self.insert("list_segments", data, where)

        # query = "INSERT INTO  list_segments (email, list_id) VALUE (%s, %s) " \
        #         "WHERE NOT EXISTS (SELECT email FROM list_segments WHERE email = %s)"
        # segment_id = self.add(query, (emails, list_id, emails))
        return segment_id

    def get_email_by_segment_id(self, segment_id):
        fields = ('email', 'id')
        where = ('id = %s', [segment_id])
        return self.getAll("list_segments", fields, where)

        # query = "SELECT email FROM list_segments WHERE id = %s" % (segment_id)
        # return self.fetch_all(query)

    def get_listsegment_open_by_list_id(self, list_id):
        # query = "select cs.open, cs.click, ls.email, ls.list_id from " \
        #         "campaign_stats cs inner join list_segments ls on cs.segment_id = ls.id where " \
        #         "ls.list_id= {}".format(list_id)

        query = "SELECT GROUP_CONCAT( cs.open ) FROM campaign_stats cs inner join "\
                "list_segments ls on cs.segment_id = ls.id where ls.list_id={} and cs.open!=0 GROUP BY segment_id " \
                "HAVING ( COUNT(segment_id) >= 1 )".format(list_id)
        return self.query(query)

    def get_listsegment_clicks_by_list_id(self, list_id):
        query = "SELECT GROUP_CONCAT( cs.click ) FROM campaign_stats cs inner join "\
                "list_segments ls on cs.segment_id = ls.id where ls.list_id={} and cs.click!=0 GROUP BY segment_id " \
                "HAVING ( COUNT(segment_id) >= 1 )".format(list_id)
        return self.query(query)

    def get_emails_by_listid(self, list_id):
        fields = ('email', 'id')
        where = ('list_id = %s', [list_id])
        return self.getAll("list_segments", fields, where)

