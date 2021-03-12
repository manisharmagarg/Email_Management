"""
    A very simple wrapper for MySQLdb

    Methods:
        getOne() - get a single row
        getAll() - get all rows
        lastId() - get the last insert id
        lastQuery() - get the last executed query
        insert() - insert a row
        insertBatch() - Batch Insert
        insertOrUpdate() - insert a row or update it if it exists
        update() - update rows
        delete() - delete rows
        query()  - run a raw sql query
        leftJoin() - do an inner left join query and get results

    License: GNU GPLv2

    Kailash Nadh, http://nadh.in
    May 2013
"""

import MySQLdb
import MySQLdb.cursors as cursors
from collections import namedtuple
from itertools import repeat
import warnings
from conf.config import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, DBNAME, CONNECT_TIMEOUT, MYSQL_PORT
warnings.filterwarnings('error', category=MySQLdb.Warning)

from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()


class Database:
    conn = None
    cur = None
    # conf = None

    class __Database:
        def __init__(self, **args):
            kwargs = args
            self.conf = kwargs
            self.conf['user'] = kwargs.get('user', MYSQL_USER)
            self.conf['passwd'] = kwargs.get('passwd', MYSQL_PASS)
            self.conf['host'] = kwargs.get('host', MYSQL_HOST)
            self.conf['connect_timeout'] = kwargs.get('connect_timeout', CONNECT_TIMEOUT)
            self.conf['db'] = kwargs.get('db', DBNAME)
            self.conf['keep_alive'] = kwargs.get('keep_alive', False)
            self.conf['charset'] = kwargs.get('charset', 'utf8')
            self.conf['port'] = kwargs.get('port', 3306)
            self.conf['autocommit'] = kwargs.get('autocommit', False)
            self.conf['ssl'] = kwargs.get('ssl', False)
            self.connect()
        def __str__(self):
            return repr(self) + self.val

        def connect(self):

            """Connect to the mysql server"""
            try:
                if not self.conf['ssl']:
                    self.conn = MySQLdb.connect(db=self.conf['db'], host=self.conf['host'],
                                                port=self.conf['port'], user=self.conf['user'],
                                                passwd=self.conf['passwd'],
                                                charset=self.conf['charset'])

                else:
                    self.conn = MySQLdb.connect(db=self.conf['db'], host=self.conf['host'],
                                                port=self.conf['port'], user=self.conf['user'],
                                                passwd=self.conf['passwd'],
                                                ssl=self.conf['ssl'],
                                                charset=self.conf['charset'])

                self.cur = self.conn.cursor(cursors.DictCursor)
                self.conn.autocommit(self.conf['autocommit'])
            except:
                print ('MySQL connection failed')
                raise

        def getOne(self, table=None, fields='*', where=None, order=None, limit=(1,)):
            """Get a single result

                table = (str) table_name
                fields = (field1, field2 ...) list of fields to select
                where = ("parameterizedstatement", [parameters])
                        eg: ("id=%s and name=%s", [1, "test"])
                order = [field, ASC|DESC]
                limit = [limit1, limit2]
            """
            if not self.conn.open:
                self.connect()
            cur = self._select(table, fields, where, order, limit)
            result = cur.fetchone()

            if result:
                row = result
            else:
                row = None
                # Row = namedtuple("Row", [f[0] for f in cur.description])
                # row = Row(*result)

            return row

        def getAll(self, table=None, fields=None, where=None, order=None, limit=None):
            """Get all results

                table = (str) table_name
                fields = (field1, field2 ...) list of fields to select
                where = ("parameterizedstatement", [parameters])
                        eg: ("id=%s and name=%s", [1, "test"])
                order = [field, ASC|DESC]
                limit = [limit1, limit2]
            """
            if not self.conn.open:
                self.connect()
            cur = self._select(table, fields, where, order, limit)

            return list(cur)

        #       cur = self._select(table, fields, where, order, limit)
        #       result = cur.fetchall()
        #
        #       rows = None
        #
        #       if result:
        #           rows = [item for item in result]
        #
        #       return rows

        def get_all_as_set(self, table=None, fields=None, where=None, order=None, limit=None):
            """Get all results

                table = (str) table_name
                fields = (field1, field2 ...) list of fields to select
                where = ("parameterizedstatement", [parameters])
                        eg: ("id=%s and name=%s", [1, "test"])
                order = [field, ASC|DESC]
                limit = [limit1, limit2]
            """
            if not self.conn.open:
                self.connect()
            cur = self._select(table, fields, where, order, limit)

            return list(cur)

        def lastId(self):
            """Get the last insert id"""
            if not self.conn.open:
                self.connect()
            return self.cur.lastrowid

        def lastQuery(self):
            """Get the last executed query"""
            try:
                if not self.conn.open:
                    self.connect()
                return self.cur.statement
            except AttributeError:
                return self.cur._last_executed

        def leftJoin(self, tables=(), fields=(), join_fields=(), where=None, order=None, limit=None):
            """Run an inner left join query

                tables = (table1, table2)
                fields = ([fields from table1], [fields from table 2])  # fields to select
                join_fields = (field1, field2                    print('...............', self.conn.open)
)  # fields to join. field1 belongs to table1 and field2 belongs to table 2
                where = ("parameterizedstatement", [parameters])
                        eg: ("id=%s and name=%s", [1, "test"])
                order = [field, ASC|DESC]
                limit = [limit1, limit2]
            """
            if not self.conn.open:
                self.connect()
            cur = self._select_join(tables, fields, join_fields, where, order, limit)
            result = cur.fetchall()

            rows = None
            if result:
                Row = namedtuple("Row", [f[0] for f in cur.description])
                # rows = [Row(*r) for r in result]
                rows = [r for r in result]

            return rows

        def insert(self, table, data):
            """Insert a record"""
            if not self.conn.open:
                self.connect()
            query = self._serialize_insert(data)

            sql = "INSERT INTO %s (%s) VALUES(%s)" % (table, query[0], query[1])

            # return self.query(sql, list(data.values())).rowcount
            insert_row = self.query(sql, list(data.values())).lastrowid
            return insert_row

        def insertBatch(self, table, data):
            """Insert multiple record"""
            if not self.conn.open:
                self.connect()
            query = self._serialize_batch_insert(data)
            sql = "INSERT INTO %s (%s) VALUES %s" % (table, query[0], query[1])
            flattened_values = [v for sublist in data for k, v in sublist.items()]
            return self.query(sql, flattened_values).rowcount

        def insertIgnoreBatch(self, table, data):
            """Insert multiple record"""
            if not self.conn.open:
                self.connect()
            query = self._serialize_batch_insert(data)
            sql = "INSERT IGNORE INTO %s (%s) VALUES %s" % (table, query[0], query[1])
            flattened_values = [v for sublist in data for k, v in sublist.items()]
            return self.query(sql, flattened_values).rowcount

        def update(self, table, data, where=None):
            """Insert a record"""

            # # update rows based on a parametrized condition
            # db.update("books",
            #   {"discount": 10},
            #   ("id=%s AND year=%s", [id, year])
            # )
            if not self.conn.open:
                self.connect()
            query = self._serialize_update(data)

            sql = "UPDATE %s SET %s" % (table, query)

            if where and len(where) > 0:
                sql += " WHERE %s" % where[0]

            return self.query(sql, list(data.values()) + where[1] if where and len(where) > 1 else data.values()
                              ).rowcount

        def insertOrUpdate(self, table, data, keys):
            if not self.conn.open:
                self.connect()
            insert_data = data.copy()

            data = {k: data[k] for k in data if k not in keys}

            insert = self._serialize_insert(insert_data)

            update = self._serialize_update(data)

            sql = "INSERT INTO %s (%s) VALUES(%s) ON DUPLICATE KEY UPDATE %s" % (table, insert[0], insert[1], update)

            return self.query(sql, list(insert_data.values()) + list(data.values())).rowcount

        def delete(self, table, where=None):
            """Delete rows based on a where condition"""
            if not self.conn.open:
                self.connect()

            sql = "DELETE FROM %s" % table

            if where and len(where) > 0:
                sql += " WHERE %s" % where[0]

            return self.delete_query(sql, where[1] if where and len(where) > 1 else None).rowcount

        def delete_query(self, sql, params=None):
            """Run a raw query"""

            # check if connection is alive. if not, reconnect
            try:
                if not self.conn.open:
                    self.connect()
                self.cur.execute(sql, params)
                self.commit()
            #     self.cur.execute(sql, params)
            #     self.commit()
            #
            # except MySQLdb.OperationalError as e:
            #     # mysql timed out. reconnect and retry once
            #     if e[0] == 2006:
            #         self.connect()
            #         self.cur.execute(sql, params)
            #     else:
            #         raise
            except Warning as a_warning:
                pass
            except:
                # print("Query failed")
                raise

            return self.cur

        def query(self, sql, params=None):
            """Run a raw query"""
            # check if connection is alive. if not, reconnect
            try:
                self.connect()
                self.cur.execute(sql, params)
                self.commit()

            # except Warning as a_warning:
            #     pass
            except:
                print("Query failed")
                raise

            return self.cur

        def commit(self):
            """Commit a transaction (transactional engines like InnoDB require this)"""
            if not self.conn.open:
                self.connect()
            return self.conn.commit()

        def rollback(self):
            """Rollback a transaction (transactional engines like InnoDB require this)"""
            if not self.conn.open:
                self.connect()
            return self.conn.rollback()

        def is_open(self):
            """Check if the connection is open"""
            if not self.conn.open:
                self.connect()
            return self.conn.open

        def close(self):
            """Kill the connection"""
            self.cur.close()
            self.conn.close()

        def _serialize_insert(self, data):
            """Format insert dict values into strings"""
            if not self.conn.open:
                self.connect()
            keys = ",".join(list(data.keys()))
            vals = ",".join(["%s" for k in data])

            return [keys, vals]

        def _serialize_batch_insert(self, data):
            #       """Format insert dict values into strings"""
            if not self.conn.open:
                self.connect()
            keys = ",".join(list(data[0].keys()))
            v = "(%s)" % ",".join(tuple("%s".rstrip(',') for v in range(len(data[0]))))
            l = ','.join(list(repeat(v, len(data))))
            return [keys, l]

        def _serialize_update(self, data):
            """Format update dict values into string"""
            if not self.conn.open:
                self.connect()
            return "=%s,".join(list(data.keys())) + "=%s"

        def _select(self, table=None, fields=(), where=None, order=None, limit=None):
            """Run a select query"""
            if not self.conn.open:
                self.connect()

            sql = "SELECT %s FROM `%s`" % (",".join(fields), table)

            # where conditions
            if where and len(where) > 0:
                sql += " WHERE %s" % where[0]

            # order
            if order:
                sql += " ORDER BY %s" % order[0]

                if len(order) > 1:
                    sql += " %s" % order[1]

            # limit
            if limit:
                sql += " LIMIT %s" % limit[0]

                if len(limit) > 1:
                    sql += " OFFSET %s" % limit[1]

            return self.query(sql, where[1] if where and len(where) > 1 else None)

        def _select_join(self, tables=(), fields=(), join_fields=(), where=None, order=None, limit=None):
            """Run an inner left join query"""
            if not self.conn.open:
                self.connect()
            fields = [tables[0] + "." + f for f in fields[0]] + \
                     [tables[1] + "." + f for f in fields[1]]

            sql = "SELECT %s FROM %s LEFT JOIN %s ON (%s = %s)" % \
                  (",".join(fields),
                   tables[0],
                   tables[1],
                   tables[0] + "." + join_fields[0],
                   tables[1] + "." + join_fields[1]
                   )

            # where conditions
            if where and len(where) > 0:
                sql += " WHERE %s" % where[0]

            # order
            if order:
                sql += " ORDER BY %s" % order[0]

                if len(order) > 1:
                    sql += " " + order[1]

            # limit
            if limit:
                sql += " LIMIT %s" % limit[0]

                if len(limit) > 1:
                    sql += " OFFSET %s" % limit[1]

            return self.query(sql, where[1] if where and len(where) > 1 else None)

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()

        def fetch_all(self, query):
            try:
                if not self.conn.open:
                    self.connect()
                cursor = self.conn.cursor()
                cursor.execute(query)
                data = cursor.fetchall()
                self.conn.commit()
                cursor.close()
                return data
            except Exception as e:
                print('[base] :: fetch_all() :: Got exception: %s' % e)
                raise e

    instance = None

    def __init__(self, **args):
        if not Database.instance:
            print("connection init")
            Database.instance = Database.__Database(**args)
        else:
            if not Database.instance.conn.open:
                Database.instance.connect()

            print("connection singleton")

    def __getattr__(self, name):
        return getattr(self.instance, name)

