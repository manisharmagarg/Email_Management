import traceback
import json
import math
from struct import *
import random
from emailapp.decorate import login_required
from emailapp.sql_helpers import templates, authenticate, user, lists, \
    campaign_helper, email_result, ready_to_send_email_helper, \
    campaign_stats, campaign_winning_combination, emails_unsubscribe, \
    campaign_setup, email_subject, ab_campaigns_helper
from emailapp import app, session, request, redirect, render_template, \
    url_for, jsonify
from conf.config import EMAIL_OPEN_URL, APP_ROOT, APP_STATIC
from datetime import datetime, timedelta


campaign_stats_helper = campaign_stats.CampaignStatsHelper()
template_helper = templates.Templates()
user_authenticate = authenticate.Authenticate()
campaign_helper_obj = campaign_helper.CampaignHelper()
email_result_helper = email_result.EmailResultHelper()
ready_to_send_email_helper_obj = ready_to_send_email_helper.\
    ReadyToSendEmailsHelper()
email_user = user.User()
list_helper = lists.Lists()
campaign_winning_helper = campaign_winning_combination.CampaignWinningHelper()
emails_unsubscribe_obj = emails_unsubscribe.EmailUnsubscribeHelper()

campaign_setup_obj = campaign_setup.CampaignSetupHelper()
email_subject_obj = email_subject.EmailSubjectHelper()
ab_campaigns_helper_obj = ab_campaigns_helper.AbCampaignsHelper()


@login_required
def campaigns():
    email_campaign = campaign_helper_obj.get_campaigns()
    email_ab_campaign = ab_campaigns_helper_obj.get_all_ab_campaign()
    email_campaigns = []
    email_campaign_data = []
    email_ab_campaign_data = []

    for item in email_campaign:

        id = item['id']
        name = item['name']
        campaign_type = item['campaign_type']
        status = item['status']
        campaign_state = item['campaign_state']

        list_id = item['list_id']
        send_emails = len(ready_to_send_email_helper_obj.get_send_emails(id))
        unsubscribe_emails = len(ready_to_send_email_helper_obj.get_unsubscribe_emails(id))
        send_unsubscribe_emails = send_emails + unsubscribe_emails
        total_emails = int(list_helper.get_listsegment_count(list_id))
        average = 0
        if send_unsubscribe_emails:
            avg = (send_unsubscribe_emails*100)/total_emails
            average = int(math.trunc(avg))

        campaign_data = {"id": id, "name": name, "campaign_type": campaign_type,
                         "status": status, "campaign_state": campaign_state,
                         "average": average}
        email_campaign_data.append(campaign_data)
        email_campaigns.append(campaign_data)

    # ab_campaign work

    child_campaign = []
    for ab_data in email_ab_campaign:
        child_id = []
        id = ab_data['id']
        name = ab_data['name']
        campaign_state = ab_data['campaign_state']
        status = ab_data['status']
        campaign_type = ab_data['campaign_type']
        list_id = ab_data['list_id']
        parent_count = ab_data['ab_campaign_count']
        test_percentage = ab_data['test_percentage']
        ab_camapign = ab_campaigns_helper_obj.get_ab_campagin_by_id(id)

        if status == 'QUEUED' or status == 'PAUSE':
            send_emails = 0
            unsubscribe_emails = 0
            total_emails = 0
            for ab in ab_camapign:
                # child_id = []
                ab_id = ab['id']
                child_id.append(ab['id'])
                child_campaign.append(child_id)
                send_email = len(ready_to_send_email_helper_obj.get_ab_campaign_send_emails(ab_id))
                unsubscribe_email = len(ready_to_send_email_helper_obj.get_ab_unsubscribe_emails(ab_id))
                total_emails_data = int(list_helper.get_listsegment_count(list_id))
                total_emails_data_per = (total_emails_data * test_percentage)/100
                total_emails_data_per_trunc = int(math.trunc(total_emails_data_per))
                per_combination_emails = int(total_emails_data_per_trunc)/int(parent_count)
                trunc_per_combination_emails = int(math.trunc(per_combination_emails))
                total_emails = trunc_per_combination_emails*int(parent_count)

                # get total emails from the segment
                send_emails += send_email
                unsubscribe_emails += unsubscribe_email

            ab_send_unsubscribe_emails = send_emails + unsubscribe_emails
            average = 0
            if ab_send_unsubscribe_emails:
                avg = (ab_send_unsubscribe_emails * 100) / total_emails
                average = int(math.trunc(avg))

            ab_campaign_data = {"id": id, "name": name, "campaign_type": campaign_type,
                                "status": status, "campaign_state": campaign_state,
                                "average": average
                                }
        else:
            ab_campaign_data = {"id": id, "name": name, "campaign_type": campaign_type,
                                "status": status, "campaign_state": campaign_state
                                }
        email_ab_campaign_data.append(ab_campaign_data)
        email_campaigns.append(ab_campaign_data)

    # all_campaigns = sorted(email_campaigns, key=lambda x: x['status'], reverse=True)

    context = {'email_campaigns': email_campaigns,
               'One_time': email_campaign_data,
               'AB_test': email_ab_campaign_data}
    return render_template('campaigns/campaigns.html', **context)


@login_required
def create_campaigns():
    user_id = request.user
    list_data = list_helper.get_list(user_id)
    if not list_data:
        list_name = 'All Users'
        list_id = list_helper.create_list(list_name, request.user)
        user = email_user.get_email_user()
        for emails in user:
            list_helper.add_list_by_id(emails['email'], list_id)
    return render_template('campaigns/create_campaigns.html')


