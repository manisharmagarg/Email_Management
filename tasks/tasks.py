import mysql.connector
from celery import Celery
import logging
from conf.config import MYSQL_USER, MYSQL_PASS, MYSQL_HOST, DBNAME, \
    CONNECT_TIMEOUT, CELERY_BROKER_URL, CELERY_RESULT_BACKEND, \
    USE_AWS_EMAIL_SERVER, EMAIL_OPEN_URL, EMAIL_CLICK_URL, \
    APP_ROOT, APP_STATIC, LIMIT, EMAIL_UNSUBSCRIBE
from .smtp_email import SmtpEmail
from .ses_email import Email
import traceback
import mysql.connector
import os
from string import Template
from .sql_helpers import campaign_helper, lists, templates, email_result, \
    ready_to_send_email_helper, emails_unsubscribe, ab_campaigns_helper
import urllib
from .tracking.email_tracking import EmailTracking
import pytracking
from pytracking.html import adapt_html
from datetime import datetime
from datetime import timedelta

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)

CELERYBEAT_SCHEDULE = {
    "runs-every-91-seconds": {
        "task": "process_emails",
        "schedule": 91.0,
        "args": (),
    },
    "runs-every-145-seconds": {
        "task": "process_ab_campaign_emails",
        "schedule": 145.0,
        "args": (),
    },
    "run-ab-send-email-181-seconds": {
        "task": "send_ab_emails",
        "schedule": 181.0,
        "args": (),
    },
    "run-send-email-99-seconds": {
        "task": "send_emails",
        "schedule": 99.0,
        "args": (),
    },
    "runs-every-61-seconds": {
        "task": "mark_campaigns_processed",
        "schedule": 61.0,
        "args": (),
    },
}

my_sql_cursor = mysql.connector.connect(user=MYSQL_USER,
                                        password=MYSQL_PASS,
                                        host=MYSQL_HOST,
                                        database=DBNAME,
                                        connect_timeout=CONNECT_TIMEOUT)

my_sql_cursor.autocommit = False

app = Celery('tasks')

app.conf.update(
    result_expires=60,
    task_acks_late=True,
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND
)

CELERY_ROUTES = {
    'tasks.send_email': {'queue': 'send_email'},
}

###############################################################################
#                                                                             #
#   app.config_from_object(CELERY_CONFIG)                                     #
#   run below statement                                                       #
#   celery - A tasks.app worker - B --loglevel = info                         #
#   celery -A tasks.app purge                                                 #
#   celery -A tasks.app worker -B --loglevel=info -Q default,send_email -c 10 #
#                                                                             #
###############################################################################

app.conf.beat_schedule.update(CELERYBEAT_SCHEDULE)

app.conf.task_default_queue = 'default'

app.conf.task_routes = CELERY_ROUTES


@app.task(name="mark_campaigns_processed")
def mark_campaigns_processed():
    campaign_obj = campaign_helper.CampaignHelper()
    ab_campaigns_helper_obj = ab_campaigns_helper.AbCampaignsHelper()
    list_obj = lists.Lists()
    email_result_obj = email_result.EmailResultHelper()
    ready_to_send_emails_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()

    try:
        campaigns = campaign_obj.get_email_configurations_processing(is_ab_campaign=False)
        # my_sql_cursor.commit()

        for campaign in campaigns:
            campaign_id = campaign['id']
            is_ab_campaign = int.from_bytes(campaign['is_ab_campaign'], byteorder='big')

            logging.warning('Processing Campaign %s' % campaign_id)

            emails_result = email_result_obj.check_if_all_emails_processed_for_campaign(campaign_id)

            ready_to_send_emails = ready_to_send_emails_obj.get_all_emails_by_campaigns(campaign_id)

            if emails_result and ready_to_send_emails:
                if len(emails_result) == len(ready_to_send_emails):
                    campaign_obj.update_email_configration_status(campaign_id, 'PROCESSED')
            # my_sql_cursor.commit()

    except Exception as e:
        # my_sql_cursor.rollback()
        logging.warning('[celery app] :: mark_campaigns_processed() :: Got exception: %s' % e)
        logging.warning(traceback.format_exc())

    try:
        logging.warning('Processing AB campaigns...')
        campaigns = ab_campaigns_helper_obj.get_email_configurations_processing()

        for campaign in campaigns:
            campaign_id = campaign['id']
            parent_campaign_id = campaign['ab_campaign_parent_id']

            emails_a_result = email_result_obj.check_if_all_emails_processed_for_ab_campaign(campaign_id)

            ready_to_send_a_emails = ready_to_send_emails_obj.get_all_emails_by_AB_campaign(campaign_id)

            if emails_a_result and ready_to_send_a_emails:
                if len(emails_a_result) == len(ready_to_send_a_emails):
                    ab_campaigns_helper_obj.update_email_configration_status(campaign_id, 'PROCESSED')
                    ab_campaigns_helper_obj.update_parenet_campaign_status(parent_campaign_id, 'PROCESSED')

    except Exception as e:
        # my_sql_cursor.rollback()
        logging.warning('[celery app] :: mark_campaigns_processed() :: '
                        'Got exception: %s' % e)
        logging.warning(traceback.format_exc())


