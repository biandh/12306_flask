# -*- coding: utf8 -*-
import sys
import json
import logging
import time
import datetime
import re
from urllib import quote
reload(sys)
sys.setdefaultencoding('utf8')
from flask import Flask, redirect
from flask import url_for, flash
from flask import request, session, g, render_template

from form.forms import QueryTricket, LoginForm
import os
from flask_ckeditor import CKEditor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    '../inter/')))
from GetTrainStatus import QueryTecket
from CheckUser import checkUser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    '../init/')))
from qiangpiao import QiangPiao
from login import GoLogin

logging.basicConfig(format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: '\
                           '%(message)s', level=logging.INFO)


app = Flask(__name__)
app.secret_key = 'xxxbdsdfadada'
app.config['UPLOAD_PATH'] = os.path.join(app.root_path, 'uploads')
app.config['ALLOWED_EXTENSIONS'] = ['png', 'jpg', 'jpeg', 'gif']
app.config['CKEDITOR_SERVE_LOCAL'] = True
ckeditor = CKEditor(app)
q_tricket = QueryTecket('')
station_name_map = q_tricket.station_info_dict
ticket_obj = QiangPiao()
login_obj = GoLogin(ticket_obj, False)
check_user_obj = checkUser(ticket_obj)


def to_string(en):
    return json.dumps(en, ensure_ascii=False)


@app.template_global()
def link_to_12306(from_s, to_s, date):
    rule = u'【(.+?)】'
    if u'【' in from_s:
        from_s = re.findall(rule, from_s)[0]
        from_s_en = station_name_map.get(from_s, 'null')
    if u'【' in to_s:
        to_s = re.findall(rule, to_s)[0]
        to_s_en = station_name_map.get(to_s, 'null')
    base_url = 'https://kyfw.12306.cn/otn/leftTicket/init?' \
               'linktypeid=dc&fs=%s,%s&ts=%s,%s&date=%s&flag=N,N,Y'
    # from_s_encode = quote(from_s)
    # to_s_encode = quote(to_s)
    url = base_url % (from_s, from_s_en, to_s, to_s_en, date)
    return url

@app.template_global()
def remove_station_name_decotate(from_s):
    rule = u'【(.+?)】'
    ret = re.findall(rule, from_s)
    if len(ret) > 0:
        return ret[0]
    return from_s

@app.route('/login', methods=['GET', 'POST'])
def login():
    to_day = datetime.datetime.today().strftime('%Y-%m-%d')
    form = LoginForm()
    qiangpiao_info = {}
    from_station = request.form.get('from_station', '请输入始发站名称')
    to_station = request.form.get('to_station', '请输入到达站名称')
    qiangpiao_info['from_station'] = remove_station_name_decotate(from_station)
    qiangpiao_info['to_station'] = remove_station_name_decotate(to_station)
    qiangpiao_info['trains'] = request.form.get('trains', '请输入抢票车次')
    qiangpiao_info['username'] = session.get('username', '请输入乘车人姓名')
    re_form = request.form
    qiangpiao_info['date'] = request.form.get('date', to_day)
    username = re_form.get('username', '')
    if not os.path.exists('../log/' + username):
        os.mkdir('../log/' + username)
    log_files = os.listdir('../log/' + username)

    for files in log_files:
        session[files] = 1
        # with open(files) as fp:
        #     lines = fp.readlines()  # 读取所有行
        #     first_line = lines[-1]
        #     if '预定单号' in first_line:
    pwd = re_form.get('password', '')
    rand_code = re_form.get('rand_code', '')
    is_connect = check_user_obj.user_is_connecting()

    if is_connect:
        return redirect(url_for('snap_up_trainTicket',
                                qiangpiao=json.dumps(qiangpiao_info, ensure_ascii=False)))

    if username.strip() == '' or len(pwd.strip()) < 6 or len(rand_code) < 2:
        pass
    else:
        mess, name = login_obj.go_login_v2(username, pwd, rand_code=rand_code)
        if u'登录成功' in mess:
            session['is_check'] = True
            session['username'] = name
            session['accountname'] = username
            qiangpiao_info['username'] = name
            check_user_obj.set_timeout()
            return redirect(url_for('snap_up_trainTicket',
                                    qiangpiao=json.dumps(qiangpiao_info, ensure_ascii=False)))
    login_obj.get_code()
    return render_template('login.html', form=form,
                           qiangpiao=qiangpiao_info, cur_time=time.time())


@app.route('/login2/<form>', methods=['GET', 'POST'])
def login2(form):
    # form = '{}'
    to_day = datetime.datetime.today().strftime('%Y-%m-%d')
    form = json.loads(form)
    login_form = LoginForm()
    qiangpiao_info = {}
    from_station = form.get('from_station', '请输入始发站名称')
    to_station = form.get('to_station', '请输入到达站名称')
    qiangpiao_info['from_station'] = remove_station_name_decotate(from_station)
    qiangpiao_info['to_station'] = remove_station_name_decotate(to_station)
    qiangpiao_info['trains'] = form.get('trains', '请输入抢票车次')
    qiangpiao_info['username'] = session.get('username', '请输入乘车人姓名')

    qiangpiao_info['date'] = form.get('date', to_day)
    login_obj.get_code()
    return render_template('login.html', form=login_form,
                           qiangpiao=qiangpiao_info, cur_time=time.time())


@app.route('/snap_up_trainTicket', methods=['GET', 'POST'])
def snap_up_trainTicket():
    # form = LoginForm()
    qiangpiao = json.loads(request.args.get('qiangpiao', '{}'))
    if not check_user_obj.user_is_connecting() or not session['is_check']:
        flash('登录过期，请重新登录！')
        return redirect(url_for('login'))
    username = session.get('username', 'default')
    return render_template('snap_up_trainTicket_static.html',
                           username=username, qiangpiao=qiangpiao, message = '')


def read(usename, filename):
    qiangpiao_log = []
    name = '../log/' + usename.encode('utf8') + '/' + filename.encode('utf8')
    try:
        with open(name) as fp:
            for line in fp:
                qiangpiao_log.append(line.strip().decode('utf8'))
    except Exception as ex:
        logging.info(str(ex))
    return qiangpiao_log


def write(usename, filename, log_info):
    name = '../log/' + usename.encode('utf8') + '/' + filename.encode('utf8')
    fp = open(name, 'a+')
    for info in log_info:
        fp.write(info.strip() + '\n')
    fp.close()


@app.route('/snap_up_trainTicket2', methods=['POST', 'GET'])
def snap_up_trainTicket2():
    # form = LoginForm()
    r = request
    form = request.form
    tmp = {}
    for k, v in form.items():
        tmp[k] = v
    if not session['is_check'] or not check_user_obj.user_is_connecting():
        flash('登录过期，请重新登录！')
        return redirect(url_for('login2', form=json.dumps(tmp, ensure_ascii=False),
                                url='snap_up_trainTicket2'))
    username = session.get('username', 'default')
    accountname = session.get('accountname', 'default')
    qiangpiao_info = {}
    for k, v in form.items():
        if k == 'log_info':
            continue
        qiangpiao_info[k] = v
    key = qiangpiao_info['trains'] + '_' + qiangpiao_info['person_name'] + \
          '_' + qiangpiao_info['date']
    qiangpiao_info['date'] = [qiangpiao_info['date']]
    qiangpiao_info['person_name'] = re.split(u'，|,|、|/| ',qiangpiao_info['person_name'])
    qiangpiao_info['seat'] = [qiangpiao_info['seat']]

    if session.get(key, None) is None:
        session[key] = 1
        session[key + '_count'] = 0
        log_info = []
    else:
        log_info = read(accountname, key)
    cur_log_info = []
    if log_info == [] or u'预定单号' not in log_info[-1] and u'未处理的订单' not in log_info[-1]:
        try:
            session[key + '_count'] += 1
        except:
            session[key] = 1
            session[key + '_count'] = 1
        ticket_obj.go_qiangpiao(qiangpiao_info, cur_log_info, session[key + '_count'])
        message = ''
        if u'站点输入有误' in cur_log_info[-1]:
            flash(u'站点输入有误')
            message = u'站点输入有误'
            return render_template('snap_up_trainTicket_static.html',
                                   username=username, qiangpiao=form,
                                   message=message)
        elif u'联系人不在列表中' in cur_log_info[-1]:
            flash(u'联系人不在列表中!')
            message = u'联系人不在列表中!'
            return render_template('snap_up_trainTicket_static.html',
                                   username=username, qiangpiao=form,
                                   message=message)
        write(accountname, key, cur_log_info)
        log_info.extend(cur_log_info)
        return render_template('snap_up_trainTicket.html',
                               username=username, form=form,
                               log_info=log_info[::-1][:100],
                               log_str = "\n".join(log_info))

    log_info.extend(cur_log_info)
    return render_template('snap_up_trainTicket_end.html',
                           username=username, form=form,
                           log_info=log_info[::-1][:100])


@app.route('/', methods=['GET','POST'])
@app.route('/query_tricket', methods=['GET','POST'])
def query_tricket():
    col_name = [u'车次', u'发站', u'到站', u'发车', u'到达', u'耗时',
                u'无座', u'硬座', u'硬卧', u'软卧', u'高软', u'二等',
                u'一等', u'商务', u'动卧', u'--']
    form = QueryTricket()
    day = request.form.get('day', 'NULL')
    # print day
    if form.validate_on_submit():
        # print form.data
        types = 0
        from_station = form.start_station.data.decode('utf8')
        to_station = form.end_station.data.decode('utf8')
        date_str = [day]
        yuezhan_trains = form.yuezhan_trains.data.decode('utf8').upper()
        num = 0
        if form.huancheng_num.data and form.huancheng_num.data.isdigit():
            num = int(form.huancheng_num.data)
        q_tricket.station_dates = date_str
        if yuezhan_trains != '' and len(yuezhan_trains) > 2:
            queryResult = q_tricket.get_trains_status(from_station, to_station, [yuezhan_trains], True)
            queryResult.insert(0, [col_name])
        else:
            queryResult, types = q_tricket.train_transfer_status(from_station, to_station, num)
            if types == 0:
                queryResult.insert(0, [col_name])
            else:
                queryResult.insert(0, [col_name, col_name])
        if types != 0:
            return render_template('query_result_span.html', date=date_str[0], queryResult=queryResult)
        return render_template('query_result.html', date = date_str[0], queryResult=queryResult,
                               station_name_map = station_name_map)
    elif len(form.errors) > 0:
        for k, v in form.errors.items():
            flash('%s: %s' % (k, '\n'.join(v)))
    return render_template('12306_query_tricket.html', form=form)


if __name__ == '__main__':
    app.jinja_env.globals['link_to_12306'] = link_to_12306
    app.jinja_env.globals['enumerate'] = enumerate
    app.jinja_env.globals['len'] = len
    app.jinja_env.globals['range'] = range
    app.jinja_env.globals['to_string'] = to_string
    app.jinja_env.add_extension('jinja2.ext.do')
    app.run()