from .database import Database


class Templates(Database):

    def __init__(self, *args):
        super(Templates, self).__init__(*args)

    def get_templates(self):
        fields = ('id', 'name', 'path')
        where = ("system_template=%s", ['false'])
        return self.getAll("templates", fields, where)

        # query = "SELECT id, name, path FROM templates WHERE system_template='false'"
        # return self.fetch_all(query)

    def get_template_by_id(self, template_id):
        fields = ('path', 'name', 'id')
        where = ('id=%s', [template_id])
        return self.getOne("templates", fields, where)
        # query = "SELECT path, name, id FROM templates WHERE id = '%s'" % template_id
        # return self.fetch_one(query)

    def get_template_vars_by_template_id(self, template_id):
        fields = ('template_key', 'template_value')
        where = ('templates_id=%s', [template_id])
        return self.getAll("templatevars", fields, where)
        # query = "SELECT template_key, template_value FROM templatevars " \
        #         "where templates_id=%s" % template_id
        # return self.fetch_all(query)

    def get_template_by_name(self, template_name):
        fields = ('path', 'name', 'id')
        where = ('name=%s', [template_name])
        return self.getOne("templates", fields, where)
        # query = "SELECT id FROM templates WHERE name = '%s'" % str(template_name)
        # return self.fetch_one(query)



