# coding=utf-8
from config.urlConf import urls
from myUrllib.httpUtils import HTTPClient

httpClint = HTTPClient()

def getPassCodeNewOrderAndLogin(session, imgType):
    """
    下载验证码
    :param session:
    :param imgType: 下载验证码类型，login=登录验证码，其余为订单验证码
    :return:
    """
    if imgType == "login":
        codeImgUrl = urls["getCodeImg"]
        print codeImgUrl
        # codeImgUrl = session.urls["getCodeImg"]
    else:
        # codeImgUrl = session.urls["codeImgByOrder"]
        codeImgUrl = urls["codeImgByOrder"]
    print (u"下载验证码...")
    img_path = '../flask_app/static/images/login/tkcode.png'
    # result = session.httpClint.send(codeImgUrl)
    print codeImgUrl
    result = session.httpClint.send(codeImgUrl)
    try:
        print(u"下载验证码成功")
        open(img_path, 'wb').write(result)
    except OSError:
        print (u"验证码下载失败，可能ip被封，确认请手动请求: {0}".format(codeImgUrl))
