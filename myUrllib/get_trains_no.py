# coding=utf-8
import urllib
import urllib2
import json
import datetime
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

url = 'http://kyfw.12306.cn/otn/resources/js/query/train_list.js'
# req = urllib2.Request(url)
# res = urllib2.urlopen(req, timeout=20)
# data = json.loads(res.read())['data']
# print data

trains_url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=train_num&' \
             'from_station_telecode=start_station&to_station_telecode=end_station&depart_date=query_date'
def get_data_time(n=3):
    now = datetime.datetime.now()
    # 递增的时间
    # delta = datetime.timedelta(days=1)
    # 六天后的时间
    endnow = now + datetime.timedelta(days=n)
    # 六天后的时间转换成字符串
    endnow = str(endnow.strftime('%Y-%m-%d'))
    return endnow

query_date = get_data_time()
trains_url = trains_url.replace('query_date', query_date)

with open('../data/train_list.json') as fp:
    data = fp.read()
    js_data = json.loads(data)
    num_set = set()
    for k, v in js_data.items():
        # print k
        for k2, v2 in v.items():
            for trains_inf in v2:
                train_no = trains_inf.get('train_no')
                station_train_code = trains_inf.get('station_train_code')
                trains_data = station_train_code.replace("（", "(").split('(')
                if len(trains_data) != 2:
                    print '长度不为2\t' + station_train_code
                    continue
                num = trains_data[0]
                if num in num_set:
                    continue
                station_data = trains_data[1].replace('）', ")").replace(')', "").split('-')
                if len(station_data) != 2:
                    print '长度不为22\t'+ station_train_code
                print k + "\t" + k2 + "\t" + num + "\t" + train_no + "\t" + station_data[0] + "\t" + station_data[1]
                num_set.add(num)
        # break