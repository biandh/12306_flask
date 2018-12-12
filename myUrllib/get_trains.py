# coding=utf-8
import urllib
import urllib2
import json
import datetime
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def get_hot_city(filename):
    name_list = []
    with open(filename) as fp:
        for line in fp:
            name_list.append(line.strip())
    return name_list

def get_data_time(n=1):
    now = datetime.datetime.now()
    # 递增的时间
    # delta = datetime.timedelta(days=1)
    # 六天后的时间
    endnow = now + datetime.timedelta(days=n)
    # 六天后的时间转换成字符串
    endnow = str(endnow.strftime('%Y-%m-%d'))
    return endnow

def get_station_info(filename):
    station_name_map = {}
    with open(filename) as fp:
        for line in fp:
            fields = line.strip().split("\t")
            if len(fields) != 5:
                continue
            if fields[1] not in station_name_map:
                station_name_map[fields[1]] = fields[2]
            else:
                print fields[1], 'is exist !'
    return station_name_map

def get_history_data(filename):
    trans = set()
    with open(filename) as fp:
        for line in fp:
            fields = line.strip().split("\t")
            if len(fields) != 4:
                continue
            trans.add(fields[2])
    return trans


def get_station_trans(s_map):

    trans_info = {}
    hot_city = get_hot_city('../data/hot_city')
    history_trans = get_history_data('../data/trains.txt')
    fp = open('../data/trains.txt', 'a+')

    # for k1, v1 in s_map.items():
    #     for k2, v2 in s_map.items():
    for k1 in hot_city:
        for k2 in hot_city:
            v1 = s_map[k1]
            v2 = s_map[k2]
            if k1 == k2:
                continue
            # k1 = '北京'
            # k2 = '上海'
            # v1 = s_map[k1]
            # v2 = s_map[k2]
            cur_url = url.replace('start_station', v1)
            cur_url = cur_url.replace('end_station', v2)
            try:
                req = urllib2.Request(cur_url)
                res = urllib2.urlopen(req, timeout=5)
            except Exception as ex:
                print 'station_except:\t' + cur_url
                continue
            data = json.loads(res.read())['data']
            print cur_url
            if len(data['result']) == 0:
                print k1 + "\t" + k2 + "\t" + '没有火车！'
                fp.write(k1 + "\t" + k2 + "\t" + '没有火车！' + "\n")
            time.sleep(5)
            for info in data['result']:
                info_list = info.split('|')
                trains = info_list[3]
                if trains in trans_info or trains in history_trans:
                    print k1, k2, trains, 'in history_data'
                    continue
                trains_no = info_list[2]
                cur_trains_url = trains_url.replace('start_station', v1)
                cur_trains_url = cur_trains_url.replace('end_station', v2)
                cur_trains_url = cur_trains_url.replace('train_num', trains_no)
                try:
                    trans_req = urllib2.Request(cur_trains_url)
                    trans_res = urllib2.urlopen(trans_req, timeout=5)
                    trans_data = json.loads(trans_res.read()).get('data', {}).get('data', [])
                    trans_info[trains] = trans_data
                    time.sleep(0.2)
                    print k1 + "\t" + k2 + "\t" + trains + "\t" + json.dumps(trans_data, ensure_ascii=False)
                    fp.write(k1 + "\t" + k2 + "\t" + trains + "\t" + json.dumps(trans_data, ensure_ascii=False) + '\n')
                except Exception as ex:
                    print 'trans_except:\t'+cur_trains_url
                    continue
                # print trans_data
                # break
            # break
                # print info_list
            # print data
        # break


def get_history_trains_info(filename):

    trains_num = set()
    with open(filename) as fp:
        for line in fp:
            fields = line.strip().split('\t')
            if len(fields) != 7:
                continue
            if '{' not in fields[6] and '}' not in fields[6]:
                continue
            trains_num.add(fields[2])
    return trains_num


