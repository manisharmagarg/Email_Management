from emailapp.decorate import login_required
import os

from emailapp.sql_helpers import templates, authenticate, user, lists, \
    campaign_helper, campaign_stats, system_emails, emails_unsubscribe, \
    ab_campaigns_helper, email_result
from emailapp import app, session, request, redirect, render_template, \
    bcrypt, url_for, jsonify

from conf.config import PYTRACKING_SECRET_KEY, EMAIL_OPEN_URL, \
    EMAIL_CLICK_URL, APP_STATIC, EMAIL_UNSUBSCRIBE
from emailapp.tracking.email_tracking import EmailTracking
import json
from string import Template
from emailapp.helpers.smtp_email import SmtpEmail
from datetime import datetime
import pytracking
import traceback
import socket

template_helper = templates.Templates()
user_authenticate = authenticate.Authenticate()
email_user = user.User()
list_helper = lists.Lists()
campaign_stats_helper = campaign_stats.CampaignStatsHelper()
track_email = EmailTracking()
system_emails_obj = system_emails.SystemEmailsHelper()
# smtp_email_obj = smtp_email.SmtpEmail()
email_notification_obj = email_result.EmailResultHelper()
email_unsubscribe_helper_obj = emails_unsubscribe.EmailUnsubscribeHelper()
ab_campaigns_helper_obj = ab_campaigns_helper.AbCampaignsHelper()


def register():
    try:
        if request.method == 'POST':
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            email = request.form['email']
            password = request.form['password']

            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user_authenticate.create_account(firstname, lastname, email,
                                             pw_hash)
            return redirect('/login/')
        return render_template('register.html')
    except Exception as exp:
        app.logger.warning(exp)
        context = {"msg": "Email already used"}
        return render_template('register.html', **context)


def login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = user_authenticate.authenticate(email)
            pw_hash = user['password']
            auth = bcrypt.check_password_hash(pw_hash, password)
            if auth:
                session['user'] = user['id']
                session['email'] = email
                session['firstname'] = user['firstname']
                session['lastname'] = user['lastname']
                app.logger.info('login successfull')
                return redirect("/campaigns/")
            else:

                msg = {'msg': "Invalid email/password"}
                return render_template('login.html', **msg)
        return render_template('login.html')
    except Exception as e:
        app.logger.warning(e)
        app.logger.warning(traceback.format_exc())
        msg = {'msg': "Invalid email/password"}
        return render_template('login.html', **msg)


@login_required
def create_user():
    ret = {}
    try:
        if request.method == 'POST':
            name = request.json.get('name')
            email = request.json.get('email')
            user_id = request.json.get('user_id')
            email_user.insert_email_user(name, email, user_id)
            ret['Success'] = True
            ret['Message'] = "EMAIL SENT"
    except Exception as e:
        ret['Success'] = True
        ret['error'] = '%s' % e
        app.logger.warning(e)
    return json.dumps(ret)


@login_required
def delete_user(list_segment_id, list_id):
    try:
        segment = list_helper.get_list_by_id(list_id, request.user)
        id = segment['id']
        name = segment['list_name']
        list_helper.delete_listsegment(list_segment_id)
        user = email_user.get_email_user()

        if request.method == 'POST':
            first = request.form['first']
            from_first = int(first) - 1
            last = request.form['last']
            data = email_user.get_email_user()

            if first and last:
                dal = data[int(from_first):int(last)]

                mails = []
                for filter in dal:
                    filter_data = filter['email']
                    emails = list_helper.check_exist_emails(filter_data, id)

                    if emails:
                        app.logger.info(emails)

                    else:
                        list_helper.add_list_by_id(filter_data, id)

                if mails:
                    context = {'data': email_user.get_email_user(),
                               "segment_name": name, "segment_id": id,
                               'message': mails}
                    return render_template('segments/segment.html', **context)
                    # return "mails are already exists"
                else:
                    return redirect('/segments/')

        context = {"data": list_helper.get_list_segment_by_listid(list_id),
                   "users": user,
                   "segment_name": name,  "segment_id": id}
        return render_template('segments/segment.html', **context)
    except Exception as e:
        app.logger.warning('[Accounts] :: delete_user() :: '
                           'Got exception: %s' % e)


