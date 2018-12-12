# coding=utf-8
import datetime
import wrapcache
import time

from config.TicketEnmu import ticket


class checkUser:
    def __init__(self, session):
        self.session = session

    def sendCheckUser(self):
        """
        检查用户登录, 检查间隔为五分钟
        :return:
        """
        if wrapcache.get("user_time") is None:
            check_user_url = self.session.urls["check_user_url"]
            data = {"_json_att": ""}
            check_user = self.session.httpClint.send(check_user_url, data)
            if check_user.get("data", False):
                check_user_flag = check_user["data"]["flag"]
                if check_user_flag is True:
                    wrapcache.set("user_time", datetime.datetime.now(), timeout=60 * 5)
                else:
                    if check_user['messages']:
                        print (ticket.LOGIN_SESSION_FAIL.format(check_user['messages']))
                        self.session.call_login()
                        wrapcache.set("user_time", datetime.datetime.now(), timeout=60 * 5)
                    else:
                        print (ticket.LOGIN_SESSION_FAIL.format(check_user['messages']))
                        self.session.call_login()
                        wrapcache.set("user_time", datetime.datetime.now(), timeout=60 * 5)

    def user_is_connecting(self):
        """
        检查用户登录, 检查间隔为五分钟
        :return:
        """
        check_user_url = self.session.urls["check_user_url"]
        data = {"_json_att": ""}
        if wrapcache.get("user_time") is None:
            check_user = self.session.httpClint.send(check_user_url, data)
            if check_user.get("data", False):
                check_user_flag = check_user["data"]["flag"]
                if check_user_flag is True:
                    wrapcache.set("user_time", datetime.datetime.now(), timeout=60 * 5)
                    return True
                else:
                    if check_user['messages']:
                        print (ticket.LOGIN_SESSION_FAIL.format(check_user['messages']))
                    else:
                        print (ticket.LOGIN_SESSION_FAIL.format(check_user['messages']))
            return False
        else:
            return True

    def set_timeout(self):
        """设置超时
        """
        wrapcache.set("user_time", datetime.datetime.now(), timeout=60 * 5)