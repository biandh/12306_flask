# coding=utf-8
import datetime
import time
from collections import OrderedDict

import wrapcache

from config.TicketEnmu import ticket
from config.ticketConf import _get_yaml
from inter.ConfirmSingleForQueueAsys import confirmSingleForQueueAsys


class getQueueCountAsync:
    """
    排队
    """
    def __init__(self,
                 session,
                 train_no,
                 stationTrainCode,
                 fromStationTelecode,
                 toStationTelecode,
                 leftTicket,
                 set_type,
                 users,
                 station_dates,
                 passengerTicketStr,
                 oldPassengerStr,
                 result,
                 ifShowPassCodeTime):
        self.train_no = train_no
        self.session = session
        self.stationTrainCode = stationTrainCode
        self.fromStationTelecode = fromStationTelecode
        self.toStationTelecode = toStationTelecode
        self.set_type = set_type
        self.leftTicket = leftTicket
        self.users = users
        self.station_dates = station_dates
        self.passengerTicketStr = passengerTicketStr
        self.oldPassengerStr = oldPassengerStr
        self.result = result
        self.ifShowPassCodeTime=ifShowPassCodeTime

    def data_par(self):
        """
         - 字段说明
            - train_date 时间
            - train_no 列车编号,查询代码里面返回
            - stationTrainCode 列车编号
            - seatType 对应坐席
            - fromStationTelecode 起始城市
            - toStationTelecode 到达城市
            - leftTicket 查询代码里面返回
            - purpose_codes 学生还是成人
            - _json_att 没啥卵用，还是带上吧
        :return:
        """
        new_train_date = filter(None, str(time.asctime(time.strptime(self.station_dates, "%Y-%m-%d"))).split(" "))
        data = OrderedDict()
        data['train_date'] = "{0} {1} {2} {3} 00:00:00 GMT+0800 (中国标准时间)".format(
            new_train_date[0],
            new_train_date[1],
            new_train_date[2],
            new_train_date[4],
            time.strftime("%H:%M:%S", time.localtime(time.time()))
        ),
        data["train_no"] = self.train_no
        data["stationTrainCode"] = self.stationTrainCode
        data["seatType"] = self.set_type
        data["fromStationTelecode"] = self.fromStationTelecode
        data["toStationTelecode"] = self.toStationTelecode
        data["leftTicket"] = self.leftTicket
        data["purpose_codes"] = "ADULT"
        data["_json_att"] = ""
        return data

    def conversion_int(self, str):
        return int(str)

    def sendGetQueueCountAsync(self, log_info=[]):
        """
        请求排队接口
        :return:
        """
        urls = self.session.urls["getQueueCountAsync"]
        data = self.data_par()
        getQueueCountAsyncResult = self.session.httpClint.send(urls, data)
        if getQueueCountAsyncResult.get("status", False) and getQueueCountAsyncResult.get("data", False):
            if "status" in getQueueCountAsyncResult and getQueueCountAsyncResult["status"] is True:
                if "countT" in getQueueCountAsyncResult["data"]:
                    ticket_data = getQueueCountAsyncResult["data"]["ticket"]
                    ticket_split = sum(map(self.conversion_int, ticket_data.split(","))) if ticket_data.find(
                        ",") != -1 else ticket_data
                    countT = getQueueCountAsyncResult["data"]["countT"]
                    if int(countT) is 0:
                        if int(ticket_split) < self.users:
                            log_info.append(u"当前余票数小于乘车人数，放弃订票")
                            print(u"当前余票数小于乘车人数，放弃订票")
                        else:
                            log_info.append(u"排队成功, 当前余票还剩余: {0} 张".format(ticket_split))
                            print(u"排队成功, 当前余票还剩余: {0} 张".format(ticket_split))
                            c = confirmSingleForQueueAsys(session=self.session,
                                                          passengerTicketStr=self.passengerTicketStr,
                                                          oldPassengerStr=self.oldPassengerStr,
                                                          result=self.result,)
                            print(u"验证码提交安全期，等待{}MS".format(self.ifShowPassCodeTime))
                            log_info.append(u"验证码提交安全期，等待{}MS".format(self.ifShowPassCodeTime))
                            time.sleep(self.ifShowPassCodeTime)
                            c.sendConfirmSingleForQueueAsys()
                else:
                    log_info.append(u"排队发现未知错误{0}，将此列车 {1}加入小黑屋".format(getQueueCountAsyncResult, self.train_no))
                    print(u"排队发现未知错误{0}，将此列车 {1}加入小黑屋".format(getQueueCountAsyncResult, self.train_no))
                    # wrapcache.set(key=self.train_no, value=datetime.datetime.now(),
                    #               timeout=int(_get_yaml()["ticket_black_list_time"]) * 60)
            elif "messages" in getQueueCountAsyncResult and getQueueCountAsyncResult["messages"]:
                log_info.append(u"排队异常，错误信息：{0}, 将此列车 {1}加入小黑屋".format(getQueueCountAsyncResult["messages"][0], self.train_no))
                print(u"排队异常，错误信息：{0}, 将此列车 {1}加入小黑屋".format(getQueueCountAsyncResult["messages"][0], self.train_no))
                wrapcache.set(key=self.train_no, value=datetime.datetime.now(),
                              timeout=int(_get_yaml()["ticket_black_list_time"]) * 60)
            else:
                if "validateMessages" in getQueueCountAsyncResult and getQueueCountAsyncResult["validateMessages"]:
                    log_info.append(str(getQueueCountAsyncResult["validateMessages"]))
                    print(str(getQueueCountAsyncResult["validateMessages"]))



