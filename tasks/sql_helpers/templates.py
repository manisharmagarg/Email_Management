from .database import Database


class Templates(Database):

    def __init__(self, *args):
        super(Templates, self).__init__(*args)

    def get_template_by_id(self, template_id):
        fields = ('id','path')
        where = ("id = '%s'", [template_id])
        return self.getOne('templates', fields=fields, where=where)

    def get_template_vars_by_template_id(self, template_id):
        fields = ('template_key', 'template_value')
        where = ("templates_id=%s", [template_id])
        return self.getAll('templatevars', fields=fields, where=where)
