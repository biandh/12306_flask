# coding=utf-8
from collections import OrderedDict
from inter.GetQueueCount import getQueueCount
from inter.GetRepeatSubmitToken import getRepeatSubmitToken


class checkOrderInfo:

    def __init__(self, session, train_no, set_type, passengerTicketStrList, oldPassengerStr, station_dates, ticket_peoples):
        self.train_no = train_no
        self.set_type = set_type
        self.passengerTicketStrList = passengerTicketStrList
        self.oldPassengerStr = oldPassengerStr
        self.station_dates = station_dates
        self.ticket_peoples = ticket_peoples
        self.RepeatSubmitToken = getRepeatSubmitToken(session)
        self.getTicketInfoForPassengerForm = self.RepeatSubmitToken.sendGetRepeatSubmitToken()
        self.ticketInfoForPassengerForm = self.getTicketInfoForPassengerForm.get("ticketInfoForPassengerForm", "")
        self.token = self.getTicketInfoForPassengerForm.get("token", "")
        self.session = self.getTicketInfoForPassengerForm.get("session", "")

    def data_par(self):
        """
        参数结构
        :return:
        """
        data = OrderedDict()
        data['passengerTicketStr'] = self.passengerTicketStrList.rstrip("_{0}".format(self.set_type))
        data['oldPassengerStr'] = self.oldPassengerStr
        data['REPEAT_SUBMIT_TOKEN'] = self.token
        data['randCode'] = ""
        data['cancel_flag'] = 2
        data['bed_level_order_num'] = "000000000000000000000000000000"
        data['tour_flag'] = 'dc'
        data['_json_att'] = ""
        return data

    def sendCheckOrderInfo(self, log_info = []):
        """
        检查支付订单，需要提交REPEAT_SUBMIT_TOKEN
        passengerTicketStr : 座位编号,0,票类型,乘客名,证件类型,证件号,手机号码,保存常用联系人(Y或N)
        oldPassengersStr: 乘客名,证件类型,证件号,乘客类型
        :return:
        """
        CheckOrderInfoUrls = self.session.urls["checkOrderInfoUrl"]
        data = self.data_par()
        checkOrderInfoRep = self.session.httpClint.send(CheckOrderInfoUrls, data)
        if 'data' in checkOrderInfoRep:
            print (u'车票提交通过，正在尝试排队')
            log_info.append(u'车票提交通过，正在尝试排队')
            ifShowPassCodeTime = int(checkOrderInfoRep["data"]["ifShowPassCodeTime"]) / float(1000)
            if "ifShowPassCode" in checkOrderInfoRep["data"] and checkOrderInfoRep["data"]["ifShowPassCode"] == "Y":
                is_need_code = True
            elif "ifShowPassCode" in checkOrderInfoRep["data"] and checkOrderInfoRep['data']['submitStatus'] is True:
                is_need_code = False
            else:
                is_need_code = False
            QueueCount = getQueueCount(self.session,
                                       is_need_code,
                                       ifShowPassCodeTime,
                                       self.set_type,
                                       self.station_dates,
                                       self.train_no,
                                       self.ticket_peoples,
                                       self.ticketInfoForPassengerForm,
                                       self.token,
                                       self.oldPassengerStr,
                                       self.passengerTicketStrList,
                                       )
            QueueCount.sendGetQueueCount(log_info)
        elif "errMsg" in checkOrderInfoRep['data'] and checkOrderInfoRep['data']["errMsg"]:
            print checkOrderInfoRep['data']["errMsg"]
            log_info.append(checkOrderInfoRep['data']["errMsg"])
        elif 'messages' in checkOrderInfoRep and checkOrderInfoRep['messages']:
            log_info.append(checkOrderInfoRep['messages'][0])
            print (checkOrderInfoRep['messages'][0])