@login_required
def one_time_campaign_setup(campaign_id=None, params=None):
    user_id = request.user
    lst_data = []
    status = 'ACTIVE'
    campaign_type = ''
    list_data = list_helper.get_list(user_id)

    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)

    if campaign_id is None:
        name = ""
        list_id = ""
        list_name = "Choose a list of recipients"
        type = ''
    else:
        campaigns = campaign_helper_obj.get_campaign_by_id_and_status(campaign_id, params)

        if campaigns:

            name = campaigns['name']
            list_id = campaigns['list_id']
            type = campaigns['type']
            campaign_type = campaigns['campaign_type']
            data = list_helper.get_list_name_by_listid(list_id)
            list_name = data['list_name']
        else:

            parent_campaign = ab_campaigns_helper_obj.get_ab_parent_campaign(campaign_id)
            name = parent_campaign['name']
            type = parent_campaign['type']
            list_id = parent_campaign['list_id']
            campaign_type = parent_campaign['campaign_type']
            list_data = list_helper.get_list_name_by_listid(list_id)
            list_name = list_data['list_name']
            count = list_helper.get_listsegment_count(list_id)

    if request.method == 'POST':
        toggle_value = request.form.get('toggle_data')
        campaign_name = request.form['campaign_name']
        list_id = request.form['list_id']
        if not campaign_id:
            if toggle_value is None:
                type = 'one-time'
                campaign_type = 'One-time'
                campaign_id = campaign_helper_obj\
                    .create_campaign(campaign_name, status,
                                     type,
                                     user_id, templates_id=None,
                                     campaign_type=campaign_type,
                                     list_id=list_id, send_time=None,
                                     email_subject=None, preview_text=None,
                                     percentage=None, is_ab_campaign=False,
                                     parent_campaign_id=None)

                return redirect(url_for('route_subject_line',
                                        campaign_id=campaign_id))
            else:
                type = 'one-time'
                campaign_type = 'AB_Test'
                ab_campaign_parent_id = ab_campaigns_helper_obj. \
                    create_ab_campaigns_parent(campaign_name, list_id,
                                               user_id, campaign_type,
                                               status, type,
                                               percentage=None,
                                               rate=None, time_after=None,
                                               time_type=None, ab_campaign_count=None)

                return redirect(url_for('route_ab_test',
                                        campaign_id=ab_campaign_parent_id))

        else:
            campaign_type = 'One-time'
            if toggle_value is None:
                toggle_value = 'One-time'
            else:
                toggle_value = 'AB_Test'
            if toggle_value == params:
                data = campaign_helper_obj.get_campaign_by_id_and_status(campaign_id, params)
                if data:
                    campaign_helper_obj.update_campaign(list_id, campaign_name,
                                                        campaign_id, campaign_type,
                                                        state=None)
                    return redirect(url_for('route_subject_line',
                                            campaign_id=campaign_id))
                else:
                    ab_campaigns_helper_obj.update_ab_parent_campaign(campaign_id,
                                                                      campaign_name,
                                                                      list_id)
                    return redirect(url_for('route_ab_test', campaign_id=campaign_id))
            else:
                if params == 'One-time':
                    campaign_helper_obj.delete_campaigns(campaign_id)
                    type = 'one-time'
                    campaign_type = 'AB_Test'
                    ab_campaign_parent_id = ab_campaigns_helper_obj. \
                        create_ab_campaigns_parent(campaign_name, list_id,
                                                   user_id, campaign_type,
                                                   status, type,
                                                   percentage=None,
                                                   rate=None, time_after=None,
                                                   time_type=None, ab_campaign_count=None)

                    return redirect(url_for('route_ab_test',
                                            campaign_id=ab_campaign_parent_id))
                else:
                    ab_campaigns_helper_obj.delete_ab_campaigns(campaign_id)
                    type = 'one-time'
                    campaign_type = 'One-time'
                    campaign_id = campaign_helper_obj \
                        .create_campaign(campaign_name, status,
                                         type,
                                         user_id, templates_id=None,
                                         campaign_type=campaign_type,
                                         list_id=list_id, send_time=None,
                                         email_subject=None, preview_text=None,
                                         percentage=None, is_ab_campaign=False,
                                         parent_campaign_id=None)

                    return redirect(url_for('route_subject_line',
                                            campaign_id=campaign_id))

    context = {'list_data': lst_data, 'name': name, 'list_name': list_name,
               'list_id': list_id, 'type': type, 'campaign_type': campaign_type}
    return render_template('campaigns/one_time_campaign_setup.html',
                           **context)


@login_required
def subject_line(campaign_id=None):
    state = 'DRAFT'
    user_id = request.user
    get_campaign = campaign_helper_obj.get_campaign_by_id(campaign_id)
    data = get_campaign['email_subject']
    campaign_state = get_campaign['campaign_state']
    campaign_type = get_campaign['campaign_type']
    type = get_campaign['type']
    if campaign_state == 'PUBLISHED':
        state = 'PUBLISHED'

    if data is None:
        emails_subject = ''
        preview_text = ''
    else:
        emails_subject = get_campaign['email_subject']
        preview_text = get_campaign['preview_text']

    if request.method == 'POST':
        email_subject = request.form['email_subject']
        preview_text_subject = request.form['preview_text_subject']

        campaign_helper_obj.update_campaign_setup(campaign_id,
                                                  email_subject,
                                                  preview_text_subject,
                                                  state)

        return redirect(url_for('route_content_templates_by_id',
                                campaign_id=campaign_id))
    context = {'emails_subject': emails_subject, 'type': type, 'campaign_type': campaign_type,
               'preview_text': preview_text, 'campaign_id': campaign_id}
    return render_template('campaigns/subject_line.html', **context)


@login_required
def content_templates(campaign_id=None):

    user_id = request.user
    campaign_type = 'One-time'
    templates = template_helper.get_templates()
    campaign = campaign_helper_obj.get_campaign_by_id(campaign_id)
    template_id = campaign['templates_id']
    if template_id is None:
        path = ""
        name = "Select a template"
        template_id = ""
    else:

        template = template_helper.get_template_by_id(template_id)
        path = template['path']
        name = template['name']

    if request.method == 'POST':
        template_id = request.form['template_id']

        campaign_helper_obj.update_template(campaign_id, template_id)

        return redirect(url_for('route_send_time_by_id',
                                campaign_id=campaign_id))
    context = {"template": templates, "template_id": template_id,
               "path": path, "name": name}
    return render_template('campaigns/content_templates.html', **context)


@login_required
def send_time(campaign_id=None):

    state = 'PUBLISHED'
    campaign = campaign_helper_obj.get_campaign_by_id(campaign_id)
    send_time = campaign['send_time']
    time_data = ''
    time = ''
    hour = ''
    hour_data = ''
    hour_value = ''
    min_value = ''
    zone = ''
    if send_time is None:
        pass
    else:
        time_data = send_time.split(" ")
        time = time_data[0]+" "+time_data[1]+" "+time_data[2]
        hour = time_data[3]
        hour_data = hour.split(":")
        hour_value = hour_data[0]
        min_value = hour_data[1]
        zone = time_data[4]
    hours = []
    for i in range(1, 13):
        hours.append(i)
    mins = []
    for min in range(0, 60):
        mins.append(min)

    if request.method == 'POST':
        date = request.form['date']
        hours = request.form['hours']
        min = request.form['min']
        time_zone = request.form['time_zone']

        send_time = date + (' %s' % hours) + ':' + min + (' %s' % time_zone)
        campaign_helper_obj.update_send_time(campaign_id, send_time, state)

        return redirect('/campaigns/')

    context = {'hours': hours, 'mins': mins, 'time_value': time, 'hour_value': hour_value,
               'min_value': min_value, 'zone_value': zone}
    return render_template('campaigns/send_time.html', **context)


def campaign_pause():
    if request.method == "POST":
        params = request.form.get('params')
        campaign_id = request.form.get('id')
        if params == 'One-time':
            if not campaign_helper_obj.get_status_by_id(campaign_id):
                campaign_helper_obj.update_email_configration_status(campaign_id, 'PAUSE')
                return 'PAUSED'

        else:
            if not ab_campaigns_helper_obj.get_status_by_id(campaign_id):
                ab_campaigns_helper_obj.update_parent_campaign_status(campaign_id, 'PAUSE')
                return 'PAUSED'
    return 'PROCESSED'