@app.task(name="process_emails")
def process_emails_campaigns():
    try:
        logging.warning('process_emails_campaigns')
        campaign_helper_obj = campaign_helper.CampaignHelper()
        QUEUED_TIME = datetime.now()
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        list_obj = lists.Lists()

        ready_to_send_emails_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()

        emails_unsubscribe_helper_obj = emails_unsubscribe.EmailUnsubscribeHelper()

        campaigns = campaign_helper_obj.get_email_configurations()
        for email_config in campaigns:
            try:

                campaign_id = email_config['id']
                template_id = email_config['templates_id']
                campaign_type = email_config['campaign_type']
                send_time = email_config['send_time']

                if campaign_helper_obj. \
                        check_if_campaign_already_processing(campaign_id):
                    logging.warning('Already Processed # %s' % (str(campaign_id)))
                    continue

                if current_time < send_time:
                    continue

                list_id = email_config['list_id']

                users = list_obj. \
                    get_list_segment_by_listid(list_id)  # get segments on base of list id
                # Change status to PROCESSING
                processing_status = 'PROCESSING'
                campaign_helper_obj. \
                    update_email_configration_status(campaign_id, processing_status)

                template_html = build_template(template_id)
                subject = email_config['email_subject']
                # get_ready_to_send_emails = len(ready_to_send_emails_obj.get_all_emails_by_campaign(campaign_id))

                list_segments_emails = list_obj.get_segments_mails_by_campaing_id(campaign_id)
                list_segments_emails_list = []
                for get_list_segments in list_segments_emails:
                    list_segments_emails_list.append(get_list_segments)

                # get_list_segments_emails = len(list_segments_emails_list)

                if template_html:
                    try:
                        for user in users:
                            last_one_hour_emails = ready_to_send_emails_obj.get_all_ready_to_send_emails_by_status()
                            one_hour_record_list = []
                            for emails_record in last_one_hour_emails:
                                one_hour_record_list.append(emails_record)
                            last_one_hour_emails_len = len(one_hour_record_list)

                            logging.warning('last_one_hour_emails %s' % last_one_hour_emails_len)

                            email_address = user['email']
                            list_segment_id = user['id']

                            if last_one_hour_emails_len > LIMIT:
                                logging.warning('One hour limit crossed !')
                                break
                            else:
                                remaining_emails = LIMIT - last_one_hour_emails_len
                                logging.warning('remaining_emails %s' % remaining_emails)

                                email_schedule_for_sending = ready_to_send_emails_obj. \
                                    check_is_emails_records(email_address, campaign_id)

                                if not email_schedule_for_sending:

                                    if emails_unsubscribe_helper_obj.check_emails_record(email_address):

                                        ready_email_status = "UNSUBSCRIBE"
                                        ready_to_send_emails_obj. \
                                            add_ready_to_emails(email_address,
                                                                template_html,
                                                                subject,
                                                                ready_email_status,
                                                                list_segment_id,
                                                                campaign_type,
                                                                campaign_id=campaign_id)

                                    else:
                                        ready_email_status = "READY_TO_SEND"
                                        ready_to_send_emails_obj. \
                                            add_ready_to_emails(email_address,
                                                                template_html,
                                                                subject,
                                                                ready_email_status,
                                                                list_segment_id,
                                                                campaign_type,
                                                                campaign_id=campaign_id)
                                    get_ready_to_send_emails = len(
                                        ready_to_send_emails_obj.get_all_emails_by_campaign(campaign_id))
                                    get_list_segments_emails = len(list_segments_emails_list)
                                    if get_ready_to_send_emails == get_list_segments_emails:
                                        processing_status = 'QUEUED'
                                        campaign_helper_obj. \
                                            update_email_configration_queued_time(campaign_id,
                                                                                  processing_status,
                                                                                  QUEUED_TIME)

                    except Exception as e:
                        logging.warning('[Tasks] :: process_email() :: %s' % e)
                        logging.warning(traceback.format_exc())

                # my_sql_cursor.commit()

            except Exception as e:
                # my_sql_cursor.rollback()
                logging.warning('[Tasks] :: process_email() :: %s' % e)
                logging.warning(traceback.format_exc())
    except Exception as e:
        logging.warning(e)
        logging.warning(traceback.format_exc())


