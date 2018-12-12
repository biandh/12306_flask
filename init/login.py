# -*- coding=utf-8 -*-
from time import sleep
from config.urlConf import urls
from config.ticketConf import _get_yaml
from damatuCode.damatuWeb import DamatuApi
from inter.GetPassCodeNewOrderAndLogin import getPassCodeNewOrderAndLogin
from inter.GetRandCode import getRandCode
from myException.UserPasswordException import UserPasswordException
from myException.balanceException import balanceException
from myUrllib import myurllib2
from myUrllib.httpUtils import HTTPClient
# httpClint = HTTPClient()

class GoLogin:
    def __init__(self, session=None, is_auto_code=False, auto_code_type=1):
        if session is None:
            self.session = self
        else:
            self.session = session
        self.randCode = ""
        self.is_auto_code = is_auto_code
        self.auto_code_type = auto_code_type
        self.urls = urls
        self.httpClint = HTTPClient()

    def auth(self):
        """认证"""
        authUrl = urls["auth"]
        authData = {"appid": "otn"}
        tk = self.session.httpClint.send(authUrl, authData)
        return tk

    def get_code(self):
        "获取验证码"
        getPassCodeNewOrderAndLogin(session=self.session, imgType="login")

    def codeCheck(self):
        """
        验证码校验
        :return:
        """
        codeCheck = urls["codeCheck"]
        codeCheckData = {
            "answer": self.randCode,
            "rand": "sjrand",
            "login_site": "E"
        }
        fresult = self.session.httpClint.send(codeCheck, codeCheckData)
        if "result_code" in fresult and fresult["result_code"] == "4":
            print (u"验证码通过,开始登录..")
            return True, ''
        else:
            if "result_message" in fresult:
                print(fresult["result_message"])
            sleep(1)
            self.session.httpClint.del_cookies()
            return False, fresult["result_message"]

    def baseLogin(self, user, passwd):
        """
        登录过程
        :param user:
        :param passwd:
        :return: 权限校验码
        """
        logurl = self.session.urls["login"]
        logData = {
            "username": user,
            "password": passwd,
            "appid": "otn"
        }
        tresult = self.session.httpClint.send(logurl, logData)

        if 'result_code' in tresult and tresult["result_code"] == 0:
            print (u"登录成功")
            tk = self.auth()
            if "newapptk" in tk and tk["newapptk"]:
                return tk["newapptk"], u'登录成功！'
            else:
                return False, u'登录失败！'
        elif 'result_message' in tresult and tresult['result_message']:
            messages = tresult['result_message']
            return False, messages
                # raise UserPasswordException("{0}".format(messages))
        else:
            return False, u'登录失败, 请稍后重试！'

    def getUserName(self, uamtk):
        """
        登录成功后,显示用户名
        :return:
        """
        if not uamtk:
            return u"权限校验码不能为空"
        else:
            uamauthclientUrl = self.session.urls["uamauthclient"]
            data = {"tk": uamtk}
            uamauthclientResult = self.session.httpClint.send(uamauthclientUrl, data)
            if uamauthclientResult:
                if "result_code" in uamauthclientResult and uamauthclientResult["result_code"] == 0:
                    print(u"欢迎 {} 登录".format(uamauthclientResult["username"]))
                    return True, uamauthclientResult["username"]
                else:
                    return False, ''
            else:
                self.session.httpClint.send(uamauthclientUrl, data)
                url = self.session.urls["getUserInfo"]
                self.session.httpClint.send(url)
                return True, 'default'

    def go_login(self):
        """
        登陆
        :param user: 账户名
        :param passwd: 密码
        :return:
        """
        if self.is_auto_code and self.auto_code_type == 1:
            balance = DamatuApi(_get_yaml()["auto_code_account"]["user"], _get_yaml()["auto_code_account"]["pwd"]).getBalance()
            if int(balance) < 40:
                raise balanceException(u'余额不足，当前余额为: {}'.format(balance))
        user, passwd = _get_yaml()["set"]["12306account"][0]["user"], _get_yaml()["set"]["12306account"][1]["pwd"]
        if not user or not passwd:
            raise UserPasswordException(u"温馨提示: 用户名或者密码为空，请仔细检查")
        login_num = 0
        while True:
            getPassCodeNewOrderAndLogin(session=self.session, imgType="login")
            self.randCode = getRandCode(self.is_auto_code, self.auto_code_type)
            login_num += 1
            self.auth()
            if self.codeCheck()[0]:
                uamtk, _ = self.baseLogin(user, passwd)
                if uamtk:
                    self.getUserName(uamtk)
                    break

    def go_login_v2(self, user, passwd, rand_code=None):
        if self.is_auto_code and self.auto_code_type == 1:
            balance = DamatuApi(_get_yaml()["auto_code_account"]["user"], _get_yaml()["auto_code_account"]["pwd"]).getBalance()
            if int(balance) < 40:
                raise balanceException(u'余额不足，当前余额为: {}'.format(balance))
        if not user or not passwd:
            raise UserPasswordException(u"温馨提示: 用户名或者密码为空，请仔细检查")
        login_num = 0

        if rand_code is None:
            self.randCode = getRandCode(self.is_auto_code, self.auto_code_type)
        else:
            self.randCode = rand_code
        login_num += 1
        self.auth()
        status, mess = self.codeCheck()
        if status:
            uamtk, mess = self.baseLogin(user, passwd)
            if uamtk:
                st, name = self.getUserName(uamtk)
            return mess, name
        else:
            return mess, ''

    def logout(self):
        url = 'https://kyfw.12306.cn/otn/login/loginOut'
        result = myurllib2.get(url)
        if result:
            print (u"已退出")
        else:
            print (u"退出失败")


if __name__ == "__main__":
    user = GoLogin(None, False, 1)
    # res = user.auth()
    user.get_code()
    user.go_login_v2('b624345050', '530530')