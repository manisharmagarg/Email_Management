import traceback
import json
from struct import *
import random
from emailapp.decorate import login_required
from emailapp.sql_helpers import templates, authenticate, user, lists, \
    campaign_helper, email_result, ready_to_send_email_helper, \
    campaign_stats, campaign_winning_combination, emails_unsubscribe, \
    campaign_setup, email_subject, ab_campaigns_helper
from emailapp import app, session, request, redirect, render_template, url_for,\
    bcrypt, jsonify
from conf.config import EMAIL_OPEN_URL, APP_ROOT, APP_STATIC
from datetime import datetime, timedelta


campaign_stats_helper = campaign_stats.CampaignStatsHelper()
template_helper = templates.Templates()
user_authenticate = authenticate.Authenticate()
campaign_helper_obj = campaign_helper.CampaignHelper()
email_result_helper = email_result.EmailResultHelper()
ready_to_send_email_helper_obj = ready_to_send_email_helper.ReadyToSendEmailsHelper()
email_user = user.User()
list_helper = lists.Lists()
campaign_winning_helper = campaign_winning_combination.CampaignWinningHelper()
emails_unsubscribe_obj = emails_unsubscribe.EmailUnsubscribeHelper()

campaign_setup_obj = campaign_setup.CampaignSetupHelper()
email_subject_obj = email_subject.EmailSubjectHelper()
ab_campaigns_helper_obj = ab_campaigns_helper.AbCampaignsHelper()


@login_required
def ui_campaigns():
    email_campaign = campaign_helper_obj.get_campaigns()
    email_ab_campaign = ab_campaigns_helper_obj.get_all_ab_campaign()

    email_campaigns = []

    for item in email_campaign:
        email_campaign_data = []
        id = item['id']
        camapaign_type = item['campaign_type']
        name = item['name']
        campaign_state = item['campaign_state']
        status = item['status']

        email_campaign_data.append(id)
        email_campaign_data.append(name)
        email_campaign_data.append(camapaign_type)
        email_campaign_data.append(status)
        email_campaign_data.append(campaign_state)

        email_campaigns.append(email_campaign_data)

    for ab_data in email_ab_campaign:
        email_campaign_data = []

        id = ab_data['id']
        camapaign_type = ab_data['campaign_type']
        name = ab_data['name']
        campaign_state = ab_data['campaign_state']
        status = ab_data['status']

        email_campaign_data.append(id)
        email_campaign_data.append(name)
        email_campaign_data.append(camapaign_type)
        email_campaign_data.append(status)
        email_campaign_data.append(campaign_state)

        email_campaigns.append(email_campaign_data)

    context = {'email_campaigns': email_campaigns}
    return render_template('ui/campaigns.html', **context)


@login_required
def ui_create_campaign():
    return render_template('ui/create_campaigns.html')


@login_required
def ui_one_time_campaign_setup(campaign_id=None):

    user_id = request.user
    list_data = list_helper.get_list(user_id)
    lst_data = []
    status = 'ACTIVE'
    campaign_type = 'One-time'

    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)

    if campaign_id == None:
        name = ""
        list_id = ""
        list_name = "Choose a list of recipients"
    else:
        campaigns = campaign_helper_obj.get_campaign_by_id(campaign_id)
        name = campaigns['name']
        list_id = campaigns['list_id']
        data = list_helper.get_list_name_by_listid(list_id)
        list_name = data['list_name']

    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        list_id = request.form['list_id']
        if not campaign_id:
            campaign_id = campaign_helper_obj\
                .create_campaign(campaign_name, status,
                                 user_id, templates_id=None,
                                 campaign_type=campaign_type,
                                 list_id=list_id, send_time=None,
                                 email_subject=None, preview_text=None,
                                 percentage=None, is_ab_campaign=False,
                                 parent_campaign_id=None)

            return redirect(url_for('route_ui_subject_line_by_id', campaign_id=campaign_id))
        else:
            campaign_helper_obj.update_campaign(list_id, campaign_name, campaign_id,
                                                campaign_type, state=None)
            return redirect(url_for('route_ui_subject_line_by_id', campaign_id=campaign_id))

    context = {'list_data': lst_data, 'name': name, 'list_name': list_name, 'list_id': list_id}
    return render_template('ui/one_time_campaign_setup.html', **context)


@login_required
def ui_subject_line(campaign_id=None):
    state = 'DRAFT'
    user_id = request.user
    get_campaign = campaign_helper_obj.get_campaign_by_id(campaign_id)
    data = get_campaign['email_subject']
    campaign_state = get_campaign['campaign_state']

    if campaign_state == 'PUBLISHED':
        state = 'PUBLISHED'

    if data == None:
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

        return redirect(url_for('route_ui_content_templates_by_id', campaign_id=campaign_id))
    context = {'emails_subject': emails_subject,
               'preview_text': preview_text, 'campaign_id': campaign_id}
    return render_template('ui/subject_line.html', **context)


