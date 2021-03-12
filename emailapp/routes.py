from emailapp import *
from emailapp.views.campaigns import campaigns, create_campaigns, \
    one_time_campaign_setup, subject_line, content_templates, \
    send_time, one_time_campaign_create, ab_test, \
    ab_subject_lines, ab_content_templates, ab_send_time, campaigns_edit, \
    graph, graph_data, campaign_pause, campaign_resume

from emailapp.views.segments import segments, create_segments, edit_segments

from emailapp.views.accounts import register, login, delete_user,\
    create_user, signout, email_opened, click_tracking, \
    send_system_email, email_unsubscribe, bounce, reject, notifications


#############################
#        Accounts           #
#############################

"""" User Registration."""


@app.route('/register/', methods=['GET', 'POST'])
def route_user_register():
    return register()


""" User Login. """


@app.route('/login/', methods=['GET', 'POST'])
def route_user_login():
    return login()


""" User Logout """


@app.route('/signout/', methods=['GET', 'POST'])
def route_user_signout():
    return signout()


@app.route('/v1/email/queue/add/', methods=['GET', 'POST'])
def route_send_system_email():
    return send_system_email()


""" Open Email handler """


@app.route('/e/o/<string:params>/', methods=['GET', 'POST'])
def route_open_email(params):
    return email_opened(params)


""" Click link handler """


@app.route('/e/c/<string:params>/', methods=['GET'])
def route_click_tracking(params):
    return click_tracking(params)


""" unsubscribe """


@app.route('/unsubscribe/<int:segment_id>/<int:campaign_id>/', methods=['GET'])
def route_unsubscribe(segment_id, campaign_id):
    app.logger.info(segment_id)
    app.logger.info(campaign_id)
    return email_unsubscribe(segment_id, campaign_id)


@app.route('/e/bounce/', methods=['GET', 'POST'])
def route_bounce():
    return bounce()


@app.route('/e/reject/', methods=['GET', 'POST'])
def route_reject():
    return reject()


@app.route('/ses/notifications/', methods=['GET', 'POST'])
def route_notifications():
    return notifications()


#############################
#       Campaigns           #
#############################
@app.route('/campaigns/', methods=['GET', 'POST'])
def route_campaigns():
    return campaigns()


""" Create Campaign """


@app.route('/campaigns/create/', methods=['GET', 'POST'])
def route_create_campaigns():
    return create_campaigns()


""" create One-time Campaign """


@app.route('/campaigns/one_time_campaign/setup/', methods=['GET', 'POST'])
def route_one_time_campaign_setup():
    return one_time_campaign_setup()


@app.route('/campaigns/one_time_campaign/setup/<int:campaign_id>/<string:params>/',
           methods=['GET', 'POST'])
def route_one_time_campaign_setup_by_id(campaign_id, params):
    return one_time_campaign_setup(campaign_id, params)


""" set the emails subject """


@app.route('/campaigns/subject_line/<int:campaign_id>/',
           methods=['GET', 'POST'])
def route_subject_line(campaign_id):
    return subject_line(campaign_id)


""" set template for one-time campaigns"""


@app.route('/campaigns/content_templates/<int:campaign_id>/',
           methods=['GET', 'POST'])
def route_content_templates_by_id(campaign_id):
    return content_templates(campaign_id)


""" set send time for the one-time campaigns """


@app.route('/campaigns/send_time/<int:campaign_id>/',
           methods=['GET', 'POST'])
def route_send_time_by_id(campaign_id):
    return send_time(campaign_id)


@app.route('/campaigns/pause/', methods=['GET', 'POST'])
def route_campaign_pause():
    return campaign_pause()


@app.route('/campaigns/resume/', methods=['GET', 'POST'])
def route_campaign_resume():
    return campaign_resume()


""" create A/B Test campaigns """


@app.route('/campaigns/one_time_campaign/create/', methods=['GET', 'POST'])
def route_one_time_campaign_create():
    return one_time_campaign_create()


""" create A/B Test campaing when AB campaign id is found """


@app.route('/campaigns/one_time_campaign/create/<int:campaign_id>/<string:params>/',
           methods=['GET', 'POST'])
def route_one_time_campaign_create_by_id(campaign_id, params):
    return one_time_campaign_create(campaign_id, params)


""" set the no of subjects, templates and send time """


@app.route('/campaigns/ab_test/<int:campaign_id>/', methods=['GET', 'POST'])
def route_ab_test(campaign_id):
    return ab_test(campaign_id)


""" set the email subject """


@app.route('/campaigns/subject_lines/<int:campaign_id>/',
           methods=['GET', 'POST'])
def route_ab_subject_lines(campaign_id):
    return ab_subject_lines(campaign_id)


""" set the no of templates for the AB campaings """


@app.route('/campaigns/ab_content_templates/<int:campaign_id>/',
           methods=['GET', 'POST'])
def route_ab_content_templates(campaign_id):
    return ab_content_templates(campaign_id)


""" A/B Test send time """


@app.route('/campaigns/ab_send_time/<int:campaign_id>/',
           methods=['GET', 'POST'])
def route_ab_send_time(campaign_id):
    return ab_send_time(campaign_id)


""" set the campaign Dashboard graph """


@app.route('/', methods=['GET'])
@app.route('/campaigns/dashboard/', methods=['GET', 'POST'])
def route_graph():
    return graph()


@app.route('/campaigns/dashboard/<int:campaign_id>/<string:params>/', methods=['GET', 'POST'])
def route_graph_by_id(campaign_id, params):
    return graph(campaign_id, params)


""" set the graph data """


@app.route('/graph_data/', methods=['GET', 'POST'])
def route_graph_data():
    return graph_data()


@app.route('/graph_data/<int:campaign_id>/<string:params>/', methods=['GET', 'POST'])
def route_graph_data_by_id(campaign_id, params):
    return graph_data(campaign_id, params)


""" edit the one-time and A/B Test campaigns """


@app.route('/campaigns/<string:params>/<int:campaign_id>/edit/',
           methods=['GET', 'POST'])
def route_campaigns_edit(campaign_id, params):
    return campaigns_edit(campaign_id, params)


#############################
#        segments           #
#############################


""" Routes for segments """


@app.route('/segments/', methods=['GET', 'POST'])
def route_segments():
    return segments()


""" create segments """


@app.route('/segments/create/', methods=['GET', 'POST'])
def route_create_segments():
    return create_segments()


""" edit segments """


@app.route('/segments/<int:list_id>/edit/', methods=['GET', 'POST'])
def route_edit_segments(list_id):
    return edit_segments(list_id)