def campaign_resume():
    if request.method == "POST":
        params = request.form.get('params')
        campaign_id = request.form.get('id')
        if params == 'One-time':
            campaign_helper_obj.update_email_configration_status(campaign_id, "QUEUED")
        else:
            ab_campaigns_helper_obj.update_parent_campaign_status(campaign_id, "QUEUED")
    return 'RESUME'


###############################
#          A/B Testing        #
###############################
@login_required
def one_time_campaign_create(campaign_id=None, params=None):

    user_id = request.user
    list_data = list_helper.get_list(user_id)

    lst_data = []
    status = 'ACTIVE'
    campaign_type = ''

    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)
    name = ''
    list_name = ''
    count = ''
    list_id = ''
    type = ''
    if campaign_id is None:
        name = ""
        list_id = ""
        list_name = "Choose a list of recipients"
        toggle_value = ''

    else:
        parent_campaign = ab_campaigns_helper_obj.get_ab_parent_campaigns(campaign_id, params)

        if parent_campaign:
            name = parent_campaign['name']
            type = parent_campaign['type']
            list_id = parent_campaign['list_id']
            campaign_type = parent_campaign['campaign_type']
            list_data = list_helper.get_list_name_by_listid(list_id)
            list_name = list_data['list_name']
            count = list_helper.get_listsegment_count(list_id)
        else:
            campaigns = campaign_helper_obj.get_campaign_by_id(campaign_id)
            name = campaigns['name']
            list_id = campaigns['list_id']
            type = campaigns['type']
            campaign_type = campaigns['campaign_type']
            data = list_helper.get_list_name_by_listid(list_id)
            list_name = data['list_name']

    if request.method == 'POST':
        toggle_value = request.form.get('toggle_data')
        campaign_name = request.form['campaign_name']
        list_id = request.form['list_id']

        if not campaign_id:
            if toggle_value:
                type = 'Reoccuring'
                campaign_type = 'AB_Test'
                ab_campaign_parent_id = ab_campaigns_helper_obj.\
                    create_ab_campaigns_parent(campaign_name, list_id,
                                               user_id, campaign_type,
                                               status, type,
                                               percentage=None,
                                               rate=None, time_after=None,
                                               time_type=None, ab_campaign_count=None)

                return redirect(url_for('route_ab_test',
                                        campaign_id=ab_campaign_parent_id))
            else:
                type = 'Reoccuring'
                campaign_type = 'One-time'
                toggle_value = False
                campaign_id = campaign_helper_obj \
                    .create_campaign(campaign_name, status, type,
                                     user_id, templates_id=None,
                                     campaign_type=campaign_type,
                                     list_id=list_id, send_time=None,
                                     email_subject=None, preview_text=None,
                                     percentage=None, is_ab_campaign=False,
                                     parent_campaign_id=None)

                return redirect(url_for('route_subject_line',
                                        campaign_id=campaign_id))
        else:
            if toggle_value is None:
                toggle_value = 'One-time'
            else:
                toggle_value = 'AB_Test'
            if toggle_value == params:
                if ab_campaigns_helper_obj.get_ab_parent_campaigns(campaign_id, params):
                    ab_campaigns_helper_obj.update_ab_parent_campaign(campaign_id,
                                                                      campaign_name,
                                                                      list_id)
                    return redirect(url_for('route_ab_test', campaign_id=campaign_id))
                else:
                    campaign_type = 'One-time'
                    campaign_helper_obj.update_campaign(list_id, campaign_name,
                                                        campaign_id, campaign_type,
                                                        state=None)
                    return redirect(url_for('route_subject_line',
                                            campaign_id=campaign_id))
            else:
                if params == 'One-time':
                    campaign_helper_obj.delete_campaigns(campaign_id)
                    type = 'one-time'
                    campaign_type = 'AB_Test'
                    ab_campaign_parent_id = ab_campaigns_helper_obj. \
                        create_ab_campaigns_parent(campaign_name, list_id,
                                                   user_id, campaign_type,
                                                   status, type,
                                                   percentage=None,
                                                   rate=None, time_after=None,
                                                   time_type=None, ab_campaign_count=None)

                    return redirect(url_for('route_ab_test',
                                            campaign_id=ab_campaign_parent_id))
                else:
                    ab_campaigns_helper_obj.delete_ab_campaigns(campaign_id)
                    type = 'one-time'
                    campaign_type = 'One-time'
                    campaign_id = campaign_helper_obj \
                        .create_campaign(campaign_name, status,
                                         type,
                                         user_id, templates_id=None,
                                         campaign_type=campaign_type,
                                         list_id=list_id, send_time=None,
                                         email_subject=None, preview_text=None,
                                         percentage=None, is_ab_campaign=False,
                                         parent_campaign_id=None)

                    return redirect(url_for('route_subject_line',
                                            campaign_id=campaign_id))

    context = {'list_data': lst_data, 'name': name, 'list_name': list_name,
               'campaign_type': campaign_type,
               'count': count, 'list_id': list_id, 'type': type}
    return render_template('campaigns/one_time_campaign_create.html',
                           **context)


@login_required
def ab_test(campaign_id=None):
    get_ab_campaigns = ab_campaigns_helper_obj.\
        get_ab_parent_campaign(campaign_id)

    list_id = get_ab_campaigns['list_id']
    campaign_type = get_ab_campaigns['campaign_type']
    test_percentage = get_ab_campaigns['test_percentage']
    test_variable = get_ab_campaigns['test_variable']

    type = get_ab_campaigns['type']
    if test_percentage is None:
        test_percentage = ''
        rate = 'Select rate'
        time_after = ''
        time_type = 'Select type'
        ab_campaign_count = ''
    else:
        test_percentage = get_ab_campaigns['test_percentage']
        rate = get_ab_campaigns['rate']
        time_after = get_ab_campaigns['time_after']
        time_type = get_ab_campaigns['time_type']
        ab_campaign_count = get_ab_campaigns['ab_campaign_count']

    segment_count = list_helper.get_listsegment_count(list_id)

    if request.method == 'POST':

        percentage = request.form['percentage']
        rate = request.form['rate']
        time_after = request.form['time_after']
        time_type = request.form['time_type']
        campaign_count = request.form.get('campaign_count')
        test_variable = request.form.get('filter')
        ab_campaigns_helper_obj.\
            update_ab_winning_cambination(campaign_id, percentage,
                                          test_variable, rate, time_after,
                                          time_type, campaign_count)
        return redirect(url_for('route_ab_subject_lines',
                                campaign_id=campaign_id))
    context = {'ab_campaigns_parent_id': campaign_id,
               'segment_count': segment_count, 'type': type,
               'test_percentage': test_percentage, 'rate': rate,
               'time_after': time_after, 'time_type': time_type,
               'ab_campaign_count': ab_campaign_count, 'campaign_type': campaign_type, 'filter': test_variable}
    return render_template('campaigns/ab_test.html', **context)