@app.task(name="process_ab_campaign_emails")
def process_emails_ab_campaigns():
    try:
        logging.warning('process AB campaign')
        ab_campaigns_helper_obj = ab_campaigns_helper.AbCampaignsHelper()
        emails_unsubscribe_helper_obj = emails_unsubscribe.EmailUnsubscribeHelper()
        QUEUED_TIME = datetime.now()
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        list_helper_obj = lists.Lists()
        ready_to_send_emails_helper_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()

        # QUEUED_TIME = datetime.now()
        ab_campaigns = ab_campaigns_helper_obj.get_all_ab_campaign()

        for email_config in ab_campaigns:
            try:

                parent_ab_campaign_id = email_config['id']
                list_id = email_config['list_id']
                ab_campaign_count = email_config['ab_campaign_count']
                templates_id = email_config['templates_id']
                test_percentage = email_config['test_percentage']
                campaign_type = email_config['campaign_type']
                send_time = email_config['send_time']

                segments = list_helper_obj.get_list_segment_by_listid(list_id)

                template_html = build_template(templates_id)

                if current_time < send_time:
                    continue

                if template_html:
                    segment_list_len = len(segments)

                    ab_campaign_data = ab_campaigns_helper_obj.get_ab_campagin_by_id(parent_ab_campaign_id)
                    total_emails_segment_list = []
                    ab_campaign_ids = []
                    ab_campaign_subjects = []
                    total_email_processed = ''
                    for ab_campaign in ab_campaign_data:
                        ab_campaign_ids.append(ab_campaign['id'])
                        ab_campaign_subjects.append(ab_campaign['email_subject'])

                    if ab_campaign_count == '3':
                        test_percent = int(int(segment_list_len) * int(test_percentage)) / 100

                        campaign_first = int(test_percent) / 3
                        segment_first_campaign = segments[:int(campaign_first)]

                        segment_second_campaign = segments[int(campaign_first):(int(campaign_first) * 2)]

                        segment_third_campaign = segments[(int(campaign_first) * 2): (int(campaign_first) * 3)]

                        total_email_processed = len(segment_first_campaign) + \
                                                len(segment_second_campaign) + len(segment_third_campaign)

                        logging.warning('total_email_processed %s' % total_email_processed)
                        total_emails_segment_list.insert(0, segment_first_campaign)
                        total_emails_segment_list.insert(1, segment_second_campaign)
                        total_emails_segment_list.insert(2, segment_third_campaign)

                    if ab_campaign_count == '2':
                        test_percent = int(int(segment_list_len) * int(test_percentage)) / 100

                        campaign_first = int(test_percent) / 2
                        segment_first_campaign = segments[:int(campaign_first)]

                        segment_second_campaign = segments[int(campaign_first):(int(campaign_first) * 2)]

                        total_email_processed = len(segment_first_campaign) + len(segment_second_campaign)

                        logging.warning('total_email_processed %s' % total_email_processed)
                        total_emails_segment_list.insert(0, segment_first_campaign)
                        total_emails_segment_list.insert(1, segment_second_campaign)

                    last_one_hour_emails = ready_to_send_emails_helper_obj. \
                        get_all_ready_to_send_emails_by_status()
                    one_hour_record_list = []
                    for emails_record in last_one_hour_emails:
                        one_hour_record_list.append(emails_record)

                    last_one_hour_emails_len = len(one_hour_record_list)

                    logging.warning('last_one_hour_emails_len %s' % last_one_hour_emails_len)
                    remaining_emails = LIMIT - last_one_hour_emails_len

                    logging.warning('Remaining AB emails %s' % remaining_emails)

                    if last_one_hour_emails_len > LIMIT:
                        logging.warning('AB Campaign One hour limit crossed !')
                        break
                    else:
                        if remaining_emails > total_email_processed:
                            for index, val in enumerate(total_emails_segment_list):

                                for mail in val:
                                    email_address = mail['email']
                                    segment_id = mail['id']
                                    ab_campaign = ab_campaign_ids[index]

                                    """
                                    Change status to PROCESSING

                                    """
                                    processing_status = 'PROCESSING'
                                    ab_campaigns_helper_obj. \
                                        update_email_configration_status(ab_campaign,
                                                                         processing_status)
                                    ab_campaigns_helper_obj. \
                                        update_parenet_campaign_status(parent_ab_campaign_id,
                                                                       processing_status)

                                    email_schedule_for_sending = ready_to_send_emails_helper_obj. \
                                        check_is_ab_emails_records(email_address, ab_campaign)

                                    if not email_schedule_for_sending:
                                        if emails_unsubscribe_helper_obj.check_emails_record(email_address):
                                            ready_email_status = "UNSUBSCRIBE"
                                            ready_to_send_emails_helper_obj. \
                                                add_ready_to_emails(email_address,
                                                                    template_html,
                                                                    ab_campaign_subjects[index],
                                                                    ready_email_status,
                                                                    segment_id,
                                                                    campaign_type,
                                                                    ab_campaign_id=ab_campaign_ids[index])
                                        else:
                                            ready_email_status = "READY_TO_SEND"
                                            ready_to_send_emails_helper_obj. \
                                                add_ready_to_emails(email_address,
                                                                    template_html,
                                                                    ab_campaign_subjects[index],
                                                                    ready_email_status,
                                                                    segment_id,
                                                                    campaign_type,
                                                                    ab_campaign_id=ab_campaign_ids[index])

                                    processing_status = 'QUEUED'
                                    ab_campaigns_helper_obj. \
                                        update_email_configration_status(ab_campaign_ids[index],
                                                                         processing_status)
                                    ab_campaigns_helper_obj. \
                                        update_email_configration_queued_time(parent_ab_campaign_id,
                                                                              processing_status,
                                                                              QUEUED_TIME)
                # break
            except Exception as e:
                logging.warning('AB campaign inner try Exception: %s' % e)
                logging.warning(traceback.format_exc())

    except Exception as e:
        logging.warning('AB Campaign Exception: %s' % e)
        logging.warning(traceback.format_exc())


