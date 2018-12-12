# -*- coding=utf-8 -*-
import datetime
import random
import socket
import sys
import threading
import time
import wrapcache
import logging
import json
import os
import traceback
from config import urlConf
from myUrllib.httpUtils import HTTPClient
import math
import copy
import datetime
import wrapcache
from config.TicketEnmu import ticket
reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: '\
                           '%(message)s', level=logging.INFO)
g_cur_path = os.path.dirname(__file__) + '/'
train_info_path = g_cur_path + '../config/trains.format'
station_info_path = g_cur_path + '../config/station_name.format'


class QueryTecket:
    """
    查询接口
    """

    def __init__(self, session, station_dates=None):
        self.httpClint = HTTPClient()
        self.urls = urlConf.urls
        self.qiangpiao = True
        self.session = session
        if station_dates is None:
            station_dates = (datetime.date.today() + datetime.timedelta(2)).strftime('%Y-%m-%d')
        # print station_dates
        self.station_dates = station_dates if isinstance(station_dates, list) else [station_dates]
        self.ticket_black_list = dict()
        self.train_info_dict = self.get_train_info(train_info_path)
        self.station_info_dict, self.re_station_info_dict = self.get_station_info(station_info_path)
        self.start_station, self.end_station = self.get_station2station_file('../data/station2station.info')
        self.station_time = self.get_station2station_spendtime_duration('../data/station2station.spendtime.duration')

    def get_station2station_spendtime_duration(self, filename):
        station_time = {}
        with open(filename) as fp:
            for line in fp:
                fields = line.strip().decode('utf8').split('\t')
                if len(fields) != 2:
                    continue
                station_time[fields[0]] = json.loads(fields[1])
        return station_time

    def get_station2station_file(self, filename):
        start_station = {}
        end_station = {}
        with open(filename) as fp:
            for line in fp:
                fields = line.strip().decode('utf8').split('\t')
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

    def get_train_info(self, filename):
        """读取火车车次信息，包括经过站，时间等
        """
        train_info_dict = {}
        with open(filename) as fp:
            for line in fp:
                line_arr = line.decode('utf8').strip().split('\t')
                if len(line_arr) != 7:
                    continue
                train_name = line_arr[2].strip()
                train_info = json.loads(line_arr[-1])
                train_info_dict[train_name] = train_info
        return train_info_dict

    def get_station_info(self, filename):
        """读取火车站次信息，包括站次名，站次简称
        """
        station_info_dict = {}
        re_station_info_dict = {}
        with open(filename) as fp:
            for line in fp:
                line_arr = line.decode('utf8').strip().split('\t')
                if len(line_arr) != 5:
                    continue
                station_name = line_arr[1].strip()
                staion_info = line_arr[2]
                station_info_dict[station_name] = staion_info
                re_station_info_dict[staion_info] = station_name
        return station_info_dict, re_station_info_dict

    def get_train_station(self, train_num):
        """获取车次沿路经过车站
        """
        train_info = self.train_info_dict[train_num]
        train_station = [info['station_name'] for info in train_info]
        return train_station

    def get_ticket_status(self, train_num, station_1, station_2):
        """获取车次指定站点间状态
        """
        pass

    def get_trains_station_index(self, station, trains_station, station_alias = []):
        """获取车次经过的某个站点的索引，主要考虑到会出先，北京，北京南，这种情况
        """
        suffex = [u'南', u'东', u'西', u'北']
        if station in trains_station:
            return trains_station.index(station)

        for station in station_alias:
            if station in trains_station:
                return trains_station.index(station)

        if not (any(i == station[-1] for i in suffex) and len(station) > 2):
            for i in suffex:
                if station + i in trains_station:
                    return trains_station.index(station + i)
        else:
            if station[:-1] in trains_station:
                return trains_station.index(station[:-1])
            for i in suffex:
                if station[:-1] + i in trains_station:
                    return trains_station.index(station[:-1] + i)
        return -1

    def get_trains_status(self, station_1, station_2, train_no_list=[], span=False):
        """指定车次状态查询，支持越站查询
        """
        ret_list = []
        station_tuple = []
        station_tuple.append([station_1, station_2])
        span_list = []
        span_list.append([0, 0, 100])
        if len(train_no_list) > 0:
            start_alias, end_alias = self.get_online_alias(station_1, station_2)
        for i, train_no in enumerate(train_no_list):
            station_list = self.get_train_station(train_no)
            try:
                if span:
                    index_1 = self.get_trains_station_index(station_1, station_list, start_alias)
                    index_2 = self.get_trains_station_index(station_2, station_list, end_alias)
                    span_num = index_2 - index_1
                    for i in range(max(0, index_1 - 3), index_1 + 1):
                        for j in range(index_1 + 1, index_2 + 4):
                            if i == index_1 and j == index_2:
                                continue
                            station_tuple.append([station_list[i], station_list[j]])
                            span_list.append([index_1 - i, index_2 - j, span_num])
            except Exception as ex:
                logging.error('station_1: %s, station_2: %s' % (station_1, station_2))
                logging.error(traceback.format_exc())

        for i, station in enumerate(station_tuple):
            time.sleep(0.5)
            ticke_status_list = self.sendQuery(station[0], station[1], train_no_list)

            for j, ticke_status in enumerate(ticke_status_list):
                if span_list[i][0] > 0:
                    ticke_status_list[j][1] = '【' + ticke_status[1] + '】<--多买' + str(span_list[i][0]) + '站--' + station_1
                if span_list[i][1] > span_list[i][2] / 2:
                    ticke_status_list[j][2] = station_1 + '买' + str(span_list[i][2] - span_list[i][1]) + '站-->【' + ticke_status[2] + '】-->' + station_2
                elif span_list[i][1] > 0:
                    ticke_status_list[j][2] = '【' + ticke_status[2] + '】<--少买' + str(span_list[i][1]) + '站--' + station_2
                elif span_list[i][1] != 0:
                    ticke_status_list[j][2] = station_2 + '--多买' + str(abs(span_list[i][1])) + '站-->【' + ticke_status[2] + '】'

                if '【' not in ticke_status_list[j][1]:
                    ticke_status_list[j][1] = '【' + ticke_status[1] + '】'
                if '【' not in ticke_status_list[j][2]:
                    ticke_status_list[j][2] = '【' + ticke_status[2] + '】'

            ret_list.append(ticke_status_list)
            # print json.dumps(ticke_json, ensure_ascii=False)
        return ret_list

    def get_station2station_status(self, station_1, station_2, start_time='', end_time=''):
        """直接查询站点间车次信息
        """
        pass

    def station_seat(self, index):
        """
        获取车票对应坐席
        :return:
        """
        seat = {'商务座': 32,
                '一等座': 31,
                '二等座': 30,
                '特等座': 25,
                  '软卧': 23,
                  '硬卧': 28,
                  '硬座': 29,
                  '无座': 26,
                }
        return seat[index]

    def sendQuery(self, from_station, to_station, train_no_list=None,):
        """
        查询
        :return:
        """
        from_station_en = self.station_info_dict[from_station]
        to_station_en = self.station_info_dict[to_station]
        ret_list = []
        for station_date in self.station_dates:
            print station_date
            select_url = copy.copy(self.urls["select_url"])
            select_url["req_url"] = select_url["req_url"].format(station_date, from_station_en, to_station_en)
            station_ticket = self.httpClint.send(select_url)
            value = station_ticket.get("data", "")
            if not value:
                logging.info(u'{0}-{1} 车次坐席查询为空'.format(from_station, to_station))
            else:
                result = value.get('result', [])
                if result == []:
                    return ret_list
                for i in result:
                    ticket_info = i.split('|')
                    if (ticket_info[11] != u"Y" or ticket_info[1] != u"预订") and u'无' not in i:  # 筛选未在开始时间内的车次
                        logging.info(u"车次配置信息: %s --> %s 时间: %s 有误，或者返回数据异常，请检查: %s " %(from_station, to_station, station_date, json.dumps(ticket_info, ensure_ascii=False)))
                        continue
                    if (ticket_info[11] != u"Y" or ticket_info[1] != u"预订") and u'无' in i and not self.qiangpiao:
                        continue
                    # for j in xrange(len(self._station_seat)):
                    tmp_list = []
                    secretStr = ticket_info[0]
                    train_no = ticket_info[3]
                    if train_no_list is not None and len(train_no_list) > 0 and train_no not in train_no_list:
                        continue
                    train_from_station = ticket_info[6]
                    train_to_station = ticket_info[7]
                    start_time = ticket_info[8]
                    end_time = ticket_info[9]
                    duration_time = ticket_info[10]
                    date_time = ticket_info[13]
                    seat_not = ticket_info[26]
                    seat_ying = ticket_info[29]
                    yingwo = ticket_info[28]
                    ruanwo = ticket_info[23]
                    gaoji_ruanwo = ticket_info[21]
                    seat_2 = ticket_info[30]
                    seat_1 = ticket_info[31]
                    seat_0 = ticket_info[32]
                    dongwo = ticket_info[33]

                    tmp_list.append(ticket_info[3])
                    tmp_list.append(self.re_station_info_dict[ticket_info[6].strip()])
                    tmp_list.append(self.re_station_info_dict[ticket_info[7].strip()])
                    tmp_list.append(ticket_info[8])
                    tmp_list.append(ticket_info[9])
                    tmp_list.append(ticket_info[10])
                    # tmp_list.append(ticket_info[13])
                    # tmp_list.append(station_date)
                    tmp_list.append(ticket_info[26])
                    tmp_list.append(ticket_info[29])
                    tmp_list.append(ticket_info[28])
                    tmp_list.append(ticket_info[23])
                    tmp_list.append(ticket_info[21])
                    tmp_list.append(ticket_info[30])
                    tmp_list.append(ticket_info[31])
                    tmp_list.append(ticket_info[32])
                    tmp_list.append(ticket_info[33])
                    if ticket_info[11] != u"Y" or ticket_info[1] != u"预订":
                        tmp_list.append(u'抢票')
                    else:
                        tmp_list.append(u'预定')
                    ret_list.append(tmp_list)

        for ticket_info in ret_list:
            # ticket_info = i.split('|')
            for i, info in enumerate(ticket_info):
                if info == '':
                    info = u'--'
                    ticket_info[i] = info
        return ret_list

    def get_alias_station(self, s1_name):
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
        return list(set(s1_name_list))

    def is_good_schedule(self, station1, station2):
        """获取station1, station2耗时
        """
        ret = {"max_spendtime_str": "100:59", "min_spendtime_str": "100:59", "max_tainnum": "",
               "max_spendtime": 60 * 24 * 100, "min_trainnum": "", "min_spendtime": 60 * 24 * 100}
        key = station1 + '_' + station2
        if key in self.station_time:
            ret = self.station_time[key]
        return ret

    def get_station2station(self, s1_name_list, s2_name_list, space=0, topk=20):
        """获取station1到station2之间换乘可能经过的车站
           span 换乘几次
           topk 花费时间最少的k个换乘车站
        """
        # print "|".join(s1_name_list)
        # print '|'.join(s2_name_list)
        ret_list = []
        station_set = set()
        for i in s1_name_list:
            for j in s2_name_list:
                s1_name = i
                s2_name = j
                # print i, j
                # spendtime = is_good_schedule(s1_name, s2_name)['max_spendtime']
                space_0_json = self.is_good_schedule(s1_name, s2_name)
                spendtime = space_0_json['max_spendtime']
                space_0_json['start_station'] = s1_name
                space_0_json['end_station'] = s2_name
                # print json.dumps(is_good_schedule(s1_name, s2_name), ensure_ascii=False)
                if space == 0 and space_0_json['max_spendtime'] < 144000:
                    ret_list.append(space_0_json)
                if space == 1:
                    try:
                        start = self.start_station[s1_name]
                        end = self.end_station[s2_name]
                    except Exception as ex:
                        continue
                    trains_name = start & end
                    if len(trains_name) < 0:
                        continue
                    for t in trains_name:
                        if t in station_set or t in s1_name_list or t in s2_name_list:
                            continue
                        station_set.add(t)
                        if len(t) > 2 and t[-1] in u'东南西北' and t[:-1] in trains_name:
                            continue
                        station_set.add(t)
                        if t + u'南' in station_set or t + u'北' in station_set or t + u'西' in station_set or \
                                t + u'东' in station_set:
                            station_set.add(t + u'南')
                            station_set.add(t + u'北')
                            station_set.add(t + u'西')
                            station_set.add(t + u'东')
                            continue

                        spendtime_1 = self.is_good_schedule(s1_name, t)['min_spendtime']
                        spendtime_2 = self.is_good_schedule(t, s2_name)['min_spendtime']
                        all_spendtime = spendtime_1 + spendtime_2
                        all_spendtime_str = str(all_spendtime / 60) + ':' + str(all_spendtime % 60)
                        if all_spendtime > 2 * spendtime or all_spendtime > 50 * 60 * 24:
                            continue
                        ret_list.append({'station_name': [t], 'min_spendtime': all_spendtime,
                                         'min_spendtime_str': all_spendtime_str,
                                         "start_station": i, 'end_station': j})
                if space == 2:
                    try:
                        start = self.start_station[s1_name]
                        end = self.end_station[s2_name]
                    except Exception as ex:
                        # print 'exception:', s1_name, s2_name
                        continue
                    for station in start:
                        dis_1 = self.is_good_schedule(s1_name, station)
                        dis_1_spendtime = dis_1['min_spendtime']
                        start2 = self.start_station[station]
                        trains_name = start2 & end
                        if len(trains_name) < 1:
                            continue
                        for train in trains_name:
                            dis_2 = self.is_good_schedule(station, train)
                            dis_2_spendtime = dis_2['min_spendtime']
                            dis_3 = self.is_good_schedule(train, s2_name)
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

    def get_online_alias(self, s1, s2):
        """在线获取可能的站次别名
        """
        ret = self.get_trains_status(s1, s2)
        start_alias = set()
        end_alias = set()
        start_alias.add(s1)
        end_alias.add(s2)
        for i, info in enumerate(ret[0]):
            name_1 = info[1].replace('【', '').replace('】', '').strip()
            name_2 = info[2].replace('【', '').replace('】', '').strip()
            start_alias.add(name_1)
            end_alias.add(name_2)
        return start_alias, end_alias

    def fill_trains(self, first_ret, end_ret):
        """为了展示，填充长度不一致的数据
        """
        if len(first_ret[0]) > len(end_ret[0]):
            lens = len(first_ret[0][0])
            fill = [[' '] * lens] * int(math.fabs(len(first_ret[0]) - len(end_ret[0])))
            end_ret[0].extend(fill)
        elif len(first_ret[0]) < len(end_ret[0]):
            lens = len(end_ret[0][0])
            fill = [[' '] * lens] * int(math.fabs(len(first_ret[0]) - len(end_ret[0])))
            first_ret[0].extend(fill)

        return first_ret, end_ret

    def train_transfer_status(self, s1, s2, transfer_num=0, topk=10):
        """
        :param s1: station1 name
        :param s2: station2 name
        :param transfer_num: transfer span  0<=span<=2
        :param topk: 展示换乘时间最少的topk个站
        :return: 可换乘的topk个之间站点余票
        """
        ret = []
        if transfer_num == 0:
            ret = self.get_trains_status(s1, s2)
        elif transfer_num == 1:
            self.qiangpiao = False
            start_alias, end_alias = self.get_online_alias(s1, s2)
            ret_station_list = self.get_station2station(start_alias, end_alias, space=1, topk=topk)
            for i, en in enumerate(ret_station_list):
                start_station = en['start_station']
                end_station = en['end_station']
                station_name = en['station_name'][0]
                first_ret = self.get_trains_status(start_station, station_name)
                end_ret = self.get_trains_status(station_name, end_station)
                first_ret, end_ret = self.fill_trains(first_ret, end_ret)
                if len(first_ret[0]) == 0 or len(end_ret[0]) == 0:
                    continue
                ret.append((first_ret, end_ret))
                # break
        return ret, transfer_num


if __name__ == "__main__":
    q = QueryTecket('')
    # ret = q.get_trains_status(u'武汉', u'南京', [u'G151'], True)
    # for en in ret:
    #     for m in en:
    #         print json.dumps(m, ensure_ascii=False)
    # ret = q.get_station2station(u'德州', u'南京', space=1)
    # for i, en in enumerate(ret):
    #     print json.dumps(en, ensure_ascii=False)

    ret, transfer_num = q.train_transfer_status(u'武汉', u'南京', 1)
    # if transfer_num == 0:
    #     for i, en in enumerate(ret):
    #         for j, e in enumerate(en):
    #             print json.dumps(e, ensure_ascii=False)
    # else:
    #     for i, en in enumerate(ret[0]):
    #         if i > 0:
    #             break
    #         for j, e in enumerate(en):
    #             for k, m in enumerate(e):
    #                 print json.dumps(m, ensure_ascii=False) + '\t' + json.dumps(ret[0][1][j][k], ensure_ascii=False)