@login_required
def ab_subject_lines(campaign_id=None):
    status = 'ACTIVE'
    campaign_state = 'DRAFT'
    user_id = request.user

    parent_campaign_data = ab_campaigns_helper_obj.\
        get_ab_parent_campaign(campaign_id)
    ab_campaign_count = parent_campaign_data['ab_campaign_count']
    test_variable = parent_campaign_data['test_variable']

    get_ab_campaign = ab_campaigns_helper_obj.\
        get_ab_campagin_by_id(campaign_id)

    emails_subject = []
    preview_text = ''
    for ab in get_ab_campaign:
        child_id = ab['id']
        email_subject = ab['email_subject']
        preview_text = ab['preview_text']
        emails_subject.append(email_subject)

    if request.method == 'POST':
        email_subject_third = ''
        email_subject_first = request.form['email_first_subject']
        preview_text_subject = request.form['preview_text_subject']

        ab_campaign = ab_campaigns_helper_obj.\
            check_if_campaign_already_exist(campaign_id)

        if test_variable == 'subject_lines':
            if not ab_campaign:

                ab_campaigns_helper_obj.\
                    create_ab_campaigns(campaign_id, user_id,
                                        email_subject_first, preview_text_subject,
                                        status, campaign_state,
                                        templates_id=None,
                                        send_time=None)

                email_subject_second = request.form['email_second_subject']

                ab_campaigns_helper_obj. \
                    create_ab_campaigns(campaign_id, user_id,
                                        email_subject_second, preview_text_subject,
                                        status, campaign_state,
                                        templates_id=None,
                                        send_time=None)

                if ab_campaign_count == '3':
                    email_subject_third = request.form['email_third_subject']
                    ab_campaigns_helper_obj. \
                        create_ab_campaigns(campaign_id, user_id,
                                            email_subject_third,
                                            preview_text_subject,
                                            status, campaign_state,
                                            templates_id=None,
                                            send_time=None)
                ab_campaigns_helper_obj.update_parent_status(campaign_state,
                                                             campaign_id)
            else:
                emails_subjects = []
                email_subject_first = request.form['email_first_subject']
                email_subject_second = request.form['email_second_subject']
                preview_text_subject = request.form['preview_text_subject']
                email_subject_third = ''
                if ab_campaign_count == '3':
                    email_subject_third = request.form['email_third_subject']

                emails_subjects.insert(0, email_subject_first)
                emails_subjects.insert(1, email_subject_second)
                emails_subjects.insert(2, email_subject_third)
                child_campaign = []
                for AB_data in ab_campaign:
                    child_campaign_id = AB_data['id']
                    child_campaign.append(child_campaign_id)

                for index, val in enumerate(child_campaign):
                    ab_campaigns_helper_obj.\
                        update_ab_emails_subjects(val,
                                                  emails_subjects[index],
                                                  preview_text_subject)

            return redirect(url_for('route_ab_content_templates',
                                    campaign_id=campaign_id))
        else:
            if not ab_campaign:
                for i in range(1, int(ab_campaign_count)+1):
                    ab_campaigns_helper_obj. \
                        create_ab_campaigns(campaign_id, user_id,
                                            email_subject_first, preview_text_subject,
                                            status, campaign_state,
                                            templates_id=None,
                                            send_time=None)
                    ab_campaigns_helper_obj.update_parent_status(campaign_state,
                                                                         campaign_id)

            else:
                child_campaign = []
                for AB_data in ab_campaign:
                    child_campaign_id = AB_data['id']
                    child_campaign.append(child_campaign_id)
                for index, id in enumerate(child_campaign):

                    ab_campaigns_helper_obj. \
                        update_ab_emails_subjects(id,
                                                  email_subject_first,
                                                  preview_text_subject)

            return redirect(url_for('route_ab_content_templates',
                                    campaign_id=campaign_id))

    context = {'ab_campaign_count': ab_campaign_count,
               'emails_subject': emails_subject, 'preview_text': preview_text,
               'campaign_id': campaign_id, 'test_variable': test_variable}
    return render_template('campaigns/ab_subject_lines.html', **context)


@login_required
def ab_content_templates(campaign_id=None):

    user_id = request.user

    parent_campaign_data = ab_campaigns_helper_obj.\
        get_ab_parent_campaign(campaign_id)
    ab_campaign_count = parent_campaign_data['ab_campaign_count']
    test_variable = parent_campaign_data['test_variable']

    get_ab_campaign = ab_campaigns_helper_obj.\
        get_ab_campagin_by_id(campaign_id)

    email_templates = []
    email_templates_path = []
    email_templates_name = []
    template_first_id = ''
    template_second_id = ''
    template_third_id = ''
    template_first_name = ''
    template_second_name = ''
    template_third_name = ''
    template_first_path = ''
    template_second_path = ''
    template_third_path = ''
    preview_text = ''

    templates_id = ''
    for ab in get_ab_campaign:
        child_id = ab['id']
        templates_id = ab['templates_id']
        preview_text = ab['preview_text']
        if templates_id is None:
            template_first_name = 'Select a template'
            template_second_name = 'Select a template'
            template_third_name = 'Select a template'

        else:
            email_templates.append(templates_id)
            template = template_helper.get_template_by_id(templates_id)
            path = template['path']
            name = template['name']
            email_templates_path.append(path)
            email_templates_name.append(name)
    templates = template_helper.get_templates()

    if email_templates:
        template_first_id = email_templates[0]
        template_second_id = email_templates[1]

        template_first_path = email_templates_path[0]
        template_second_path = email_templates_path[1]

        template_first_name = email_templates_name[0]
        template_second_name = email_templates_name[1]

        if ab_campaign_count == '3':
            template_third_id = email_templates[2]
            template_third_path = email_templates_path[2]
            template_third_name = email_templates_name[2]
    ab_data = ab_campaigns_helper_obj.get_ab_campagin_by_id(campaign_id)
    if request.method == 'POST':

        template_third = ''
        templates = []
        template_first = request.form['template_first']

        if test_variable == 'content_template':

            template_second = request.form['template_second']
            if ab_campaign_count == '3':
                template_third = request.form['template_third']
            templates.insert(0, template_first)
            templates.insert(1, template_second)
            templates.insert(2, template_third)

            child_campaign = []
            for AB_data in ab_data:
                child_campaign_id = AB_data['id']
                child_campaign.append(child_campaign_id)

            for index, val in enumerate(child_campaign):
                ab_campaigns_helper_obj.\
                    update_ab_campaign_template(val, templates[index])
        else:
            child_campaign = []
            for AB_data in ab_data:
                child_campaign_id = AB_data['id']
                child_campaign.append(child_campaign_id)

            for index, val in enumerate(child_campaign):
                ab_campaigns_helper_obj. \
                    update_ab_campaign_template(val, template_first)

        return redirect(url_for('route_ab_send_time',
                                campaign_id=campaign_id))
    context = {"template": templates, "ab_campaign_count": ab_campaign_count,
               'test_variable': test_variable,
               'template_id1': template_first_id,
               'template_id2': template_second_id,
               'template_id3': template_third_id,
               'name1': template_first_name,
               'name2': template_second_name,
               'name3': template_third_name,
               'path1': template_first_path,
               'path2': template_second_path,
               'path3': template_third_path
               }
    return render_template('campaigns/ab_content_templates.html', **context)


