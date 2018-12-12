# -*- coding=utf-8 -*-
import datetime
import random
import socket
import sys
import threading
import time
import wrapcache
import logging
import traceback

from agency.cdn_utils import CDNProxy
from config import urlConf
from config.TicketEnmu import ticket
from config.ticketConf import _get_yaml
from init.login import GoLogin
from inter.AutoSubmitOrderRequest import autoSubmitOrderRequest
from inter.CheckUser import checkUser
from inter.GetPassengerDTOs import getPassengerDTOs
from inter.LiftTicketInit import liftTicketInit
from inter.Query import query
from inter.GetTrainStatus import QueryTecket
from inter.SubmitOrderRequest import submitOrderRequest
from myException.PassengerUserException import PassengerUserException
from myException.UserPasswordException import UserPasswordException
from myException.ticketConfigException import ticketConfigException
from myException.ticketIsExitsException import ticketIsExitsException
from myException.ticketNumOutException import ticketNumOutException
from myUrllib.httpUtils import HTTPClient
import json
reload(sys)
sys.setdefaultencoding('utf-8')
logging.basicConfig(format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: '\
                           '%(message)s', level=logging.INFO)


class QiangPiao(object):
    """
    快速提交车票通道
    """

    def __init__(self, qiangpiao_info=None):
        if qiangpiao_info is None:
            self.from_station, self.to_station, self.station_dates, self._station_seat, self.is_more_ticket, \
            self.ticke_peoples, self.station_trains, self.ticket_black_list_time, \
            self.order_type = self.get_ticket_info()
        else:
            pass
        self.is_auto_code = _get_yaml()["is_auto_code"]
        self.auto_code_type = _get_yaml()["auto_code_type"]
        self.is_cdn = _get_yaml()["is_cdn"]
        self.httpClint = HTTPClient()
        self.urls = urlConf.urls
        self.login = GoLogin(self, self.is_auto_code, self.auto_code_type)
        self.cdn_list = []
        self.passengerTicketStrList = ""
        self.oldPassengerStr = ""
        self.station_name_map = self.station_table('../config/station_name.format')

    def get_ticket_info(self):
        """
        获取配置信息
        :return:
        """
        ticket_info_config = _get_yaml()
        from_station = ticket_info_config["set"]["from_station"].encode("utf8")
        to_station = ticket_info_config["set"]["to_station"].encode("utf8")
        station_dates = ticket_info_config["set"]["station_dates"]
        set_type = ticket_info_config["set"]["set_type"]
        is_more_ticket = ticket_info_config["set"]["is_more_ticket"]
        ticke_peoples = ticket_info_config["set"]["ticke_peoples"]
        station_trains = ticket_info_config["set"]["station_trains"]
        ticket_black_list_time = ticket_info_config["ticket_black_list_time"]
        order_type = ticket_info_config["order_type"]
        print u"*" * 20
        print u"12306刷票小助手，最后更新于2018.12.12，请勿作为商业用途!"
        print u"*" * 20
        return from_station, to_station, station_dates, set_type, is_more_ticket, ticke_peoples, station_trains, ticket_black_list_time, order_type

    def station_table(self, files):
        """
        读取车站信息
        :param station:
        :return:
        """
        # result = open(files)
        station_name = {}
        with open(files) as fp:
            for line in fp:
                if line.startswith('#') or len(line.strip()) < 2:
                    continue
                line_arr = line.strip().decode('utf8').split('\t')
                station_name[line_arr[1]] = line_arr[2]

        # info = result.read().split('=')[1].strip("'").split('@')
        # del info[0]
        # station_name = {}
        # for i in range(0, len(info)):
        #     n_info = info[i].split('|')
        #     station_name[n_info[1]] = n_info[2]
        # from_station = station_name[from_station.encode("utf8")]
        # to_station = station_name[to_station.encode("utf8")]
        return station_name

    def call_login(self, auth=False):
        """
        登录回调方法
        :return:
        """
        if auth:
            return self.login.auth()
        else:
            self.login.go_login()

    def set_cdn(self):
        """
        设置cdn
        :return:
        """
        if self.is_cdn == 1:
            while True:
                if self.cdn_list:
                    self.httpClint.cdn = self.cdn_list[random.randint(0, len(self.cdn_list) - 1)]

    def cdn_req(self, cdn):
        for i in range(len(cdn) - 1):
            http = HTTPClient()
            urls = self.urls["loginInit"]
            start_time = datetime.datetime.now()
            http.cdn = cdn[i].replace("\n", "")
            rep = http.send(urls)
            if rep and "message" not in rep and (datetime.datetime.now() - start_time).microseconds / 1000 < 500:
                print("加入cdn {0}".format(cdn[i].replace("\n", "")))
                self.cdn_list.append(cdn[i].replace("\n", ""))
        print(u"所有cdn解析完成...")

    def cdn_certification(self):
        """
        cdn 认证
        :return:
        """
        if self.is_cdn == 1:
            CDN = CDNProxy()
            all_cdn = CDN.all_cdn()
            if all_cdn:
                print(u"开启cdn查询")
                print(u"本次待筛选cdn总数为{}".format(len(all_cdn)))
                t = threading.Thread(target=self.cdn_req, args=(all_cdn,))
                t2 = threading.Thread(target=self.set_cdn, args=())
                t.start()
                t2.start()
            else:
                raise ticketConfigException(u"cdn列表为空，请先加载cdn")
        else:
            pass

    def query_train_ticket(self, from_station, to_station, station_dates, train_no=None):
        """查询车次余票
        """
        self.cdn_certification()
        l = liftTicketInit(session=self)
        l.reqLiftTicketInit()
        checkUser(self).sendCheckUser()
        num = 0
        while num < 5:
            try:
                num += 1
                # checkUser(self).sendCheckUser()
                q = QueryTecket(session=self, station_dates=station_dates)
                # queryResult = q.sendQuery(from_station, to_station, train_no)
                queryResult = q.get_trains_status(from_station, to_station, train_no, True)
                # if len(queryResult) == 1:
                #     continue
                col_name = [u'车次', u'发站', u'到站', u'发车', u'到达', u'耗时', u'出发日期', u'无座', u'硬座', u'硬卧', u'软卧', u'高软', u'二等',
                            u'一等', u'商务', u'动卧']
                print json.dumps(col_name, ensure_ascii=False)
                for ret in queryResult:
                    for en in ret:
                        print json.dumps(en, ensure_ascii=False)

                return queryResult
            except Exception as ex:
                logging.error(traceback.format_exc())

    def init_login(self):
        self.cdn_certification()
        l = liftTicketInit(session=self)
        l.reqLiftTicketInit()
        self.call_login()
        checkUser(self).sendCheckUser()

    def go_qiangpiao(self, tricket_info, log_info = [], num = 1):
        try:
            from_station_h = tricket_info['from_station']
            to_station_h = tricket_info['to_station']
            from_station, to_station = self.station_name_map[from_station_h], self.station_name_map[to_station_h]
        except:
            return log_info.append(u'站点输入有误，请检查！')
        try:
            checkUser(self).sendCheckUser()
            now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
            while now_time > "23:00:00" or now_time < "06:00:00":
                time.sleep(5)
                now_time = time.strftime('%H:%M:%S', time.localtime(time.time()))
                if "06:00:00" < now_time < "23:00:00":
                    log_info.append(ticket.REST_TIME_PAST)
                    print(ticket.REST_TIME_PAST)
                    self.call_login()
                    break

            start_time = datetime.datetime.now()
            q = query(session=self,
                      from_station=from_station,
                      to_station=to_station,
                      from_station_h=from_station_h,
                      to_station_h=to_station_h,
                      _station_seat=tricket_info['seat'],
                      station_trains=tricket_info['trains'],
                      station_dates=tricket_info['date'])

            queryResult = q.sendQuery(log_info)
            # 查询接口
            # tmp = queryResult.get("status", False)
            # assert tmp == False
            if queryResult.get("status", False):
                train_no = queryResult.get("train_no", "")
                train_date = queryResult.get("train_date", "")
                stationTrainCode = queryResult.get("stationTrainCode", "")
                set_type = queryResult.get("set_type", "")
                secretStr = queryResult.get("secretStr", "")
                leftTicket = queryResult.get("leftTicket", "")
                query_from_station_name = queryResult.get("query_from_station_name", "")
                query_to_station_name = queryResult.get("query_to_station_name", "")
                if wrapcache.get(train_no):
                    print(ticket.QUEUE_WARNING_MSG.format(train_no))
                    log_info.append(ticket.QUEUE_WARNING_MSG.format(train_no))
                else:
                    # 获取联系人
                    if not self.passengerTicketStrList and not self.oldPassengerStr:
                        s = getPassengerDTOs(session=self, ticket_peoples=tricket_info['person_name'], set_type=set_type)
                        #
                        getPassengerDTOsResult = s.getPassengerTicketStrListAndOldPassengerStr()
                        if getPassengerDTOsResult.get("status", False):
                            self.passengerTicketStrList = getPassengerDTOsResult.get("passengerTicketStrList", "")
                            self.oldPassengerStr = getPassengerDTOsResult.get("oldPassengerStr", "")
                            set_type = getPassengerDTOsResult.get("set_type", "")
                    self.order_type = 2
                    # 提交订单
                    if self.order_type == 1:  # 快读下单
                        a = autoSubmitOrderRequest(session=self,
                                                   secretStr=secretStr,
                                                   train_date=train_date,
                                                   passengerTicketStr=self.passengerTicketStrList,
                                                   oldPassengerStr=self.oldPassengerStr,
                                                   train_no=train_no,
                                                   stationTrainCode=stationTrainCode,
                                                   leftTicket=leftTicket,
                                                   set_type=set_type,
                                                   query_from_station_name=query_from_station_name,
                                                   query_to_station_name=query_to_station_name,
                                                   )
                        a.sendAutoSubmitOrderRequest(log_info)
                    elif self.order_type == 2:  # 普通下单
                        sor = submitOrderRequest(self, secretStr,
                                                 from_station,
                                                 to_station,
                                                 train_no,
                                                 set_type,
                                                 self.passengerTicketStrList,
                                                 self.oldPassengerStr,
                                                 train_date,
                                                 self.ticke_peoples)
                        sor.sendSubmitOrderRequest(log_info)
            else:
                random_time = round(random.uniform(1, 4), 2)
                time.sleep(random_time)
                mess = u"正在第{0}次查询 随机停留时长：{6}s 乘车日期: {1} 车次：{2} 查询无票 cdn轮询IP：{4}当前cdn总数：{5} 总耗时：{3}ms".format(num,
                                                                                                            ",".join(
                                                                                                                tricket_info[
                                                                                                                    'date']),
                                                                                                            tricket_info['trains'],
                                                                                                            (datetime.datetime.now() - start_time).microseconds / 1000,
                                                                                                            self.httpClint.cdn,
                                                                                                            len(self.cdn_list),
                                                                                                             random_time)
                print mess
                log_info.append(mess)
        except PassengerUserException as e:
            print e.message
            log_info.append(e.message)
            # break
        except ticketConfigException as e:
            print e.message
            log_info.append(e.message)
            # break
        except ticketIsExitsException as e:
            print e.message
            log_info.append(e.message)
            # break
        except ticketNumOutException as e:
            print e.message
            log_info.append(e.message)
            # break
        except UserPasswordException as e:
            print e.message
            log_info.append(e.message)
            # break
        except ValueError as e:
            if e.message == "No JSON object could be decoded":
                print(u"12306接口无响应，正在重试")
                log_info.append(u"12306接口无响应，正在重试")
            else:
                print(e.message)
                log_info.append(e.message)
        except KeyError as e:
            print(e.message)
            log_info.append(e.message)
        except TypeError as e:
            print(u"12306接口无响应，正在重试 {0}".format(e.message))
            log_info.append(u"12306接口无响应，正在重试 {0}".format(e.message))
        except socket.error as e:
            print e
            log_info.append(e.message)


    def main(self):
        from_station, to_station = self.station_table(self.from_station, self.to_station)
        num = 0
        while 1:
            try:
                num += 1
                checkUser(self).sendCheckUser()
                if time.strftime('%H:%M:%S', time.localtime(time.time())) > "23:00:00" or time.strftime('%H:%M:%S',
                                                                                                        time.localtime(
                                                                                                            time.time())) < "06:00:00":
                    print(ticket.REST_TIME)
                    # while 1:
                    #     time.sleep(1)
                    #     if "06:00:00" < time.strftime('%H:%M:%S', time.localtime(time.time())) < "23:00:00":
                    #         print(ticket.REST_TIME_PAST)
                    #         self.call_login()
                    #         break
                start_time = datetime.datetime.now()

                q = query(session=self,
                          from_station=from_station,
                          to_station=to_station,
                          from_station_h=self.from_station,
                          to_station_h=self.to_station,
                          _station_seat=self._station_seat,
                          station_trains=self.station_trains,
                          station_dates=self.station_dates, )
                queryResult = q.sendQuery()
                # 查询接口
                # tmp = queryResult.get("status", False)
                # assert tmp == False
                if queryResult.get("status", False):
                    train_no = queryResult.get("train_no", "")
                    train_date = queryResult.get("train_date", "")
                    stationTrainCode = queryResult.get("stationTrainCode", "")
                    set_type = queryResult.get("set_type", "")
                    secretStr = queryResult.get("secretStr", "")
                    leftTicket = queryResult.get("leftTicket", "")
                    query_from_station_name = queryResult.get("query_from_station_name", "")
                    query_to_station_name = queryResult.get("query_to_station_name", "")
                    if wrapcache.get(train_no):
                        print(ticket.QUEUE_WARNING_MSG.format(train_no))
                    else:
                        # 获取联系人
                        if not self.passengerTicketStrList and not self.oldPassengerStr:
                            s = getPassengerDTOs(session=self, ticket_peoples=self.ticke_peoples, set_type=set_type)
                            #
                            getPassengerDTOsResult = s.getPassengerTicketStrListAndOldPassengerStr()
                            if getPassengerDTOsResult.get("status", False):
                                self.passengerTicketStrList = getPassengerDTOsResult.get("passengerTicketStrList", "")
                                self.oldPassengerStr = getPassengerDTOsResult.get("oldPassengerStr", "")
                                set_type = getPassengerDTOsResult.get("set_type", "")
                        # 提交订单
                        if self.order_type == 1:  # 快读下单
                            a = autoSubmitOrderRequest(session=self,
                                                       secretStr=secretStr,
                                                       train_date=train_date,
                                                       passengerTicketStr=self.passengerTicketStrList,
                                                       oldPassengerStr=self.oldPassengerStr,
                                                       train_no=train_no,
                                                       stationTrainCode=stationTrainCode,
                                                       leftTicket=leftTicket,
                                                       set_type=set_type,
                                                       query_from_station_name=query_from_station_name,
                                                       query_to_station_name=query_to_station_name,
                                                       )
                            a.sendAutoSubmitOrderRequest()
                        elif self.order_type == 2:  # 普通下单
                            sor = submitOrderRequest(self, secretStr, from_station, to_station, train_no, set_type,
                                                     self.passengerTicketStrList, self.oldPassengerStr, train_date,
                                                     self.ticke_peoples)
                            sor.sendSubmitOrderRequest()


                else:
                    random_time = round(random.uniform(1, 4), 2)
                    time.sleep(random_time)
                    print u"正在第{0}次查询 随机停留时长：{6}s 乘车日期: {1} 车次：{2} 查询无票 cdn轮询IP：{4}当前cdn总数：{5} 总耗时：{3}ms".format(num,
                                                                                                                ",".join(
                                                                                                                    self.station_dates),
                                                                                                                ",".join(
                                                                                                                    self.station_trains),
                                                                                                                (datetime.datetime.now() - start_time).microseconds / 1000,
                                                                                                                self.httpClint.cdn,
                                                                                                                len(self.cdn_list),
                                                                                                                random_time)
            except PassengerUserException as e:
                print e.message
                break
            except ticketConfigException as e:
                print e.message
                break
            except ticketIsExitsException as e:
                print e.message
                break
            except ticketNumOutException as e:
                print e.message
                break
            except UserPasswordException as e:
                print e.message
                break
            except ValueError as e:
                if e.message == "No JSON object could be decoded":
                    print(u"12306接口无响应，正在重试")
                else:
                    print(e.message)
            except KeyError as e:
                print(e.message)
            except TypeError as e:
                print(u"12306接口无响应，正在重试 {0}".format(e.message))
            except socket.error as e:
                print(e.message)


if __name__ == '__main__':
    ticket_obj = QiangPiao()
    ticket_obj.init_login()
    login = GoLogin(ticket_obj, False)
    login.go_login_v2()
    tricket_info = {}
    tricket_info['from_station'] = u'北京'
    tricket_info['to_station'] = u'南京'
    tricket_info['date'] = ['2018-12-28']
    tricket_info['trains'] = u'G101'
    tricket_info['seat'] = [u'二等座']
    tricket_info['person_name'] = [u'卞东海']
    # date_str = ['2018-11-28']
    ticket_obj.go_qiangpiao(tricket_info)
    # ticket_obj.main()
    # ticket_obj.query_train_ticket(from_station, to_station, date_str)
