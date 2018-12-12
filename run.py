# -*- coding=utf-8 -*-
from config.emailConf import sendEmail
from init.select_ticket_info import select


def run():
    ticket_obj = select()
    ticket_obj.main()


def Email():
    sendEmail(u"订票小助手测试一下")


if __name__ == '__main__':
    run()
    # Email()