@app.task(name="send_emails")
def send_emails():
    try:
        ready_to_send_emails_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()

        ready_to_send_emails_records = ready_to_send_emails_obj.get_all_ready_to_send_emails()
        for emails_records in ready_to_send_emails_records:
            try:
                email_address = emails_records['email_address']
                campaign_id = emails_records['campaign_id']
                get_status = ready_to_send_emails_obj.get_campaign_status(campaign_id)
                status = get_status[0]['status']
                if status == "PAUSE":
                    continue
                if not ready_to_send_emails_obj. \
                        check_if_email_already_queued(email_address,
                                                      campaign_id):
                    ready_to_send_emails_obj. \
                        update_ready_to_send_status(campaign_id,
                                                    email_address, "QUEUED")

                    template_html = emails_records['template_html']
                    subject = emails_records['subject']
                    segment_id = emails_records['list_segment_id']
                    list_id = emails_records['list_id']
                    template_id = emails_records['templates_id']

                    # call send email
                    send_email.delay(template_html, email_address,
                                     list_id, segment_id,
                                     template_id, campaign_id, subject)

                    # my_sql_cursor.commit()
            except Exception as e:
                # my_sql_cursor.rollback()
                logging.warning(e)
    except Exception as e:
        logging.warning(e)


@app.task(name="send_email")
def send_email(html, email_address, list_id, segment_id,
               template_id, campaign_id, subject):
    email_result_obj = email_result.EmailResultHelper()

    ready_to_send_emails_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()

    list_segment_id = segment_id
    try:
        email_address = email_address

        logging.warning('[celery email Address] %s' % email_address)

        configuration = pytracking.Configuration(
            base_open_tracking_url=EMAIL_OPEN_URL,
            base_click_tracking_url=EMAIL_CLICK_URL,
            include_webhook_url=False)

        html = adapt_html(html,
                          extra_metadata={"template_id": template_id,
                                          "segment_id": segment_id,
                                          "campaign_id": campaign_id,
                                          "ab_campaign_id": None},
                          click_tracking=True,
                          open_tracking=True,
                          configuration=configuration)

        unsubscribe_url = "%s/%s/%s/" % (EMAIL_UNSUBSCRIBE, segment_id, campaign_id)
        html = html.replace("EMAIL_UNSUBSCRIBE_URL", unsubscribe_url)

        if USE_AWS_EMAIL_SERVER:
            mail_obj = Email(email_address, subject, html)
            mail_obj.send()
        # else:
        #     # set up the SMTP server
        #     smtp_email_obj = SmtpEmail(email_address, subject, html)
        #     smtp_email_obj.send()

        logging.warning('mail is sent successfully')

        email_result_obj.create_email_result(list_id,
                                             list_segment_id, template_id,
                                             "SENT", "SUCCESS", campaign_id=campaign_id,
                                             ab_campaign_id=None)

        ready_to_send_emails_obj.update_ready_to_send_status(campaign_id,
                                                             email_address,
                                                             "SENT")
        # my_sql_cursor.commit()
        logging.warning('Mail is sent successfully')
    except Exception as e:
        # my_sql_cursor.rollback()

        try:
            email_result_obj.create_email_result(list_id,
                                                 list_segment_id,
                                                 template_id,
                                                 "ERROR", "ERROR",
                                                 campaign_id=campaign_id,
                                                 ab_campaign_id=None)
            ready_to_send_emails_obj. \
                update_ready_to_send_status(campaign_id,
                                            email_address, "ERROR")
            # my_sql_cursor.commit()

        except:
            pass

        logging.warning('[Tasks] :: send_email() :: Got exception: %s' % e)
        logging.warning(traceback.format_exc())


