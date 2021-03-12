import traceback
import json
from struct import *
import random
import math
from emailapp.decorate import login_required
from emailapp.sql_helpers import templates, authenticate, user, lists, \
    campaign_helper, email_result, ready_to_send_email_helper, \
    campaign_stats, campaign_winning_combination, emails_unsubscribe, \
    campaign_setup, email_subject, ab_campaigns_helper
from emailapp import app, session, request, redirect, render_template, \
    url_for, bcrypt, jsonify
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


def create_list():
    list_name = 'all user'
    list_id = list_helper.create_list(list_name, request.user)
    user = email_user.get_email_user()
    for emails in user:
        list_helper.add_list_by_id(emails['email'], list_id)


@login_required
def segments():
    list_data = list_helper.get_list(request.user)
    lst_data = []
    list_id = 0
    open_count = []
    clicks_count = []
    open_percentage = 0
    click_percentage = 0
    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])

        all_open_data = list_helper.get_listsegment_open_by_list_id(item['id'])
        for index, val in enumerate(all_open_data):
            open_count.append(val)
        open_count_len = len(open_count)
        open_percentage = int(math.trunc(open_count_len*100)/count)

        all_clicks_data = list_helper.get_listsegment_clicks_by_list_id(item['id'])
        for index, val in enumerate(all_clicks_data):
            clicks_count.append(val)
        clicks_count_len = len(clicks_count)
        clicks_percentage = int(math.trunc(clicks_count_len*100)/count)

        lst = {"id": item['id'], "name": item['list_name'], "count": count,
               "created_on": item['created_on'], "open_len": open_percentage,
               "click_len": clicks_percentage}
        lst_data.append(lst)
    context = {'list_data': lst_data}
    return render_template('segments/segments.html', ** context)


@login_required
def edit_segments(list_id):
    list_data = list_helper.get_list_name_by_listid(list_id)
    list_name = list_data['list_name']

    if request.method == 'POST':
        segment_name = request.form['segment_name']
        list_helper.update_segment_name_by_id(segment_name, list_id)
        return redirect('/segments/')

    context = {'list_name': list_name}
    return render_template('segments/edit_segment.html', **context)


@login_required
def create_segments():
    user_id = request.user
    list_data = list_helper.get_list(user_id)
    if not list_data:
        create_list()
    lst_data = []
    for item in list_data:
        count = list_helper.get_listsegment_count(item['id'])
        lst = {"id": item['id'], "name": item['list_name'], "count": count}
        lst_data.append(lst)

    if request.method == 'POST':
        segment_name = request.form['segment_name']
        list_id = request.form['list_id']

        return redirect('/segments/')
    context = {'list_data': lst_data}
    return render_template('segments/create_segments.html', **context)

