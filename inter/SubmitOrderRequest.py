# coding=utf-8
import datetime
import urllib

from inter.CheckOrderInfo import checkOrderInfo
from myException.ticketIsExitsException import ticketIsExitsException


def time():
    """
    获取日期
    :return:
    """
    today = datetime.date.today()
    return today.strftime('%Y-%m-%d')


class submitOrderRequest:
    def __init__(self, session, secretStr, from_station, to_station, train_no, set_type,
                 passengerTicketStrList, oldPassengerStr, train_date, ticke_peoples):
        self.session = session
        self.secretStr = secretStr
        self.from_station = from_station
        self.to_station = to_station
        self.to_station = to_station
        self.train_no = train_no
        self.set_type = set_type
        self.passengerTicketStrList = passengerTicketStrList
        self.oldPassengerStr = oldPassengerStr
        self.train_date = train_date
        self.ticke_peoples = ticke_peoples

    def data_apr(self):
        """
        :return:
        """
        data = [('secretStr', urllib.unquote(self.secretStr)),  # 字符串加密
                ('train_date', self.train_date),  # 出发时间
                ('back_train_date', time()),  # 返程时间
                ('tour_flag', 'dc'),  # 旅途类型
                ('purpose_codes', 'ADULT'),  # 成人票还是学生票
                ('query_from_station_name', self.from_station),  # 起始车站
                ('query_to_station_name', self.to_station),  # 终点车站
                ]
        return data

    def sendSubmitOrderRequest(self, log_info=[]):
        """
        提交车次
        预定的请求参数，注意参数顺序
        注意这里为了防止secretStr被urllib.parse过度编码，在这里进行一次解码
        否则调用HttpTester类的post方法将会将secretStr编码成为无效码,造成提交预定请求失败
        :param self:
        :param secretStr: 提交车次加密
        :return:
        """
        submit_station_url = self.session.urls["submit_station_url"]
        submitResult = self.session.httpClint.send(submit_station_url, self.data_apr())
        if 'data' in submitResult and submitResult['data']:
            if submitResult['data'] == 'N':
                print (u'出票成功')
                log_info.append(u'出票成功')
                coi = checkOrderInfo(self.session, self.train_no, self.set_type, self.passengerTicketStrList,
                                     self.oldPassengerStr,
                                     self.train_date, self.ticke_peoples)
                coi.sendCheckOrderInfo(log_info)
            else:
                print (u'出票失败')
                log_info.append(u'出票失败')
        elif 'messages' in submitResult and submitResult['messages']:
            raise ticketIsExitsException(submitResult['messages'][0])