@login_required
def ui_content_templates(campaign_id=None):

    user_id = request.user
    campaign_type = 'One-time'
    templates = template_helper.get_templates()
    campaign = campaign_helper_obj.get_campaign_by_id(campaign_id)
    template_id = campaign['templates_id']
    if template_id == None:
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

        return redirect(url_for('route_ui_send_time_by_id', campaign_id=campaign_id))
    context = {"template": templates, "template_id": template_id, "path": path, "name": name}
    return render_template('ui/content_templates.html', **context)


@login_required
def ui_send_time(campaign_id=None):

    state = 'PUBLISHED'
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

        return redirect('/ui/campaigns/')

    context = {'hours': hours, 'mins': mins}
    return render_template('ui/send_time.html', **context)


@login_required
def ui_campaign_data(campaign_id=None):
    get_campaign = ready_to_send_email_helper_obj.get_all_emails_by_id(campaign_id)
    total_emails = 0
    ready_to_send_count = 0
    sent_count = 0
    error_count = 0
    total = 0
    unsubscribe_count = 0
    for email_campaign in get_campaign:
        total_emails += 1
        status = email_campaign['status']
        if status == 'READY_TO_SEND':
            ready_to_send_count += 1
        if status == 'SENT':
            sent_count += 1
        if status == 'ERROR':
            error_count += 1
        if status == 'UNSUBSCRIBE':
            unsubscribe_count += 1

        mails = 0

        if mails <= total_emails:
            total = (sent_count + unsubscribe_count + error_count)*100/total_emails
            mails += 1
    return jsonify({"total": total})


###############################
#          A/B Testing        #
###############################
@login_required
def ui_one_time_campaign_create(campaign_id=None):

    user_id = request.user
    list_data = list_helper.get_list(user_id)
    lst_data = []
    # templates_id = 1
    status = 'ACTIVE'
    campaign_state = 'DRAFT'
    campaign_type = 'AB_Test'

    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)
    name = ''
    list_name = ''
    count = ''
    list_id = ''
    if campaign_id == None:
        name = ""
        list_id = ""
        list_name = "Choose a list of recipients"

    else:
        parent_campaign = ab_campaigns_helper_obj.get_ab_parent_campaign(campaign_id)
        name = parent_campaign['name']

        list_id = parent_campaign['list_id']
        list_data = list_helper.get_list_name_by_listid(list_id)
        list_name = list_data['list_name']
        count = list_helper.get_listsegment_count(list_id)

    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        list_id = request.form['list_id']
        # segment_list = request.form['segment_list']
        # segment_list = 26

        if campaign_id:
            ab_campaigns_helper_obj.update_ab_parent_campaign(campaign_id,
                                                              campaign_name,
                                                              list_id)
            return redirect(url_for('route_ui_test', campaign_id=campaign_id))

        ab_campaign_parent_id = ab_campaigns_helper_obj.\
            create_ab_campaigns_parent(campaign_name, list_id,
                                       user_id, campaign_type,
                                       status,
                                       percentage=None,
                                       rate=None, time_after=None,
                                       time_type=None, ab_campaign_count=None)

        return redirect(url_for('route_ui_test', campaign_id=ab_campaign_parent_id))

    context = {'list_data': lst_data, 'name': name, 'list_name': list_name,
               'count': count, 'list_id': list_id}
    return render_template('ui/one_time_campaign_create.html', **context)


@login_required
def ui_test(campaign_id=None):
    # campaign_state = 'DRAFT'
    get_ab_campaigns = ab_campaigns_helper_obj.get_ab_parent_campaign(campaign_id)
    list_id = get_ab_campaigns['list_id']
    test_percentage = get_ab_campaigns['test_percentage']
    if test_percentage == None:
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
        campaign_count = request.form.get('theCount')

        ab_campaigns_helper_obj.\
            update_ab_winning_cambination(campaign_id, percentage, rate,
                                          time_after, time_type, campaign_count)
        return redirect(url_for('route_ui_subject_lines_by_id', campaign_id=campaign_id))
    context = {'ab_campaigns_parent_id': campaign_id,
               'segment_count': segment_count,
               'test_percentage': test_percentage, 'rate': rate,
               'time_after': time_after, 'time_type': time_type,
               'ab_campaign_count': ab_campaign_count}
    return render_template('ui/test.html', **context)