@login_required
def ab_send_time(campaign_id=None):
    hours = []
    mins = []
    for i in range(1, 13):
        hours.append(i)
    for min in range(0, 60):
        mins.append(min)
    campaign_state = 'PUBLISHED'
    parent_campaign_data = ab_campaigns_helper_obj. \
        get_ab_parent_campaign(campaign_id)
    ab_campaign_count = parent_campaign_data['ab_campaign_count']
    test_variable = parent_campaign_data['test_variable']

    ab_data = ab_campaigns_helper_obj.get_ab_campagin_by_id(campaign_id)
    data_lst = []
    send_time_list = []
    send_time = ''
    for ab in ab_data:
        child_id = ab['id']
        send_time = ab['send_time']
        send_time_list.append(send_time)

    if send_time:

        if test_variable == 'send_time':
            for send_time in send_time_list:
                item = {}
                time_data = send_time.split(" ")
                time = time_data[0] + " " + time_data[1] + " " + time_data[2]
                hour = time_data[3]
                hour_data = hour.split(":")
                hour_value = hour_data[0]
                min_value = hour_data[1]
                zone = time_data[4]

                item['date'] = time
                item['hours'] = hour_value
                item['min'] = min_value
                item['zone'] = zone
                data_lst.append(item)
        else:
            ab_campaign = ab_data[0]
            send_time = ab_campaign['send_time']
            if send_time:
                item = {}
                time_data = send_time.split(" ")
                time = time_data[0] + " " + time_data[1] + " " + time_data[2]
                hour = time_data[3]
                hour_data = hour.split(":")
                hour_value = hour_data[0]
                min_value = hour_data[1]
                zone = time_data[4]

                item['date'] = time
                item['hours'] = hour_value
                item['min'] = min_value
                item['zone'] = zone
                data_lst.append(item)

    if request.method == 'POST':
        send_time = []
        if test_variable == 'send_time':

            for i in range(int(ab_campaign_count)):

                campaign_date = request.form['date_' + str(i + 1)]
                campaign_hours = request.form['hours_' + str(i + 1)]
                campaign_minutes = request.form['minutes_' + str(i + 1)]
                campaign_time_zone = request.form['time_zone_' + str(i + 1)]

                first_send_time = campaign_date + (' %s' % campaign_hours) + ':' \
                                  + campaign_minutes + (' %s' % campaign_time_zone)
                send_time.append(first_send_time)

            child_campaign = []
            for AB_data in ab_data:
                child_campaign_id = AB_data['id']
                child_campaign.append(child_campaign_id)

            for index, val in enumerate(child_campaign):
                ab_campaigns_helper_obj.update_ab_send_time(val,
                                                            send_time[index],
                                                            campaign_state)

            ab_campaigns_helper_obj.update_parent_status(campaign_state,
                                                         campaign_id)
        else:
            campaign_date = request.form['date_1']
            campaign_hours = request.form['hours_1']
            campaign_minutes = request.form['minutes_1']
            campaign_time_zone = request.form['time_zone_1']

            first_send_time = campaign_date + (' %s' % campaign_hours) + ':' \
                              + campaign_minutes + (' %s' % campaign_time_zone)

            child_campaign = []
            for AB_data in ab_data:
                child_campaign_id = AB_data['id']
                child_campaign.append(child_campaign_id)

            for index, id in enumerate(child_campaign):
                ab_campaigns_helper_obj.update_ab_send_time(id,
                                                            first_send_time,
                                                            campaign_state)

            ab_campaigns_helper_obj.update_parent_status(campaign_state,
                                                         campaign_id)

        return redirect('/campaigns/')
    context = {'hours': hours, 'mins': mins, 'campaign_id': campaign_id,
               'ab_campaign_count': ab_campaign_count, 'test_variable': test_variable,
               'data_list': data_lst}
    return render_template('campaigns/ab_send_time.html', **context)


@login_required
def campaigns_edit(campaign_id=None, params=None):
    one_time_campaign = campaign_helper_obj.\
        get_one_time_campaign_by_id(campaign_id, params)
    if one_time_campaign:
        return edit_one_time(campaign_id)
    else:
        return edit_ab_camapign(campaign_id)


@login_required
def edit_one_time(campaign_id):
    user_id = request.user
    list_data = list_helper.get_list(user_id)
    lst_data = []
    # status = 'ACTIVE'
    # state = 'DRAFT'
    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)
    get_campaign = campaign_helper_obj.get_campaign_by_id(campaign_id)

    list_id = get_campaign['list_id']
    name = get_campaign['name']
    type = get_campaign['campaign_type']
    list_data = list_helper.get_list_name_by_listid(list_id)
    list_name = list_data['list_name']
    count = list_helper.get_listsegment_count(list_id)

    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        campaign_type = request.form['campaign_type']
        list_id = request.form['list_id']

        campaign_helper_obj.update_campaigns(list_id, campaign_name,
                                             campaign_id, campaign_type)
        if campaign_type == 'One-time':
            return redirect(url_for('route_subject_line',
                                    campaign_id=campaign_id))
        else:
            return redirect(url_for('route_ab_subject_lines',
                                    campaign_id=campaign_id))

    context = {'list_data': lst_data, "campaign_id": campaign_id,
               "count": count, "campaign_name": name, "campaign_type": type,
               "list_name": list_name, "list_id": list_id}
    return render_template('campaigns/inspiration.html', **context)


@login_required
def edit_ab_camapign(campaign_id):
    user_id = request.user
    list_data = list_helper.get_list(user_id)
    lst_data = []
    # status = 'ACTIVE'
    # state = 'DRAFT'
    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)

    # get_ab_campaign = ab_campaigns_helper_obj.\
    #     get_parent_by_ab_campaign_id(campaign_id)
    get_ab_campaign = ab_campaigns_helper_obj.get_parnet_by_id(campaign_id)
    name = get_ab_campaign['name']
    list_id = get_ab_campaign['list_id']
    type = get_ab_campaign['campaign_type']
    list_data = list_helper.get_list_name_by_listid(list_id)
    list_name = list_data['list_name']
    count = list_helper.get_listsegment_count(list_id)

    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        campaign_type = request.form['campaign_type']
        list_id = request.form['list_id']

        # campaign_helper_obj.update_campaigns(list_id, campaign_name,
        #                                      campaign_id, campaign_type)
        ab_campaigns_helper_obj.update_parnet_campaign(list_id,
                                                       campaign_name,
                                                       campaign_id,
                                                       campaign_type)

        if campaign_type == 'One-time':
            return redirect(url_for('route_subject_line',
                                    campaign_id=campaign_id))
        else:
            return redirect(url_for('route_ab_subject_lines',
                                    campaign_id=campaign_id))
            # return redirect(url_for('route_ui_test',
            #                         campaign_id=campaign_id))

    context = {'list_data': lst_data, "campaign_id": campaign_id,
               "count": count, "campaign_name": name, "campaign_type": type,
               "list_name": list_name, "list_id": list_id}
    return render_template('campaigns/inspiration.html', **context)


