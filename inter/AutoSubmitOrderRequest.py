# coding=utf-8
import urllib
from collections import OrderedDict

from config.TicketEnmu import ticket
from config.ticketConf import _get_yaml
from inter.CheckRandCodeAnsyn import checkRandCodeAnsyn
from inter.GetQueueCountAsync import getQueueCountAsync
from inter.GetRandCode import getRandCode


class autoSubmitOrderRequest:
    """
    快读提交订单通道
    """
    def __init__(self, session,
                 secretStr,
                 train_date,
                 query_from_station_name,
                 query_to_station_name,
                 passengerTicketStr,
                 oldPassengerStr,
                 train_no,
                 stationTrainCode,
                 leftTicket,
                 set_type,):
        self.secretStr = urllib.unquote(secretStr)
        self.train_date = train_date
        self.query_from_station_name = query_from_station_name
        self.query_to_station_name = query_to_station_name
        self.passengerTicketStr = passengerTicketStr
        self.oldPassengerStr = oldPassengerStr
        self.session = session
        self.train_no = train_no
        self.stationTrainCode = stationTrainCode
        self.leftTicket = leftTicket
        self.set_type = set_type

    def data_par(self):
        """
        参数结构
        自动提交代码接口-autoSubmitOrderRequest
            - 字段说明
                - secretStr 车票代码
                - train_date 乘车日期
                - tour_flag 乘车类型
                - purpose_codes 学生还是成人
                - query_from_station_name 起始车站
                - query_to_station_name 结束车站
                - cancel_flag 默认2，我也不知道干嘛的
                - bed_level_order_num  000000000000000000000000000000
                - passengerTicketStr   乘客乘车代码
                - oldPassengerStr  乘客编号代码
        :return:
        """
        data = OrderedDict()
        data["secretStr"] = self.secretStr
        data["train_date"] = self.train_date
        data["tour_flag"] = "dc"
        data["purpose_codes"] = "ADULT"
        data["query_from_station_name"] = self.query_from_station_name
        data["query_to_station_name"] = self.query_to_station_name
        data["cancel_flag"] = 2
        data["bed_level_order_num"] = "000000000000000000000000000000"
        data["passengerTicketStr"] = self.passengerTicketStr
        data["oldPassengerStr"] = self.oldPassengerStr
        return data

    def sendAutoSubmitOrderRequest(self, log_info=[]):
        """
        请求下单接口
        :return:
        """
        urls = self.session.urls["autoSubmitOrderRequest"]
        data = self.data_par()
        autoSubmitOrderRequestResult = self.session.httpClint.send(urls, data)
        if autoSubmitOrderRequestResult and \
                autoSubmitOrderRequestResult.get("status", False) and\
                autoSubmitOrderRequestResult.get("httpstatus", False) == 200:
            requestResultData = autoSubmitOrderRequestResult.get("data", {})
            if requestResultData:
                result = requestResultData.get("result", "")
                ifShowPassCode = requestResultData.get("ifShowPassCode", "N")
                ifShowPassCodeTime = int(requestResultData.get("ifShowPassCodeTime", "1000")) / float(1000)
                print(ticket.AUTO_SUBMIT_ORDER_REQUEST_C)
                log_info.append(ticket.AUTO_SUBMIT_ORDER_REQUEST_C)
                g = getQueueCountAsync(session=self.session,
                                       train_no=self.train_no,
                                       stationTrainCode=self.stationTrainCode,
                                       fromStationTelecode=self.query_from_station_name,
                                       toStationTelecode=self.query_to_station_name,
                                       leftTicket=self.leftTicket,
                                       set_type=self.set_type,
                                       users=len(self.session.ticke_peoples),
                                       station_dates=self.train_date,
                                       passengerTicketStr=self.passengerTicketStr,
                                       oldPassengerStr=self.oldPassengerStr,
                                       result=result,
                                       ifShowPassCodeTime=ifShowPassCodeTime,
                                       )
                # g.sendGetQueueCountAsync()
                if ifShowPassCode == "Y":  # 如果需要验证码
                    print(u"需要验证码")
                    print(u"正在使用自动识别验证码功能")
                    log_info.append(u"需要验证码")
                    log_info.append(u"正在使用自动识别验证码功能")
                    for i in range(3):
                        randCode = getRandCode(is_auto_code=True, auto_code_type=_get_yaml()["auto_code_type"])
                        checkcode = checkRandCodeAnsyn(self.session, randCode, "")
                        if checkcode == 'TRUE':
                            print(u"验证码通过,正在提交订单")
                            log_info.append(u"验证码通过,正在提交订单")
                            data['randCode'] = randCode
                            g.sendGetQueueCountAsync(log_info)
                            return
                        else:
                            log_info.append(u"验证码有误, {0}次尝试重试".format(i + 1))
                            print (u"验证码有误, {0}次尝试重试".format(i + 1))
                    print(u"验证码超过限定次数3次，放弃此次订票机会!")
                    log_info.append(u"验证码超过限定次数3次，放弃此次订票机会!")
                else:
                    print(u"不需要验证码")
                    log_info.append(u"不需要验证码, 正在提交订单")
                    g.sendGetQueueCountAsync(log_info)
        else:
            print(ticket.AUTO_SUBMIT_ORDER_REQUEST_F)
            log_info.append(ticket.AUTO_SUBMIT_ORDER_REQUEST_F)
            if autoSubmitOrderRequestResult.get("messages", ""):
                print(autoSubmitOrderRequestResult.get("messages", ""))
                log_info.append(autoSubmitOrderRequestResult.get("messages", ""))
            elif autoSubmitOrderRequestResult.get("validateMessages", ""):
                print(autoSubmitOrderRequestResult.get("validateMessages", ""))
                log_info.append(autoSubmitOrderRequestResult.get("validateMessages", ""))