@login_required
def ui_subject_lines(campaign_id=None):
    status = 'ACTIVE'
    campaign_state = 'DRAFT'
    user_id = request.user

    parent_campaign_data = ab_campaigns_helper_obj.get_ab_parent_campaign(campaign_id)
    ab_campaign_count = parent_campaign_data['ab_campaign_count']
    get_ab_campaign = ab_campaigns_helper_obj.get_ab_campagin_by_id(campaign_id)

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

        ab_campaign = ab_campaigns_helper_obj.check_if_campaign_already_exist(campaign_id)
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
                                        email_subject_third, preview_text_subject,
                                        status, campaign_state,
                                        templates_id=None,
                                        send_time=None)
            ab_campaigns_helper_obj.update_parent_status(campaign_state, campaign_id)
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

        return redirect(url_for('route_ui_content_templates2', campaign_id=campaign_id))
    context = {'ab_campaign_count': ab_campaign_count, 'emails_subject': emails_subject,
               'preview_text': preview_text, 'campaign_id': campaign_id}
    return render_template('ui/subject_lines.html', **context)


@login_required
def ui_content_templates2(campaign_id=None):

    user_id = request.user

    parent_campaign_data = ab_campaigns_helper_obj.get_ab_parent_campaign(campaign_id)
    ab_campaign_count = parent_campaign_data['ab_campaign_count']
    get_ab_campaign = ab_campaigns_helper_obj.get_ab_campagin_by_id(campaign_id)

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
        if templates_id == None:
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

    if request.method == 'POST':
        template_third = ''
        templates = []
        template_first = request.form['template_first']
        template_second = request.form['template_second']
        if ab_campaign_count == '3':
            template_third = request.form['template_third']
        templates.insert(0, template_first)
        templates.insert(1, template_second)
        templates.insert(2, template_third)
        ab_data = ab_campaigns_helper_obj.get_ab_campagin_by_id(campaign_id)
        child_campaign = []
        for AB_data in ab_data:
            child_campaign_id = AB_data['id']
            child_campaign.append(child_campaign_id)

        for index, val in enumerate(child_campaign):
            ab_campaigns_helper_obj.update_ab_campaign_template(val, templates[index])

        return redirect(url_for('route_ui_send_time2', campaign_id=campaign_id))
    context = {"template": templates, "ab_campaign_count": ab_campaign_count,
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
    return render_template('ui/content_templates2.html', **context)


@login_required
def ui_send_time2(campaign_id=None):

    hours = []
    mins = []
    for i in range(1, 13):
        hours.append(i)
    for min in range(0, 60):
        mins.append(min)
    campaign_state = 'PUBLISHED'
    parent_campaign_data = ab_campaigns_helper_obj.get_ab_parent_campaign(campaign_id)
    ab_campaign_count = parent_campaign_data['ab_campaign_count']

    if request.method == 'POST':
        third_send_time = ''
        send_time = []
        first_campaign_date = request.form['first_date']
        first_campaign_hours = request.form['first_hours']
        first_campagin_minutes = request.form['first_minutes']
        first_campaign_time_zone = request.form['first_time_zone']

        second_campaign_date = request.form['second_date']
        second_campaign_hours = request.form['second_hours']
        second_campaign_minutes = request.form['second_minutes']
        second_campaign_time_zone = request.form['second_time_zone']

        if ab_campaign_count == '3':
            third_campaign_date = request.form['third_date']
            third_campaign_hours = request.form['third_hours']
            third_campaign_minutes = request.form['third_minutes']
            third_campaign_time_zone = request.form['third_time_zone']

            third_send_time = third_campaign_date + (' %s' % third_campaign_hours) + ':' \
                              + third_campaign_minutes + (' %s' % third_campaign_time_zone)

        first_send_time = first_campaign_date + (' %s' % first_campaign_hours) + ':' \
                          + first_campagin_minutes + (' %s' % first_campaign_time_zone)

        second_send_time = second_campaign_date + (' %s' % second_campaign_hours) \
                           + ':' + second_campaign_minutes + (' %s' % second_campaign_time_zone)

        send_time.insert(0, first_send_time)
        send_time.insert(1, second_send_time)
        send_time.insert(2, third_send_time)

        ab_data = ab_campaigns_helper_obj.get_ab_campagin_by_id(campaign_id)
        child_campaign = []
        for AB_data in ab_data:
            child_campaign_id = AB_data['id']
            child_campaign.append(child_campaign_id)

        for index, val in enumerate(child_campaign):
            ab_campaigns_helper_obj.update_ab_send_time(val, send_time[index], campaign_state)

        ab_campaigns_helper_obj.update_parent_status(campaign_state, campaign_id)

        return redirect('/ui/campaigns/')
    context = {'hours': hours, 'mins': mins, 'campaign_id': campaign_id,
               'ab_campaign_count': ab_campaign_count}
    return render_template('ui/send_time2.html', **context)


@login_required
def ui_inspiration():
    return render_template('ui/inspiration.html')


@login_required
def ui_graph():
    context = json.loads(ui_graph_data().data.decode("utf-8"))
    return render_template('ui/graph.html', **context)


@login_required
def ui_campaign_edit(campaign_id=None, params=None):
    one_time_campaign = campaign_helper_obj.get_one_time_campaign_by_id(campaign_id, params)
    if one_time_campaign:
        return edit_one_time(campaign_id)
    else:
        return edit_ab_camapign(campaign_id)


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

        campaign_helper_obj.update_campaigns(list_id, campaign_name, campaign_id, campaign_type)
        if campaign_type == 'One-time':
            return redirect(url_for('route_ui_subject_line_by_id', campaign_id=campaign_id))
        else:
            return redirect(url_for('route_ui_subject_lines_by_id', campaign_id=campaign_id))

    context = {'list_data': lst_data, "campaign_id": campaign_id, "count": count,
               "campaign_name": name, "campaign_type": type, "list_name": list_name, "list_id": list_id}
    return render_template('ui/inspiration.html', **context)


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

    # get_ab_campaign = ab_campaigns_helper_obj.get_parent_by_ab_campaign_id(campaign_id)
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

        # campaign_helper_obj.update_campaigns(list_id, campaign_name, campaign_id, campaign_type)
        ab_campaigns_helper_obj.update_parnet_campaign(list_id, campaign_name, campaign_id, campaign_type)

        if campaign_type == 'One-time':
            return redirect(url_for('route_ui_subject_line_by_id', campaign_id=campaign_id))
        else:
            return redirect(url_for('route_ui_subject_lines_by_id', campaign_id=campaign_id))
            # return redirect(url_for('route_ui_test', campaign_id=campaign_id))

    context = {'list_data': lst_data, "campaign_id": campaign_id, "count": count,
               "campaign_name": name, "campaign_type": type, "list_name": list_name, "list_id": list_id}
    return render_template('ui/inspiration.html', **context)


############################
#     get graph data       #
############################
@login_required
def ui_graph_data():

    data_dict = {}
    current_time = datetime.now().date()
    st = current_time - timedelta(days=int(30))

    open_count = 0
    clicks_count = 0
    deliveries_count = 0
    total_emails_count = 0
    unsubscribe_count = 0
    error_count = 0
    while st <= current_time:
        if st not in data_dict:
            data_dict[st] = {"clicks": 0, "open": 0}

        open_click_rate = campaign_stats_helper. \
            get_open_click_rate_by_date_and_campaign(st)

        email_results = ready_to_send_email_helper_obj.get_sent_emails_by_date(st)

        for resp in email_results:
            total_emails_count += 1
            if resp['status'] == 'SENT':
                deliveries_count += 1
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

    dates = ['x']
    clicks = ['click']
    open_rate = ['open']
    for key, val in sorted(data_dict.items()):
        dates.append(key)
        clicks.append(val['clicks'])
        open_rate.append(val['open'])
    # deliveries_count = 0
    open_percentage = ''
    click_percentage = ''
    click_percentage = ''
    deliveries_percentage = ''
    unsubscribe_percentage = ''
    total_emails_percentage = ''
    if deliveries_count and total_emails_count:
        open_percentage = round((open_count * 100) / deliveries_count, 2)
        click_percentage = round((clicks_count * 100) / deliveries_count, 2)
        deliveries_percentage = round((deliveries_count * 100) / total_emails_count, 2)
        unsubscribe_percentage = round((unsubscribe_count * 100) / total_emails_count, 2)
        total_emails_percentage = round((total_emails_count * 100) / total_emails_count, 2)
    else:
        open_percentage = ''
        click_percentage = ''
        click_percentage = ''
        # deliveries_percentage = ''
        unsubscribe_percentage = ''
        total_emails_percentage = ''

    context = {"open_count": open_count,
               "clicks_counts": clicks_count,
               "total_emails_count": total_emails_count,
               "deliveries_count": deliveries_count,
               "unsubscribe_count": unsubscribe_count,
               "open_percentage": open_percentage,
               "click_percentage": click_percentage,
               "deliveries_percentage": deliveries_percentage,
               "total_emails_percentage": total_emails_percentage,
               "unsubscribe_percentage": unsubscribe_percentage,
               "dates": dates, "clicks": clicks, "open": open_rate
               }

    return jsonify(context)


#############################
#    According to New UI    #
#############################
@login_required
def ui_create_segments():
    # list_data = list_helper.get_list(request.user)
    user_id = request.user
    list_data = list_helper.get_list(user_id)
    lst_data = []
    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)

    if request.method == 'POST':
        segment_name = request.form['segment_name']
        list_id = request.form['list_id']
        return redirect('/ui/segments/')
    context = {'list_data': lst_data}
    return render_template('ui/create_segments.html', **context)


@login_required
def ui_segments():
    return render_template('ui/segments.html')