@login_required
def signout():
    session.clear()
    return redirect('/login/')


def email_opened(params):
    try:
        url = '%s/%s' % (EMAIL_OPEN_URL, params)
        app.logger.info(PYTRACKING_SECRET_KEY)
        full_url = url
        tracking_result = pytracking.get_open_tracking_result(
            full_url, base_open_tracking_url=EMAIL_OPEN_URL)

        campaign_id = tracking_result.metadata['campaign_id']
        ab_campaign_id = tracking_result.metadata['ab_campaign_id']
        template_id = tracking_result.metadata['template_id']
        segment_id = tracking_result.metadata['segment_id']

        hostname = socket.gethostname()

        IPAddress = socket.gethostbyname(hostname)

        campaign_stats_helper.\
            add_campaign_open_stats(segment_id,
                                    template_id,
                                    tracking_result.is_open_tracking,
                                    0,
                                    '',
                                    IPAddress,
                                    campaign_id=campaign_id,
                                    ab_campaign_id=ab_campaign_id)

        return "OK"
    except Exception as e:
        app.logger.warning(e)
        return e


def click_tracking(params):
    try:
        url = '%s/%s' % (EMAIL_CLICK_URL, params)
        full_url = url
        tracking_result = pytracking.get_click_tracking_result(
            full_url, base_click_tracking_url=EMAIL_CLICK_URL)
        campaign_id = tracking_result.metadata['campaign_id']
        ab_campaign_id = tracking_result.metadata['ab_campaign_id']
        template_id = tracking_result.metadata['template_id']
        segment_id = tracking_result.metadata['segment_id']

        campaign_stats_helper.\
            add_campaign_click_stats(segment_id,
                                     template_id,
                                     0, tracking_result.is_click_tracking,
                                     tracking_result.tracked_url,
                                     campaign_id=campaign_id,
                                     ab_campaign_id=ab_campaign_id)
        app.logger.info(tracking_result)

        app.logger.info(segment_id)
        app.logger.info(campaign_id)
        app.logger.info(ab_campaign_id)

        return redirect(tracking_result.tracked_url)

    except Exception as e:
        app.logger.warning(e)
        app.logger.warning(traceback.format_exc())


def email_unsubscribe(segment_id, campaign_id):
    segment_email = list_helper.get_email_by_segment_id(segment_id)
    email_address = segment_email[0]['email']
    id = email_unsubscribe_helper_obj.\
        create_email_unsubscribe(email_address, campaign_id)
    app.logger.info(id)
    return render_template('unsubscribe_template.html')


def send_system_email():
    ret = {}
    try:
        user_id = request.json.get('user_id')
        email_type = request.json.get('email_type')

        template = template_helper.get_template_by_name(email_type)
        status = "ACTIVE"

        templateId = template['id']

        if not template:
            return jsonify("Email template not found")
        email_address = 'anaconda.wb@gmail.com'
        subject = 'smtp_email'
        html = build_template(templateId)

        smtp_email_obj = SmtpEmail(email_address, subject, html)

        smtp_email_obj.send()
        system_emails_obj.insert_system_emails(user_id, email_type, status)
        ret['message'] = "EMAIL SENT"
    except Exception as e:
        ret['error'] = '%s' % e
        app.logger.warning(e)
    return json.dumps(ret)


