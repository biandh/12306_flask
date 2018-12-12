# 12306_flask
基于flask框架的12306抢票程序，本程序后台抢票功能参考了https://github.com/testerSunshine/12306
此外增加了多种查询功能
功能：
   1. 火车票查询，包括：
      1.1 常规站-站查询
       ![image](https://raw.github.com/biandh/12306_flask/tree/master/flask_app/downloads/1.jpg)
       ![image](https://raw.github.com/biandh/12306_flask/tree/master/flask_app/downloads/2.jpg)
      1.2 某个车次越站乘车查询
      ![image](https://raw.github.com/biandh/12306_flask/tree/master/flask_app/downloads/3.jpg)
      1.3 换乘查询(目前只支持1次换乘)

   2. 火车票购票
      与之前程序相同，修复了12306更新后地址不能用问题
      ![image](https://raw.github.com/biandh/12306_flask/tree/master/flask_app/downloads/4.jpg)
      ![image](https://raw.github.com/biandh/12306_flask/tree/master/flask_app/downloads/5.jpg)

思路：先查是否有票，有则进入官网购买，无则进行抢票

运行依赖环境：见requirements.txt 文件

运行步骤：
   1. cd 12306_flask-master/flask_app
   2. python app.py
   3. 网页输入: http://127.0.0.1:5000