def deal_train_no(train_no):
    alpha_list = ['A','B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    alpha_list2 = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    if train_no[-1].isdigit():
        digit = int(train_no[-1])
        may_digits = [train_no[:-1] + str(digit-1), train_no[:-1] + str(digit +1)]
        return may_digits
    elif train_no[-1].isalpha():
        alpha = train_no[-1]
        if alpha not in alpha_list:
            alpha_list = alpha_list2
            if alpha not in alpha_list:
                print '未知的末尾号码', train_no
                return []
        index = alpha_list.index(alpha)
        return [train_no[:-1]+alpha_list[index-1], train_no[:-1] + alpha_list[index+1]]
    else:
        print '车号末尾不属于字母或数字', train_no
        return []


def url_request(cur_trains_url, last_num, cur_num):
    cur_trains_url = cur_trains_url.replace(last_num, cur_num)
    trans_req = urllib2.Request(cur_trains_url)
    trans_res = urllib2.urlopen(trans_req, timeout=3)
    time_data = json.loads(trans_res.read()).get('data', {}).get('data', [])
    return time_data


def get_trains_info(s_map):

    trains_history_num = get_history_trains_info('../data/trains_info')
    with open('../data/train_list.json') as fp:
        data = fp.read()
        js_data = json.loads(data)
        for k, v in js_data.items():
            # print k
            for k_2, v2 in v.items():
                for trains_inf in v2:
                    train_no = trains_inf.get('train_no')
                    station_train_code = trains_inf.get('station_train_code')
                    trains_data = station_train_code.replace("（", "(").split('(')
                    if len(trains_data) != 2:
                        print '长度不为2\t' + station_train_code
                        continue
                    num = trains_data[0]
                    if num in num_set or num.encode('utf8') in trains_history_num:
                        # print num, 'exists'
                        continue
                    station_data = trains_data[1].replace('）', ")").replace(')', "").split('-')
                    if len(station_data) != 2:
                        print '长度不为22\t' + station_train_code
                    cur_trains_url = 'dadd'
                    try:
                        k1 = station_data[0].encode('utf8')
                        k2 = station_data[1].encode('utf8')
                        v1 = s_map[k1]
                        v2 = s_map[k2]
                        cur_trains_url = trains_url.replace('start_station', v1)
                        cur_trains_url = cur_trains_url.replace('end_station', v2)
                        cur_trains_url = cur_trains_url.replace('train_num', train_no)
                        try:
                            trans_req = urllib2.Request(cur_trains_url)
                            trans_res = urllib2.urlopen(trans_req, timeout=3)
                            time_data = json.loads(trans_res.read()).get('data', {}).get('data', [])
                        except Exception as ex:
                            time_data = []
                        if '{' not in json.dumps(time_data, ensure_ascii=False):
                            may_train_no = deal_train_no(train_no)
                            if len(may_train_no) == 0:
                                continue
                            tmp_no = train_no
                            time.sleep(1)
                            for no in may_train_no:
                                time_data = url_request(cur_trains_url, tmp_no, no)
                                tmp_no = no
                                if '{' in json.dumps(time_data, ensure_ascii=False):
                                    train_no = no
                                    break
                        print k + "\t" + k_2 + "\t" + num + "\t" + train_no + "\t" + station_data[0] + "\t" + station_data[1] + "\t" + json.dumps(time_data, ensure_ascii=False)
                        if '{' in json.dumps(time_data, ensure_ascii=False):
                            num_set.add(num)
                    except Exception as ex:
                        # print ex
                        # print cur_trains_url
                        print('exception:\t' + k1 + '\t' + k2 + '\t' + num + "\t" + train_no)
                        continue
                # break


if __name__ == '__main__':
    num_set = set()
    for i in range(1, 30):
        query_date = get_data_time(i)
        url = 'http://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date=query_date&leftTicketDTO.' \
              'from_station=start_station&leftTicketDTO.to_station=end_station&purpose_codes=ADULT'
        url = url.replace('query_date', query_date)

        trains_url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=train_num&' \
                     'from_station_telecode=start_station&to_station_telecode=end_station&depart_date=query_date'
        trains_url = trains_url.replace('query_date', query_date)

        s_map = get_station_info('../data/station_name.format')
        get_trains_info(s_map)
    #https://kyfw.12306.cn/otn/resources/js/query/train_list.js
    # get_station_trans(s_map)
    # print s_map