@app.task(name="send_ab_emails")
def send_ab_emails():
    try:
        ready_to_send_emails_helper_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()

        ready_to_send_emails_records = ready_to_send_emails_helper_obj.get_all_ready_to_ab_send_emails()

        for emails_records in ready_to_send_emails_records:
            try:
                email_address = emails_records['email_address']
                ab_campaign_id = emails_records['ab_campaign_id']
                # status = emails_records['status']
                get_parent_id = ready_to_send_emails_helper_obj.get_ab_campaign_parent(ab_campaign_id)
                parent_id = 0
                for parent_ids in get_parent_id:
                    parent_id = parent_ids['ab_campaign_parent_id']

                get_status = ready_to_send_emails_helper_obj.get_ab_campaign_status(parent_id)
                status = ''
                for parent_status in get_status:
                    status = parent_status['status']

                if status == "PAUSE":
                    continue

                if not ready_to_send_emails_helper_obj.check_if_ab_email_already_queued(email_address,
                                                                                        ab_campaign_id):
                    ready_to_send_emails_helper_obj.update_ab_ready_to_send_status(ab_campaign_id,
                                                                                   email_address, "QUEUED")

                    template_html = emails_records['template_html']
                    subject = emails_records['subject']
                    segment_id = emails_records['list_segment_id']
                    list_id = emails_records['list_id']
                    template_id = emails_records['templates_id']

                    # call send email
                    send_ab_email.delay(template_html, email_address,
                                        list_id, segment_id,
                                        template_id, ab_campaign_id, subject)

                    # my_sql_cursor.commit()
            except Exception as e:
                # my_sql_cursor.rollback()
                logging.warning(e)
    except Exception as e:
        logging.warning(e)


