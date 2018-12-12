# coding=utf-8
import urllib
import urllib2
import json
import datetime
import time
import sys
import logging
reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig(format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: '\
                           '%(message)s', level=logging.INFO)

def get_data_time(n=1):
    now = datetime.datetime.now()
    # 递增的时间
    # delta = datetime.timedelta(days=1)
    # 六天后的时间
    endnow = now + datetime.timedelta(days=n)
    # 六天后的时间转换成字符串
    endnow = str(endnow.strftime('%Y-%m-%d'))
    return endnow

def compute_station2station_spendtime_duration(filename):
    """获取2个站点间最多和最少花费时间
    """
    station_spendtime = {}
    with open(filename) as fp:
        for line in fp:
            fields = line.strip().split('\t')
            if len(fields) != 5:
                continue
            key = fields[0] + '_' + fields[1]
            spendtime = int(fields[2]) * 60 + int(fields[3])
            train_num = fields[4]
            if key not in station_spendtime:
                station_spendtime[key] = {}
            min_time = station_spendtime[key].get('min_spendtime', 1000*60)
            max_time = station_spendtime[key].get('max_spendtime', 0)
            if min_time > spendtime:
                station_spendtime[key]['min_spendtime'] = spendtime
                station_spendtime[key]['min_spendtime_str'] = fields[2] + ':' + fields[3]
                station_spendtime[key]['min_trainnum'] = train_num
            if max_time < spendtime:
                station_spendtime[key]['max_spendtime'] = spendtime
                station_spendtime[key]['max_spendtime_str'] = fields[2] + ':' + fields[3]
                station_spendtime[key]['max_tainnum'] = train_num

    for k, v in station_spendtime.items():
        print k + '\t' + json.dumps(v, ensure_ascii=False)


def get_station2station_spendtime_duration(filename):
    station_time = {}
    with open(filename) as fp:
        for line in fp:
            fields = line.strip().split('\t')
            if len(fields) != 2:
                continue
            station_time[fields[0]] = json.loads(fields[1])
    return station_time


def get_station2station_spendtime():
    """获取2个站点间花费时间
    """
    with open('../data/trains.format') as fp:
        for line in fp:
            fields = line.strip().split('\t')
            if len(fields) != 7:
                logging.error("illegal line : %s" % line.strip())
                continue
            train_num = fields[2]
            tmp = fields[-1]
            train_info = json.loads(tmp)

            for i, station_info in enumerate(train_info):
                last_time = station_info['start_time']
                last_station_name = station_info['station_name']
                spend_time = 0
                # lasthour, last_minute = [int(t) for t in last_time.split(':')]
                for j in range(i + 1, len(train_info)):
                    lasthour, last_minute = [int(t) for t in last_time.split(':')]
                    arrive_time = train_info[j]['arrive_time']
                    hour, minute = [int(t) for t in arrive_time.split(':')]
                    station_name = train_info[j]['station_name']
                    if hour < lasthour:
                        curn_spend_time = (24 - lasthour + hour) * 60 + minute - last_minute
                    else:
                        curn_spend_time = (hour-lasthour) * 60 + minute - last_minute
                    if curn_spend_time < 0:
                        print '时间不能是负数！！'
                        continue
                    spend_time += curn_spend_time
                    print last_station_name + "\t" + station_name + '\t' + str(spend_time/60) + '\t' + str(spend_time%60) + '\t' + train_num
                    last_time = arrive_time
                # break
            # break


def get_trains_info(file_name):
    with open(file_name) as fp:
        for line in fp:
            try:
                fields = line.strip().split('\t')
                if len(fields) != 7:
                    logging.error("illegal line : %s" % line.strip())
                    continue
                train_num = fields[2]
                tmp = fields[-1]
                train_info = json.loads(tmp)
                station_list = [info['station_name'] for info in train_info]
                for i, station_name in enumerate(station_list):
                    for j in range(i+1, len(station_list)):
                        print station_name + "\t" + station_list[j] + "\t" + train_num

                # for info in train_info:
                #     print train_num + "\t" + info['station_name'] + "\t" + info['arrive_time'] + "\t" + info['start_time'] + "\t" + info['station_no']
                # break
            except Exception as ex:
                # print line.strip()
                print ex
                continue


def get_trains2station(filename):
    trains_info = {}
    station_set ={}
    with open(filename) as fp:
        for line in fp:
            trains_station = {}
            fields = line.strip().split('\t')
            if len(fields) != 5:
                continue
            trains_name = fields[0]
            trains_station['station_name'] = fields[1]
            trains_station['arrive_time'] = fields[2]
            trains_station['start_time'] = fields[3]
            trains_station['station_no'] = int(fields[4])
            if trains_name not in trains_info:
                trains_info[trains_name] = []
                station_set[trains_name] = set()
            trains_station['trains_name'] = trains_name
            trains_info[trains_name].append(trains_station)
            station_set[trains_name].add(fields[1])

    for name, station_v in trains_info.items():
        station_v = sorted(station_v, key=lambda x: x['station_no'])
    return trains_info, station_set


def get_station2trains(filename):
    station_info = {}
    trains_set = {}
    with open(filename) as fp:
        for line in fp:
            station_trains = {}
            fields = line.strip().split('\t')
            if len(fields) != 5:
                continue
            station_trains['trains_name'] = fields[0]
            station_name = fields[1]
            station_trains['arrive_time'] = fields[2]
            station_trains['start_time'] = fields[3]
            station_trains['station_no'] = int(fields[4])
            if station_name not in station_info:
                station_info[station_name] = []
                trains_set[station_name] = set()
            station_trains['station_name'] = station_name
            station_info[station_name].append(station_trains)
            trains_set[station_name].add(fields[0])

    for name, trains_v in station_info.items():
        trains_v = sorted(trains_v, key=lambda x: x['start_time'])
    return station_info, trains_set


def get_station2station(filename):
    start_station = {}
    end_station = {}
    with open(filename) as fp:
        for line in fp:
            fields = line.strip().split('\t')
            if len(fields) != 3:
                continue
            start_name = fields[0]
            end_name = fields[1]
            if start_name not in start_station:
                start_station[start_name] = set()
            if end_name not in end_station:
                end_station[end_name] = set()
            start_station[start_name].add(end_name)
            end_station[end_name].add(start_name)
    return start_station, end_station


def get_station2staion_time(filename):
    """从文件中读取站点间最长最短花费时间
    """
    station_time = {}
    with open(filename) as fp:
        for line in fp:
            fields = line.strip().split('\t')
            if len(fields) != 2:
                continue
            station_time[fields[0]] = json.loads(fields[1])

    return station_time


def is_good_schedule(station1, station2):
    """获取station1, station2耗时
    """
    ret = {"max_spendtime_str": "100:59", "min_spendtime_str": "100:59", "max_tainnum": "",
           "max_spendtime": 60 * 24 *100, "min_trainnum": "", "min_spendtime": 60 * 24 * 100}
    key = station1 + '_' + station2
    if key in station_time:
        ret = station_time[key]
    return ret


def get_alias_station(s1_name):
    """徐州|徐州东|徐州南|徐州西|徐州北 都是徐州
    """
    if not isinstance(s1_name, unicode):
        s1_name = s1_name.deocde('utf8')
    s1_name_list = [s1_name]
    d = [u'东', u'南', u'西', u'北']
    if s1_name[-1] not in d or len(s1_name) < 3:
        for i in d:
            s1_name_list.append(s1_name + i)
    elif len(s1_name) > 2:
        s1_name_list.append(s1_name[:-1])
        index = d.index(s1_name[-1])
        for i in d:
            if i == d[index]:
                continue
            s1_name_list.append(s1_name[:-1] + i)
    s1_name_list = [i.encode('utf8') for i in s1_name_list]
    return list(set(s1_name_list))

def get_trains(s1_name, s2_name, space=0, topk=20):
    """车站s1到车站s2，space 中间可以间隔的车站数
    """

    s1_name_list = get_alias_station(s1_name)
    s2_name_list = get_alias_station(s2_name)
    # print "|".join(s1_name_list)
    # print '|'.join(s2_name_list)
    ret_list = []
    for i in s1_name_list:
        for j in s2_name_list:
            s1_name = i
            s2_name = j
            # print i, j
            # spendtime = is_good_schedule(s1_name, s2_name)['max_spendtime']
            space_0_json = is_good_schedule(s1_name, s2_name)
            spendtime = space_0_json['max_spendtime']
            space_0_json['start_station'] = s1_name
            space_0_json['end_station'] = s2_name
            # print json.dumps(is_good_schedule(s1_name, s2_name), ensure_ascii=False)
            if space == 0 and space_0_json['max_spendtime'] < 144000:
                ret_list.append(space_0_json)
            if space == 1:
                try:
                    start = start_station[s1_name]
                    end = end_station[s2_name]
                except Exception as ex:
                    continue
                trains_name = start & end
                if len(trains_name) < 0:
                    continue
                for t in trains_name:
                    spendtime_1 = is_good_schedule(s1_name, t)['min_spendtime']
                    spendtime_2 = is_good_schedule(t, s2_name)['min_spendtime']
                    all_spendtime = spendtime_1 + spendtime_2
                    all_spendtime_str = str(all_spendtime / 60) + ':' + str(all_spendtime % 60)
                    if all_spendtime > 2 * spendtime or all_spendtime > 50 * 60 * 24:
                        continue
                    ret_list.append({'station_name':[t], 'min_spendtime':all_spendtime, 'min_spendtime_str':all_spendtime_str,
                                     "start_station":i, 'end_station':j})
            if space == 2:
                try:
                    start = start_station[s1_name]
                    end = end_station[s2_name]
                except Exception as ex:
                    # print 'exception:', s1_name, s2_name
                    continue
                for station in start:
                    dis_1 = is_good_schedule(s1_name, station)
                    dis_1_spendtime = dis_1['min_spendtime']
                    start2 = start_station[station]
                    trains_name = start2 & end
                    if len(trains_name) < 1:
                        continue
                    for train in trains_name:
                        dis_2 = is_good_schedule(station, train)
                        dis_2_spendtime = dis_2['min_spendtime']
                        dis_3 = is_good_schedule(train, s2_name)
                        dis_3_spendtime = dis_3['min_spendtime']
                        all_spendtime = dis_1_spendtime + dis_2_spendtime + dis_3_spendtime
                        all_spendtime_str = str(all_spendtime / 60) + ':' + str(all_spendtime % 60)
                        if all_spendtime > 2 * spendtime or all_spendtime > 50 * 60 * 24:
                            continue
                        ret_list.append({'station_name': [station, train], 'min_spendtime': all_spendtime,
                                         'min_spendtime_str': all_spendtime_str,
                                         "start_station": i, 'end_station': j})
    ret_list = sorted(ret_list, key=lambda x: x['min_spendtime'])[:topk]
    return ret_list


def get_station2station2(s1_name, s2_name):
    # start_trains_info = station_info[s1_name]
    start_trains_set = trains_set[s1_name]
    # end_trains_info = station_info[s2_name]
    end_trains_set = trains_set[s2_name]
    trains_name = start_trains_set & end_trains_set
    return trains_name


if __name__ == '__main__':
    num_set = set()
    # trains_info, station_set = get_trains2station('../data/trains.station')
    station_info, trains_set = get_station2trains('../data/station.trains')
    start_station, end_station = get_station2station('../data/station2station.info')
    # station_time = get_station2staion_time('../data/station2station.spendtime')
    name1 = u'徐州'
    name2 = u'广州'
    station_time = get_station2station_spendtime_duration('../data/station2station.spendtime.duration')
    # get_station2station_spendtime()
    ret = get_trains(name1, name2, space=0)
    print len(ret)
    for i, en in enumerate(ret):
        if i > 20:
            break
        print json.dumps(en, ensure_ascii=False)
    # ret = get_trains(name1, name2, space=2)
    # print ret
    # for i in range(1, 30):
    #     query_date = get_data_time(i)
    #     url = 'http://kyfw.12306.cn/otn/leftTicket/queryA?leftTicketDTO.train_date=query_date&leftTicketDTO.' \
    #           'from_station=start_station&leftTicketDTO.to_station=end_station&purpose_codes=ADULT'
    #     url = url.replace('query_date', query_date)
    #
    #     trains_url = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=train_num&' \
    #                  'from_station_telecode=start_station&to_station_telecode=end_station&depart_date=query_date'
    #     trains_url = trains_url.replace('query_date', query_date)
    #     get_trains_info('../data/trains.format')

    #https://kyfw.12306.cn/otn/resources/js/query/train_list.js
    # get_station_trans(s_map)
    # print s_map
