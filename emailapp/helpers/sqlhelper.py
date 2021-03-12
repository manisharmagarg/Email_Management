import mysql.connector
from conf.config import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, DBNAME


my_sql_cursor = mysql.connector.connect(user=MYSQL_USER, password=MYSQL_PASS,
                                        host=MYSQL_HOST, database=DBNAME)


def create_table():
    cursor = my_sql_cursor.cursor()
    user = "CREATE TABLE IF NOT EXISTS user (" \
           "id INT NOT NULL AUTO_INCREMENT," \
           "firstname CHAR(50)," \
           "lastname CHAR(50)," \
           "email VARCHAR(191) UNIQUE ," \
           "password CHAR(120)," \
           "created_on TIMESTAMP, " \
           "PRIMARY KEY(id)) ;"

    email_user = "CREATE TABLE IF NOT EXISTS email_user (" \
                 "id INT NOT NULL AUTO_INCREMENT, " \
                 "name CHAR(50) CHARACTER SET utf8mb4 " \
                 "COLLATE utf8mb4_unicode_ci, " \
                 "email CHAR(191) CHARACTER SET utf8mb4 " \
                 "COLLATE utf8mb4_unicode_ci, " \
                 "user_id INT, " \
                 "created_on TIMESTAMP, " \
                 "FOREIGN KEY (user_id) REFERENCES user(id) " \
                 "ON DELETE CASCADE, " \
                 "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    list = "CREATE TABLE IF NOT EXISTS list (" \
           "id INT NOT NULL AUTO_INCREMENT, " \
           "list_name CHAR(50) CHARACTER SET utf8mb4 " \
           "COLLATE utf8mb4_unicode_ci," \
           "user_id INT, "\
           "created_on TIMESTAMP, " \
           "FOREIGN KEY (user_id) REFERENCES user(id) " \
           "ON DELETE CASCADE, " \
           "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    list_segments = "CREATE TABLE IF NOT EXISTS list_segments (" \
                    "id INT NOT NULL AUTO_INCREMENT, " \
                    "email CHAR(191) CHARACTER SET utf8mb4 " \
                    "COLLATE utf8mb4_unicode_ci," \
                    "list_id INT," \
                    "user_id INT,"\
                    "created_on TIMESTAMP, " \
                    "FOREIGN KEY (list_id) REFERENCES list(id) " \
                    "ON DELETE CASCADE," \
                    "FOREIGN KEY (user_id) REFERENCES user(id) " \
                    "ON DELETE CASCADE, " \
                    "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    templates = "CREATE TABLE IF NOT EXISTS templates (" \
                "id INT NOT NULL AUTO_INCREMENT, " \
                "name CHAR(50) CHARACTER SET utf8mb4 " \
                "COLLATE utf8mb4_unicode_ci," \
                "path CHAR(50) CHARACTER SET utf8mb4 " \
                "COLLATE utf8mb4_unicode_ci, " \
                "system_template VARCHAR(45)," \
                "created_on TIMESTAMP, " \
                "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    templatevars = "CREATE TABLE IF NOT EXISTS templatevars (" \
                   "id INT NOT NULL AUTO_INCREMENT, " \
                   "template_key CHAR(100) CHARACTER SET utf8mb4 " \
                   "COLLATE utf8mb4_unicode_ci," \
                   "template_value CHAR(100) CHARACTER SET utf8mb4 " \
                   "COLLATE utf8mb4_unicode_ci," \
                   "templates_id INT, " \
                   "system_type CHAR(10) CHARACTER SET utf8mb4 " \
                   "COLLATE utf8mb4_unicode_ci,"\
                   "created_on TIMESTAMP, " \
                   "FOREIGN KEY (templates_id) REFERENCES templates(id) " \
                   "ON DELETE CASCADE, " \
                   "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    campaigns = "CREATE TABLE IF NOT EXISTS campaigns (" \
                "id INT NOT NULL AUTO_INCREMENT, " \
                "user_id INT," \
                "list_id INT," \
                "templates_id INT, " \
                "status CHAR(50) CHARACTER SET utf8mb4 " \
                "COLLATE utf8mb4_unicode_ci, " \
                "name CHAR(50) CHARACTER SET utf8mb4 " \
                "COLLATE utf8mb4_unicode_ci, " \
                "created_on TIMESTAMP, " \
                "campaign_state VARCHAR(45), " \
                "parent_campaign_id INT, " \
                "is_ab_campaign BIT, " \
                "test_percentage VARCHAR(45), " \
                "queued_time DATETIME," \
                "campaign_type VARCHAR(45),"\
                "email_subject VARCHAR(45),"\
                "preview_text VARCHAR(45), "\
                "send_time VARCHAR(45), "\
                "type VARCHAR(45), "\
                "FOREIGN KEY (user_id) REFERENCES user(id) " \
                "ON DELETE CASCADE, " \
                "FOREIGN KEY (templates_id) REFERENCES templates(id) " \
                "ON DELETE CASCADE, " \
                "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    email_results = "CREATE TABLE IF NOT EXISTS email_results (" \
                    "id INT NOT NULL AUTO_INCREMENT, " \
                    "list_id INT," \
                    "list_segment_id INT," \
                    "templates_id INT, " \
                    "result CHAR(100) CHARACTER SET utf8mb4 " \
                    "COLLATE utf8mb4_unicode_ci, " \
                    "result_description CHAR(250) CHARACTER SET utf8mb4 " \
                    "COLLATE utf8mb4_unicode_ci, " \
                    "campaign_id INT, " \
                    "ab_campaign_id INT, " \
                    "created_on TIMESTAMP, " \
                    "FOREIGN KEY (list_id) REFERENCES list(id) " \
                    "ON DELETE CASCADE, " \
                    "FOREIGN KEY (list_segment_id) REFERENCES " \
                    "list_segments(id) ON DELETE CASCADE," \
                    "FOREIGN KEY (templates_id) REFERENCES templates(id) " \
                    "ON DELETE CASCADE, " \
                    "FOREIGN KEY (campaign_id) REFERENCES campaigns(id) " \
                    "ON DELETE CASCADE," \
                    "FOREIGN KEY (ab_campaign_id) REFERENCES " \
                    "ab_campaigns(id) ON DELETE CASCADE," \
                    "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    ready_to_send_emails = "CREATE TABLE IF NOT EXISTS " \
                           "ready_to_send_emails (" \
                           "id INT NOT NULL AUTO_INCREMENT, " \
                           "email_address CHAR(200) CHARACTER SET utf8mb4 " \
                           "COLLATE utf8mb4_unicode_ci," \
                           "campaign_id INT," \
                           "ab_campaign_id INT, " \
                           "campaign_type VARCHAR(45), "\
                           "template_html TEXT," \
                           "subject CHAR(200) CHARACTER SET utf8mb4 " \
                           "COLLATE utf8mb4_unicode_ci," \
                           "status CHAR(50) CHARACTER SET utf8mb4 " \
                           "COLLATE utf8mb4_unicode_ci, " \
                           "list_segment_id INT ," \
                           "created_on TIMESTAMP, " \
                           "FOREIGN KEY (campaign_id) REFERENCES " \
                           "campaigns(id) ON DELETE CASCADE," \
                           "FOREIGN KEY (list_segment_id) REFERENCES " \
                           "list_segments(id) ON DELETE CASCADE," \
                           "FOREIGN KEY (ab_campaign_id) REFERENCES " \
                           "ab_campaigns(id) ON DELETE CASCADE," \
                           "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    campaigns_stats = "CREATE TABLE IF NOT EXISTS campaign_stats (" \
                      "id INT NOT NULL AUTO_INCREMENT, " \
                      "campaign_id INT," \
                      "ab_campaign_id INT," \
                      "segment_id INT," \
                      "template_id INT,"\
                      "open BOOLEAN,"\
                      "click BOOLEAN," \
                      "url VARCHAR(250) ," \
                      "created_on TIMESTAMP, " \
                      "IPAddress VARCHAR(250) ," \
                      "FOREIGN KEY (campaign_id) REFERENCES campaigns(id) " \
                      "ON DELETE CASCADE," \
                      "FOREIGN KEY (ab_campaign_id) REFERENCES " \
                      "ab_campaigns(id) ON DELETE CASCADE," \
                      "FOREIGN KEY (segment_id) REFERENCES " \
                      "list_segments(id) ON DELETE CASCADE," \
                      "FOREIGN KEY (template_id) REFERENCES " \
                      "templates(id) ON DELETE CASCADE," \
                      "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    system_emails = "CREATE TABLE IF NOT EXISTS system_emails (" \
                    "id INT NOT NULL AUTO_INCREMENT," \
                    "user_id INT," \
                    "email_type CHAR(50) CHARACTER SET utf8mb4 " \
                    "COLLATE utf8mb4_unicode_ci," \
                    "status CHAR(50) CHARACTER SET utf8mb4 " \
                    "COLLATE utf8mb4_unicode_ci," \
                    "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    campaigns_winning_combination = "CREATE TABLE IF NOT EXISTS " \
                                    "campaigns_winning_combination (" \
                                    "id INT NOT NULL AUTO_INCREMENT, " \
                                    "campaign_id INT," \
                                    "rate VARCHAR(250)," \
                                    "time_after VARCHAR(250)," \
                                    "time_type VARCHAR(250)," \
                                    "created_on TIMESTAMP, " \
                                    "FOREIGN KEY (campaign_id) REFERENCES " \
                                    "campaigns(id) ON DELETE CASCADE," \
                                    "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    unsubscribe = "CREATE TABLE IF NOT EXISTS unsubscribe (" \
                  "id INT NOT NULL AUTO_INCREMENT, " \
                  "email_address VARCHAR(70), "\
                  "campaign_id VARCHAR(70), "\
                  "created_on TIMESTAMP, "\
                  "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    #############################
    #       A/B Test            #
    #############################
    ab_campaigns_parent = "CREATE TABLE IF NOT EXISTS ab_campaigns_parent (" \
                          "id INT NOT NULL AUTO_INCREMENT, " \
                          "user_id INT, "\
                          "name VARCHAR(70), "\
                          "list_id INT, "\
                          "test_percentage INT, "\
                          "test_variable VARCHAR(70), "\
                          "rate VARCHAR(250), "\
                          "time_after VARCHAR(250)," \
                          "time_type VARCHAR(250)," \
                          "ab_campaign_count VARCHAR(70), "\
                          "campaign_type VARCHAR(70), "\
                          "status VARCHAR(70), "\
                          "queued_time DATETIME," \
                          "campaign_state VARCHAR(70), " \
                          "type VARCHAR(45), " \
                          "created_on TIMESTAMP, " \
                          "FOREIGN KEY (user_id) REFERENCES user(id) " \
                          "ON DELETE CASCADE, " \
                          "FOREIGN KEY (list_id) REFERENCES list(id) " \
                          "ON DELETE CASCADE, " \
                          "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    ab_campaigns = "CREATE TABLE IF NOT EXISTS ab_campaigns (" \
                   "id INT NOT NULL AUTO_INCREMENT, " \
                   "ab_campaign_parent_id INT, "\
                   "user_id INT, "\
                   "email_subject  VARCHAR(70), " \
                   "preview_text VARCHAR(45), " \
                   "templates_id INT, " \
                   "send_time VARCHAR(45), "\
                   "status VARCHAR(45), " \
                   "campaign_state VARCHAR(45), " \
                   "created_on TIMESTAMP, " \
                   "FOREIGN KEY (ab_campaign_parent_id) REFERENCES " \
                   "ab_campaigns_parent(id) ON DELETE CASCADE, " \
                   "FOREIGN KEY (user_id) REFERENCES user(id) " \
                   "ON DELETE CASCADE, " \
                   "FOREIGN KEY (templates_id) REFERENCES " \
                   "templates(id) ON DELETE CASCADE, " \
                   "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    bounce = "CREATE TABLE IF NOT EXISTS bounce (" \
             "id INT NOT NULL AUTO_INCREMENT," \
             "notification_type  VARCHAR(70), " \
             "email_address CHAR(191) CHARACTER SET utf8mb4, " \
             "source_address CHAR(191) CHARACTER SET utf8mb4, " \
             "source_arn VARCHAR(250), " \
             "source_ip VARCHAR(250), " \
             "sendingAccountId VARCHAR(250), " \
             "remoteMtaIp VARCHAR(250), " \
             "send_timestamp VARCHAR(250), " \
             "message_id VARCHAR(250), " \
             "subject VARCHAR(250), " \
             "created_on TIMESTAMP, " \
             "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"


    complaint = "CREATE TABLE IF NOT EXISTS complaint (" \
                "id INT NOT NULL AUTO_INCREMENT," \
                "notification_type  VARCHAR(70), " \
                "email_address CHAR(191) CHARACTER SET utf8mb4, " \
                "source_address CHAR(191) CHARACTER SET utf8mb4, " \
                "source_arn VARCHAR(250), " \
                "source_ip VARCHAR(250), " \
                "sendingAccountId VARCHAR(250), " \
                "send_timestamp VARCHAR(250), " \
                "message_id VARCHAR(250), " \
                "subject VARCHAR(250), " \
                "created_on TIMESTAMP, " \
                "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    delivery = "CREATE TABLE IF NOT EXISTS delivery (" \
               "id INT NOT NULL AUTO_INCREMENT," \
               "notification_type  VARCHAR(70), " \
               "email_address CHAR(191) CHARACTER SET utf8mb4, " \
               "source_address CHAR(191) CHARACTER SET utf8mb4, " \
               "source_arn VARCHAR(250), " \
               "source_ip VARCHAR(250), " \
               "sendingAccountId VARCHAR(250), " \
               "remoteMtaIp VARCHAR(250), " \
               "send_timestamp VARCHAR(250), " \
               "message_id VARCHAR(250), " \
               "subject VARCHAR(250), " \
               "created_on TIMESTAMP, " \
               "PRIMARY KEY(id)) CHARACTER SET utf8mb4;"

    cursor.execute(user)
    cursor.execute(email_user)
    cursor.execute(list)
    cursor.execute(list_segments)
    cursor.execute(templates)
    cursor.execute(templatevars)
    cursor.execute(campaigns)
    cursor.execute(system_emails)
    cursor.execute(campaigns_winning_combination)
    cursor.execute(unsubscribe)

    cursor.execute(ab_campaigns_parent)
    cursor.execute(ab_campaigns)
    cursor.execute(campaigns_stats)
    cursor.execute(ready_to_send_emails)
    cursor.execute(email_results)

    cursor.execute(complaint)
    cursor.execute(bounce)
    cursor.execute(delivery)

    my_sql_cursor.commit()
    print("Models created successfully")
    cursor.close()


def insert_data(firstname, lastname, email, password):
    cursor = my_sql_cursor.cursor()
    query = ("INSERT INTO user(firstname, lastname, email, password) "
             "VALUES (%s, %s, %s, %s)")
    data = (firstname, lastname, email, password)
    cursor.execute(query, data)
    my_sql_cursor.commit()
    cursor.close()


def insert_email_user(name, email):
    cursor = my_sql_cursor.cursor()
    query = ("INSERT INTO email_user(name, email) "
             "VALUES (%s, %s)")
    data = (name, email)
    cursor.execute(query, data)
    my_sql_cursor.commit()
    cursor.close()


def insert_list(listname, user_id):
    cursor = my_sql_cursor.cursor()
    query = "INSERT INTO list(list_name, user_id) VALUE ('%s', '%s')" % \
            (listname, user_id)
    cursor.execute(query)
    to_get = "SELECT * FROM list WHERE id=(SELECT MAX(id) FROM list);"
    cursor.execute(to_get)
    data = cursor.fetchone()
    my_sql_cursor.commit()
    cursor.close()
    return data[0]


def insert_list_segments(email, id):
    cursor = my_sql_cursor.cursor()
    query = "INSERT INTO list_segments(email, list_id) VALUE ('%s', '%s')" % \
            (email, str(id))
    data = (email, id)
    cursor.execute(query)
    my_sql_cursor.commit()
    cursor.close()


def authenticate(email):
    cursor = my_sql_cursor.cursor()
    query = "SELECT password FROM user WHERE email = '%s'" % email
    cursor.execute(query)
    data = cursor.fetchone()
    my_sql_cursor.commit()
    cursor.close()
    return data


def get_email_user():
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM email_user"
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    cursor.close()
    return data


def get_list():
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM list"
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    cursor.close()
    return data


def get_list_segment():
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM list_segments"
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    cursor.close()
    return data


def get_listsegment_count(id):
    cursor = my_sql_cursor.cursor()
    query = "SELECT COUNT(*) FROM list_segments WHERE list_id = '%s'" % id
    cursor.execute(query)
    data = cursor.fetchone()
    my_sql_cursor.commit()
    cursor.close()
    return data[0]


def delete_listsegment_by_id(id):
    cursor = my_sql_cursor.cursor()
    query1 = "DELETE FROM list WHERE id = '%s'" % id
    query2 = "DELETE FROM list_segments WHERE list_id = '%s'" % id
    cursor.execute(query1)
    cursor.execute(query2)
    my_sql_cursor.commit()


def delete_listsegment_user_by_id(id):
    cursor = my_sql_cursor.cursor()
    query = "DELETE FROM list_segments WHERE id = '%s'" % id
    cursor.execute(query)
    my_sql_cursor.commit()


def get_listsegment_by_listid(list_id):
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM list_segments WHERE list_id = '%s'" % list_id
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    return data


def get_template_by_id(template_id):
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM templates WHERE id = '%s'" % id
    cursor.execute(query)
    data = cursor.fetchone()
    my_sql_cursor.commit()
    return data


def get_templatevars():
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM templatevars"
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    return data


def get_templatevars_by_template_id(template_id):
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM templatevars where templates_id=%s" % template_id
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    return data


def get_email_configurations():
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM email_configuration WHERE status='ACTIVE'"
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    return data


def get_list_segments_by_id(id):
    cursor = my_sql_cursor.cursor()
    query = "SELECT * FROM list_segments WHERE list_id = '%s'" % id
    cursor.execute(query)
    data = cursor.fetchall()
    my_sql_cursor.commit()
    return data


def create_email_result(campaign_id, list_id, list_segment_id, template_id,
                        result, result_desc):
    cursor = my_sql_cursor.cursor()
    query = "INSERT INTO email_results(campaign_id, list_id, " \
            "list_segment_id, " \
            "templates_id, result, result_description) " \
            "VALUE (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (campaign_id, list_id, list_segment_id, template_id,
                           result, result_desc))
    my_sql_cursor.commit()