@app.task(name="ab_send_email")
def send_ab_email(html, email_address, list_id, segment_id,
                  template_id, ab_campaign_id, subject):
    email_result_obj = email_result.EmailResultHelper()

    ready_to_send_emails_helper_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()

    list_segment_id = segment_id
    try:
        email_address = email_address

        logging.warning('[celery email Address] %s' % email_address)

        email_tracking_obj = EmailTracking()
        open_url = email_tracking_obj.email_encoding(template_id, ab_campaign_id, segment_id)

        configuration = pytracking.Configuration(
            base_open_tracking_url=EMAIL_OPEN_URL,
            base_click_tracking_url=EMAIL_CLICK_URL,
            include_webhook_url=False)

        html = adapt_html(html,
                          extra_metadata={"template_id": template_id,
                                          "segment_id": segment_id,
                                          "ab_campaign_id": ab_campaign_id,
                                          "campaign_id": None},
                          click_tracking=True,
                          open_tracking=True,
                          configuration=configuration)

        unsubscribe_url = "%s/%s/%s/" % (EMAIL_UNSUBSCRIBE, segment_id, ab_campaign_id)
        html = html.replace("EMAIL_UNSUBSCRIBE_URL", unsubscribe_url)

        if USE_AWS_EMAIL_SERVER:
            mail_obj = Email(email_address, subject, html)
            mail_obj.send()
        # else:
        #     # set up the SMTP server
        #     smtp_email_obj = SmtpEmail(email_address, subject, html)
        #     smtp_email_obj.send()

        logging.warning('mail is sent successfully')

        email_result_obj.create_email_result(list_id, list_segment_id,
                                             template_id,
                                             "SENT", "SUCCESS",
                                             campaign_id=None,
                                             ab_campaign_id=ab_campaign_id)

        ready_to_send_emails_helper_obj.update_ab_ready_to_send_status(ab_campaign_id,
                                                                       email_address,
                                                                       "SENT")
        # my_sql_cursor.commit()
        logging.warning('Mail is sent successfully')
    except Exception as e:
        # my_sql_cursor.rollback()

        try:
            email_result_obj.create_ab_email_result(list_id, list_segment_id,
                                                    template_id,
                                                    "ERROR", "ERROR",
                                                    campaign_id=None,
                                                    ab_campaign_id=ab_campaign_id)
            ready_to_send_emails_helper_obj. \
                update_ready_to_send_status(ab_campaign_id,
                                            email_address, "ERROR")
            # my_sql_cursor.commit()

        except:
            pass

        logging.warning('[Tasks] :: send_email() :: Got exception: %s' % e)
        logging.warning(traceback.format_exc())


def build_template(templateId):
    template_helper = templates.Templates()

    app_static_path = APP_STATIC

    file_path = '%s/%s' % (app_static_path, 'email_template')
    template_obj = template_helper.get_template_by_id(templateId)

    template_name = template_obj['path']
    template_path = file_path + template_name

    with open(r'%s' % template_path, 'r') as f:
        template_content = f.read()

    html_template = Template(template_content)

    template_vars_data = template_helper.get_template_vars_by_template_id(templateId)

    key_val = {}
    for vars_data in template_vars_data:
        template_key = vars_data['template_key']
        template_value = vars_data['template_value']
        if template_key not in key_val:
            key_val[template_key] = ""

        key_val[template_key] = template_value

    html = html_template.substitute(key_val)
    return html