@login_required
def graph(campaign_id=None, params=None):
    context = json.loads(graph_data(campaign_id, params).data.decode("utf-8"))
    return render_template('campaigns/graph.html', **context)


@login_required
def graph_data(campaign_id=None, params=None):
    open_count = 0
    clicks_count = 0
    send_count = 0
    error_count = 0
    unsubscribe_count = 0
    deliveries_count = 0
    bounce_emails_count = 0
    total_emails_count = 0

    open_percentage = 0
    click_percentage = 0
    unsubscribe_percentage = 0
    deliveries_percentage = 0
    bounce_emails_percentage = 0
    total_emails_percentage = 0

    first_open = 0
    second_open = 0
    third_open = 0
    first_click = 0
    second_click = 0
    third_click = 0
    first_unsubscribe = 0
    second_unsubscribe = 0
    third_unsubscribe = 0
    queued_time = 0
    recipients_per_combination = 0
    current_time = datetime.now().date()

    dates = ['x']
    clicks = ['click']
    open_rate = ['open']

    campaign_name = ''
    parent_campaign_rate = ''
    parent_campaign_time_after = ''
    parent_campaign_percentage = ''
    parent_campaign_time_type = ''
    first_test_variable = ''
    second_test_variable = ''
    third_test_variable = ''
    list_name = ''

    parent_campaign_count = 0
    list_count = 0
    # campaign_name = "No Campaigns"
    campaign_name = ""
    total_send_time = ""
    seconds = 0
    campaign_a_winner = ''
    campaign_b_winner = ''
    campaign_c_winner = ''
    campaign_tie = ''

    if campaign_id:

        #####################################
        #          One-Time campaign        #
        #####################################
        campaigns = campaign_helper_obj.get_campaign_by_id_and_status(campaign_id, params)
        if campaigns:
            campaign_id = campaigns['id']
            campaign_name = campaigns['name']
            list_id = campaigns['list_id']
            queued_time = campaigns['queued_time']
            list_data = list_helper.get_list_name_by_listid(list_id)
            list_name = list_data['list_name']
            list_count = list_helper.get_listsegment_count(list_id)
            total_send_time_data = campaign_helper_obj.get_total_send_time(campaign_id)

            if total_send_time_data:
                for item in total_send_time_data:
                    seconds = item['seconds']

            month_value = 1
            if request.method == "POST":
                month_value = int(request.form.get('data'))
                if not month_value:
                    month_value = 1
            total_days = ''
            if month_value == 1:
                total_days = 30
            if month_value == 2:
                total_days = 60
            if month_value == 3:
                total_days = 90

            data_dict = {}
            current_time = datetime.now().date()
            st = current_time - timedelta(days=int(total_days))

            while st <= current_time:
                if st not in data_dict:
                    data_dict[st] = {"clicks": 0, "open": 0}

                open_click_rate = campaign_stats_helper. \
                    get_open_click_rate_by_date_and_campaign_id(st, campaign_id)
                email_results = ready_to_send_email_helper_obj. \
                    get_sent_emails_by_date_campaign_id(st, campaign_id)

                for resp in email_results:
                    total_emails_count += 1
                    if resp['status'] == 'SENT':
                        send_count += 1
                    if resp['status'] == 'UNSUBSCRIBE':
                        unsubscribe_count += 1
                    if resp['status'] == 'ERROR':
                        error_count += 1

                for stats_data in open_click_rate:
                    open_count += stats_data['open']
                    clicks_count += stats_data['click']
                    data_dict[st]['clicks'] += stats_data['click']
                    data_dict[st]['open'] += stats_data['open']
                st = st + timedelta(days=1)

            for key, val in sorted(data_dict.items()):
                dates.append(key)
                clicks.append(val['clicks'])
                open_rate.append(val['open'])

            #####################################
            #        Campaign Bounce code       #
            #####################################

            get_bounce_emails = email_result_helper.get_bounce_emails()
            get_list_emails = list_helper.get_emails_by_listid(list_id)

            all_bounce_email_list = []
            for emails in get_bounce_emails:
                all_bounce_email_list.append(emails['email_address'])

            all_email_list = []
            for email in get_list_emails:
                all_email_list.append(email['email'])

            bounce_emails = []
            for i in all_email_list:
                if i in all_bounce_email_list:
                    bounce_emails.append(i)

            bounce_emails_count = len(bounce_emails)
            if total_emails_count != 0:
                bounce_emails_percentage = round((bounce_emails_count * 100) / total_emails_count, 2)

            #####################################
            #      Campaign Get Percentage      #
            #####################################

            deliveries_count = send_count + error_count + unsubscribe_count
            if deliveries_count and total_emails_count:
                open_percentage = round((open_count * 100) / deliveries_count, 2)
                click_percentage = round(
                    (clicks_count * 100) / deliveries_count, 2)
                deliveries_percentage = round(
                    (deliveries_count * 100) / total_emails_count, 2)
                unsubscribe_percentage = round(
                    (unsubscribe_count * 100) / total_emails_count, 2)
                total_emails_percentage = round(
                    (total_emails_count * 100) / total_emails_count, 2)

        else:
            #####################################
            #           AB-Test campaign        #
            #####################################
            parent_campaign = ab_campaigns_helper_obj.get_ab_parent_campaigns(campaign_id, params)
            if parent_campaign:
                if parent_campaign['campaign_state'] == 'PUBLISHED':
                    parent_campaign_campaign_state = parent_campaign['campaign_state']
                    parent_campaign_id = parent_campaign['id']
                    campaign_name = parent_campaign['name']
                    parent_campaign_rate = parent_campaign['rate']
                    parent_campaign_time_after = parent_campaign['time_after']
                    parent_campaign_time_type = parent_campaign['time_type']
                    parent_campaign_percentage = parent_campaign['test_percentage']
                    parent_campaign_list_id = parent_campaign['list_id']
                    ab_campaign_test_variable = parent_campaign['test_variable']
                    list_id = parent_campaign['list_id']
                    queued_time = parent_campaign['queued_time']
                    list_data = list_helper.get_list_name_by_listid(list_id)
                    list_name = list_data['list_name']
                    list_count = list_helper.get_listsegment_count(parent_campaign_list_id)
                    parent_campaign_count = parent_campaign['ab_campaign_count']

                    #############################
                    #       total send time     #
                    #############################
                    total_ab_send_time_data = campaign_helper_obj.get_ab_total_send_time(parent_campaign_id)
                    if total_ab_send_time_data:
                        for item in total_ab_send_time_data:
                            seconds = item['seconds']

                    value = math.trunc(int(list_count) / int(parent_campaign_count))
                    recipients_per_combination = math.trunc(
                        (value / 100) * parent_campaign_percentage)

                    ##############################################################
                    #           get child campaign against parent campaig        #
                    ##############################################################
                    ab_campaign = ab_campaigns_helper_obj.get_ab_campagin_by_id(parent_campaign_id)
                    ab_email_subject = []
                    ab_templates = []
                    ab_send_time = []
                    child_campaigns = []
                    for ab in ab_campaign:
                        ab_template_id = ab['templates_id']
                        ab_campaign_id = ab['id']
                        child_campaigns.append(ab_campaign_id)

                        get_tem_data = template_helper.get_template_by_id(ab_template_id)
                        ab_email_subject.append(ab['email_subject'])
                        ab_templates.append(get_tem_data['path'])
                        ab_send_time.append(ab['send_time'])
                    month_value = 1
                    if request.method == "POST":
                        month_value = int(request.form.get('data'))
                        if not month_value:
                            month_value = 1
                    total_days = ''
                    if month_value == 1:
                        total_days = 30
                    if month_value == 2:
                        total_days = 60
                    if month_value == 3:
                        total_days = 90

                    data_dict = {}
                    current_time = datetime.now().date()
                    st = current_time - timedelta(days=int(total_days))

                    while st <= current_time:
                        if st not in data_dict:
                            data_dict[st] = {"clicks": 0, "open": 0}
                        open_clicks = []
                        for index, val in enumerate(child_campaigns):

                            open_click_rate = campaign_stats_helper. \
                                get_ab_open_click_rate_by_date_and_campaign_id(st, val)
                            open_clicks.append(open_click_rate)
                            email_results = ready_to_send_email_helper_obj. \
                                get_ab_sent_emails_by_date_campaign_id(st, val)

                        for op_click_data in open_clicks:
                            for stats_data in op_click_data:
                                open_count += stats_data['open']
                                clicks_count += stats_data['click']
                                data_dict[st]['clicks'] += stats_data['click']
                                data_dict[st]['open'] += stats_data['open']
                        st = st + timedelta(days=1)

                    for key, val in sorted(data_dict.items()):
                        dates.append(key)
                        clicks.append(val['clicks'])
                        open_rate.append(val['open'])

                    if ab_campaign_test_variable == 'subject_lines':
                        first_test_variable = ab_email_subject[0]
                        second_test_variable = ab_email_subject[1]
                        third_test_variable = ''
                        if parent_campaign_count == '3':
                            third_test_variable = ab_email_subject[2]

                    elif ab_campaign_test_variable == 'content_template':
                        first_test_variable = ab_templates[0]
                        second_test_variable = ab_templates[1]
                        third_test_variable = ''
                        if parent_campaign_count == '3':
                            third_test_variable = ab_templates[2]

                    elif ab_campaign_test_variable == 'send_time':
                        first_test_variable = ab_send_time[0]
                        second_test_variable = ab_send_time[1]
                        third_test_variable = ''
                        if parent_campaign_count == '3':
                            third_test_variable = ab_send_time[2]

                    open_data = []
                    click_data = []
                    for index, val in enumerate(child_campaigns):
                        get_stats_data = campaign_stats_helper.get_ab_campaign_stats(val)
                        for index, val in enumerate(get_stats_data):
                            total_open = val['open']
                            total_click = val['click']
                            open_data.append(total_open)
                            click_data.append(total_click)

                    #########################################
                    #        AB open click calculations     #
                    #########################################
                    first_open = open_data[0]
                    second_open = open_data[1]
                    first_click = click_data[0]
                    second_click = click_data[1]
                    open_count = first_open + second_open
                    clicks_count = first_click + second_click
                    if parent_campaign_count == '3':
                        third_open = open_data[2]
                        third_click = click_data[2]
                        open_count = first_open + second_open + third_open
                        clicks_count = first_click + second_click + third_click

                    ##############################
                    #     unsubscribe emails     #
                    ##############################
                    unsubscribe_list = []
                    for index, val in enumerate(child_campaigns):
                        ab_unsubscribe_count = ready_to_send_email_helper_obj.check_status_by_ab_campaign_id(val)

                        for data in ab_unsubscribe_count:
                            ab_unsubscribe_count = data['unsubscribe']
                            unsubscribe_list.append(ab_unsubscribe_count)
                    first_unsubscribe = unsubscribe_list[0]
                    second_unsubscribe = unsubscribe_list[1]
                    unsubscribe_counts = first_unsubscribe + second_unsubscribe
                    if parent_campaign_count == '3':
                        third_unsubscribe = unsubscribe_list[2]
                        unsubscribe_counts = first_unsubscribe + second_unsubscribe + third_unsubscribe
                    total_emails = []
                    for index, val in enumerate(child_campaigns):
                        email_results = ready_to_send_email_helper_obj. \
                            get_ab_sent_emails_by_id(val)
                        for resp in email_results:
                            total_emails.append(resp)

                    for emails in total_emails:
                        total_emails_count += 1
                        if emails['status'] == 'UNSUBSCRIBE':
                            unsubscribe_count += 1
                        if emails['status'] == 'SENT':
                            send_count += 1
                        if emails['status'] == 'ERROR':
                            error_count += 1

                if queued_time:
                    # queued_time = campaigns['queued_time']
                    current_time = datetime.now()
                    winning_combination = ab_campaigns_helper_obj.get_all_combinations(campaign_id)
                    winning_type = winning_combination['rate']
                    winning_time = winning_combination['time_after']
                    winning_day_hours = winning_combination['time_type']

                    if winning_type == 'Open rate':
                        if winning_day_hours == 'days':
                            wining_time = queued_time + timedelta(days=int(winning_time))
                        else:
                            wining_time = queued_time + timedelta(hours=int(winning_time))

                        campaign_a_winner = ''
                        campaign_b_winner = ''
                        campaign_c_winner=''
                        campaign_tie=''
                        if current_time > wining_time:
                            if (first_open > second_open) and (first_open > third_open):
                                campaign_a_winner = 'Campaign A is winner'
                            elif (second_open > first_open) and (second_open > third_open):
                                campaign_b_winner = 'campaign B is winner'
                            elif (third_open > first_open) and (third_open > second_open):
                                campaign_c_winner = 'campaign C is winner'
                            else:
                                campaign_tie = 'All campaign result are equal'
                        else:
                            pass
                    else:
                        if winning_day_hours == 'days':
                            wining_time = queued_time + timedelta(days=int(winning_time))
                        else:
                            wining_time = queued_time + timedelta(hours=int(winning_time))

                        campaign_a_winner = ''
                        campaign_b_winner = ''
                        campaign_c_winner = ''
                        campaign_tie = ''
                        if current_time > wining_time:
                            if (first_click > second_click) and (first_click > third_click):
                                campaign_a_winner = 'Campaign A is winner'
                            elif (second_click > first_click) and (second_click > third_click):
                                campaign_b_winner = 'campaign B is winner'
                            elif (third_click > first_click) and (third_click > second_click):
                                campaign_c_winner = 'campaign C is winner'
                            else:
                                campaign_tie = 'campaigns result are equal'
                        else:
                            pass

                #####################################
                #        AB-Campaign Bounce code    #
                #####################################
                get_bounce_emails = email_result_helper.get_bounce_emails()
                get_list_emails = list_helper.get_emails_by_listid(list_id)

                all_bounce_email_list = []
                for emails in get_bounce_emails:
                    all_bounce_email_list.append(emails['email_address'])

                all_email_list = []
                for email in get_list_emails:
                    all_email_list.append(email['email'])

                bounce_emails = []
                for i in all_email_list:
                    if i in all_bounce_email_list:
                        bounce_emails.append(i)

                bounce_emails_count = len(bounce_emails)
                if total_emails_count != 0:
                    bounce_emails_percentage = round((bounce_emails_count * 100) / total_emails_count, 2)

                deliveries_count = send_count + error_count + unsubscribe_count
                if deliveries_count and total_emails_count:
                        open_percentage = round((open_count * 100) / deliveries_count, 2)
                        click_percentage = round(
                            (clicks_count * 100) / deliveries_count, 2)
                        deliveries_percentage = round(
                            (deliveries_count * 100) / total_emails_count, 2)
                        unsubscribe_percentage = round(
                            (unsubscribe_count * 100) / total_emails_count, 2)
                        total_emails_percentage = round(
                            (total_emails_count * 100) / total_emails_count, 2)

    else:
        month_value = 1
        if request.method == "POST":
            month_value = int(request.form.get('data'))
            if not month_value:
                month_value = 1
        total_days = ''
        if month_value == 1:
            total_days = 30
        if month_value == 2:
            total_days = 60
        if month_value == 3:
            total_days = 90

        data_dict = {}
        current_time = datetime.now().date()
        st = current_time - timedelta(days=int(total_days))
        get_bounce_emails_list = ''
        get_sent_email_by_date_list = ''

        while st <= current_time:
            if st not in data_dict:
                data_dict[st] = {"clicks": 0, "open": 0}

            open_click_rate = campaign_stats_helper.get_open_click_rate_by_date_and_campaign(st)

            email_results = ready_to_send_email_helper_obj.get_sent_emails_by_date(st)

            #####################################
            #            Bounce code            #
            #####################################
            get_bounce_emails = email_result_helper.get_bounce_emails()
            get_bounce_emails_list = []
            for item in get_bounce_emails:
                get_bounce_emails_list.append(item)

            get_sent_email_by_date = ready_to_send_email_helper_obj.get_sent_email_by_date(st)
            get_sent_email_by_date_list = []
            for item2 in get_sent_email_by_date:
                get_sent_email_by_date_list.append(item2)

            for resp in email_results:
                total_emails_count += 1
                if resp['status'] == 'SENT':
                    send_count += 1
                if resp['status'] == 'UNSUBSCRIBE':
                    unsubscribe_count += 1
                if resp['status'] == 'ERROR':
                    error_count += 1

            for stats_data in open_click_rate:
                open_count += stats_data['open']
                clicks_count += stats_data['click']
                data_dict[st]['clicks'] += stats_data['click']
                data_dict[st]['open'] += stats_data['open']
            st = st + timedelta(days=1)
        # bounce emails
        bounce_emails = []
        for item1 in get_bounce_emails_list:
            for item2 in get_sent_email_by_date_list:
                if item1['subject'] == item2['subject'] and item1['email_address'] == item2['email_address']:
                    bounce_emails.append(item1['email_address'])

        bounce_emails_count = len(bounce_emails)
        if total_emails_count != 0:
            bounce_emails_percentage = round((bounce_emails_count * 100) / total_emails_count, 2)


        for key, val in sorted(data_dict.items()):
            dates.append(key)
            clicks.append(val['clicks'])
            open_rate.append(val['open'])

        deliveries_count = send_count + error_count
        if deliveries_count and total_emails_count:
            open_percentage = round((open_count * 100) / deliveries_count, 2)
            click_percentage = round(
                (clicks_count * 100) / deliveries_count, 2)
            deliveries_percentage = round(
                (deliveries_count * 100) / total_emails_count, 2)
            unsubscribe_percentage = round(
                (unsubscribe_count * 100) / total_emails_count, 2)
            total_emails_percentage = round(
                (total_emails_count * 100) / total_emails_count, 2)
        else:
            open_percentage = ''
            click_percentage = ''
            click_percentage = ''
            unsubscribe_percentage = ''
            total_emails_percentage = ''


    if not seconds:
        total_send_time = "_"
    else:
        if seconds > 0:
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            if (d == 0):
                total_send_time = "%d Hours %02d Minutes %02d Seconds" % (h, m, s)
                if (h == 0):
                    total_send_time = "%d Minutes %02d Seconds" % (m, s)
                    if (m == 0):
                        total_send_time = "%d Seconds" % s
            else:
                total_send_time = "%d Days %d Hours %02d Minutes %02d Seconds" % (d, h, m, s)
        else:
            total_send_time = "_"

    context = {"open_count": open_count,
               "clicks_counts": clicks_count,
               "total_emails_count": total_emails_count,
               "deliveries_count": deliveries_count,
               "error_count": error_count,
               "unsubscribe_count": unsubscribe_count,
               "open_percentage": open_percentage,
               "click_percentage": click_percentage,
               "deliveries_percentage": deliveries_percentage,
               "total_emails_percentage": total_emails_percentage,
               "unsubscribe_percentage": unsubscribe_percentage,
               "dates": dates, "clicks": clicks, "open": open_rate,
               'testing_name': campaign_name, 'campaign_type': params,
               'win_by': parent_campaign_rate,
               'time_after': parent_campaign_time_after,
               'percentage': parent_campaign_percentage,
               'time_type': parent_campaign_time_type,
               'recipients_per_combination': recipients_per_combination,
               'list_count': list_count,
               'ab_campaign_count': parent_campaign_count,
               'first_template': first_test_variable,
               'second_template': second_test_variable,
               'third_template': third_test_variable,
               'first_open': first_open,
               'second_open': second_open,
               'first_click': first_click,
               'second_click': second_click,
               'third_open': third_open,
               'third_click': third_click,
               'first_unsubscribe': first_unsubscribe,
               'second_unsubscribe': second_unsubscribe,
               'third_unsubscribe': third_unsubscribe,
               "list_name": list_name, 'queued_time': queued_time,
               "campaign_type": params, 'campaign_id': campaign_id,
               "total_send_time": total_send_time,
               "campaign_a_winner": campaign_a_winner,
               "campaign_b_winner": campaign_b_winner,
               "campaign_c_winner": campaign_c_winner,
               "campaign_tie": campaign_tie,
               "bounce_emails_count": bounce_emails_count,
               "bounce_emails_percentage": bounce_emails_percentage,
    }

    return jsonify(context)
