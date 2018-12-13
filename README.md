# 12306_flask
基于flask框架的12306抢票程序，本程序后台抢票功能参考了https://github.com/testerSunshine/12306

此外增加了多种查询功能

功能：
   1. 火车票查询，包括：

      1.1 常规站-站查询

       <img src="https://github.com/biandh/12306_flask/raw/master/flask_app/downloads/1.jpg" width="300" height="120"/>
       <br/>
       <img src="https://github.com/biandh/12306_flask/raw/master/flask_app/downloads/2.jpg" width="300" height="150"/>


      1.2 某个车次越站乘车查询

      <img src="https://github.com/biandh/12306_flask/raw/master/flask_app/downloads/3.jpg" width="300" height="150"/>

      1.3 换乘查询(目前只支持1次换乘)

      <img src="https://github.com/biandh/12306_flask/raw/master/flask_app/downloads/6.jpg" width="300" height="100"/>
      <br/>
      注意：越站和换乘只能选择一个，越站需要输入越站 车次，换乘填 1 即代表换乘一次

   2. 火车票购票

      后台抢票程序与上面参考地址相同，但修复了12306更新后不能获取到状态问题

      <img src="https://github.com/biandh/12306_flask/raw/master/flask_app/downloads/4.jpg" width="300" height="200"/>
      <br/>
      <img src="https://github.com/biandh/12306_flask/raw/master/flask_app/downloads/5.jpg" width="300" height="100"/>


思路：先查是否有票，有则进入官网购买，无则进行抢票

运行依赖环境：见requirements.txt 文件

运行步骤：
   1. cd 12306_flask-master/flask_app
   2. python app.py
   3. 网页输入: http://127.0.0.1:5000

希望大家都能买到回家过年的票~~~~~