def build_template(templateId):

    app_static_path = APP_STATIC

    file_path = '%s/%s' % (app_static_path, 'email_template')

    template_obj = template_helper.get_template_by_id(templateId)
    template_name = template_obj['path']
    template_path = file_path + template_name
    with open(r'%s' % template_path, 'r') as f:
        template_content = f.read()

    html_template = Template(template_content)
    template_vars_data = template_helper.\
        get_template_vars_by_template_id(templateId)

    key_val = {}
    for vars_data in template_vars_data:
        template_key = vars_data['template_key']
        template_value = vars_data['template_value']
        if template_key not in key_val:
            key_val[template_key] = ""

        key_val[template_key] = template_value

    html = html_template.substitute(key_val)
    return html


def bounce():
    response = {}
    try:
        data = email_notification_obj.get_bounce_notifications()
        response["data"] = data
    except:
        response["Success"] = True
        response["Message"] = "some thing is wrong!"
    return json.dumps(response)


def reject():
    response = {}
    try:
        data = email_notification_obj.get_reject_notifications()
        response["data"] = data
    except:
        response["Success"] = True
        response["Message"] = "some thing is wrong!"
    return json.dumps(response)


def notifications():
    response = {}
    data = request.json
    try:
        message = data['Message']
        notification_type = message['notificationType']

        if notification_type:
            if notification_type == "Delivery":
                notification_type = message['notificationType']
                mail = message['mail']
                delivery = message['delivery']
                destination = mail['destination']
                headers = mail['headers']

                subject = ''
                for data in headers:
                    name = data['name']
                    if name == "Subject":
                        subject = data['value']

                email_address = destination[0]
                source_address = mail['source']
                source_arn = mail['sourceArn']
                source_ip = mail['sourceIp']
                sending_account_id = mail['sendingAccountId']

                send_timestamp = mail['timestamp']
                message_id = mail['messageId']

                remoteMtaIp = delivery['remoteMtaIp']

                check_message_id = email_notification_obj.check_delivery_message_id(message_id)
                if not check_message_id:

                    for index, val in enumerate(destination):
                        email_notification_obj.insert_delivery_notifications(notification_type, val, source_address,
                                                                             source_arn, source_ip, sending_account_id, remoteMtaIp,
                                                                             send_timestamp, message_id, subject)

            elif notification_type == "Bounce":
                notification_type = message['notificationType']
                mail = message['mail']
                bounce = message['Bounce']
                destination = mail['destination']
                headers = mail['headers']
                print(headers)

                subject = ''
                for data in headers:
                    name = data['name']
                    if name == "Subject":
                        subject = data['value']

                source_address = mail['source']
                source_arn = mail['sourceArn']
                source_ip = mail['sourceIp']
                sending_account_id = mail['sendingAccountId']

                send_timestamp = mail['timestamp']
                message_id = mail['messageId']

                remoteMtaIp = bounce['remoteMtaIp']

                check_message_id = email_notification_obj.check_bounce_message_id(message_id)
                if not check_message_id:
                    for index, val in enumerate(destination):
                        email_notification_obj.insert_bounce_notifications(notification_type, val, source_address,
                                                                           source_arn, source_ip, sending_account_id, remoteMtaIp,
                                                                           send_timestamp, message_id, subject)

            elif notification_type == "Complaint":
                notification_type = message['notificationType']
                mail = message['mail']
                destination = mail['destination']
                headers = mail['headers']

                subject = ''
                for data in headers:
                    name = data['name']
                    if name == "Subject":
                        subject = data['value']

                source_address = mail['source']
                source_arn = mail['sourceArn']
                source_ip = mail['sourceIp']
                sending_account_id = mail['sendingAccountId']

                send_timestamp = mail['timestamp']
                message_id = mail['messageId']

                check_message_id = email_notification_obj.check_complaint_message_id(message_id)
                if not check_message_id:

                    for index, val in enumerate(destination):

                        email_notification_obj.insert_complaint_notifications(notification_type, val, source_address,
                                                                              source_arn, source_ip, sending_account_id,
                                                                              send_timestamp, message_id, subject)
        response["Success"] = True
        response["Message"] = "Saved data successfully!"
    except:
        response["Success"] = True
        response["Message"] = "Not receive json data"

    return json.dumps(response)
