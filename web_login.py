#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  利用华为ups检测机房是否停电
#  停电后发送企业微信告警并对主要服务器关机


import sys
import os
import time
import ssl
import json
import http.cookiejar
import paramiko
from urllib import parse, request

#   ----------------------企业微信配置开始------------------------------------
corpid = '你自己的pid'
corpsecret = '你自己的key'
wx_url = 'https://qyapi.weixin.qq.com'
log_file = r'D:\脚本\web_loing.log'


#   ----------------------取token---------------------------------------------
def get_token(wx_url, corpid, corpsecret):
    token_url = '{}/cgi-bin/gettoken?corpid={}&corpsecret={}'.format(
        wx_url, corpid, corpsecret)
    token = json.loads(request.urlopen(token_url).read().decode())[
        'access_token']
    print(token)
    return token


#   -----------------------构建告警信息json----------------------------------------
def messages(msg):
    values = {"touser": 'lijingfeng', "msgtype": 'text',
              "agentid": 1000002, "text": {'content': msg}, "safe": 0}
    msges = (bytes(json.dumps(values), 'utf-8'))
    print(msges)
    return msges


#   ------------------发送告警信息--------------
def send_message(wx_url, token, data):
    send_url = '{}/cgi-bin/message/send?access_token={}'.format(wx_url, token)
    respone = request.urlopen(request.Request(url=send_url, data=data)).read()
    x = json.loads(respone.decode())['errcode']
    print(x)
    if x == 0:
        print('Succesfully')
    else:
        print('Failed')
        with open(log_file, 'a', encoding='utf-8') as file_zj:
            file_nr = time.strftime(
                "%Y-%m-%d %X", time.localtime(time.time())) + ' 微信发送失败!.\n'
            file_zj.writelines(file_nr)
#   ----------------------企业微信配置结束------------------------------------


#   ------------------连接linux主 机开始--------------
def run(ssh_num):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_num[0], 22, ssh_num[2], ssh_num[1])
        stdin, stdout, stderr = ssh.exec_command('shutdown -h 5')
        ssh_end = stdout.read().decode('utf-8')  # 回显
        print(ssh_end)
        print("check status %s OK\n" % ssh_num[0])
        ssh.close()
        # 关机后调用企业微信发送,并关本机
        msg = '报警主机: {}\n 报警时间: {} \n 报警信息:检测到电源有故障,请检查是否误报,服务器将于5分钟后关机 \n 当前状态:等待关机'.format(
            ssh_num[0], time.strftime("%Y-%m-%d %X", time.localtime(time.time())))

        test_token = get_token(wx_url, corpid, corpsecret)
        msg_data = messages(msg)
        send_message(wx_url, test_token, msg_data)

    except Exception as ex:
        print("\tError %s\n" % ex)
        with open(log_file, 'a', encoding='utf-8') as file_zj:
            file_nr = time.strftime("%Y-%m-%d %X", time.localtime(time.time())) + \
                "\tError %s" % ex + ' to ' + ssh_num[0] + '\n'
            file_zj.writelines(file_nr)
        # 抛异常时调用企业微信发送,并退出
        msg = ssh_num[0] + '尝试关机失败'
        test_token = get_token(wx_url, corpid, corpsecret)
        msg_data = messages(msg)
        send_message(wx_url, test_token, msg_data)
#   ------------------连接linux主 机结束--------------


ssl._create_default_https_context = ssl._create_unverified_context  # 忽略ssl错误
post_time = str(int(time.time())) + "000"  # 提交时间
textmod = {"userName": "admin5", "password": "QAZwsx99",
           "dateTime": post_time}  # 提交数据
textmod = parse.urlencode(textmod).encode(encoding='utf-8')  # 转码
url = 'https://localhost:8443/security!login.action'
req = request.Request(url=url, data=textmod)
try:
    # 保存cookie
    cj = http.cookiejar.CookieJar()
    opener = request.build_opener(request.HTTPCookieProcessor(cj))
    r = opener.open(req).read().decode('utf-8')  # 返回登陆结果
except:
    # 抛异常时调用企业微信发送,并退出
    msg = 'ups_web不能正常连接.请检查'
    test_token = get_token(wx_url, corpid, corpsecret)
    msg_data = messages(msg)
    send_message(wx_url, test_token, msg_data)
    with open(log_file, 'a', encoding='utf-8') as file_zj:
        file_nr = time.strftime(
            "%Y-%m-%d %X", time.localtime(time.time())) + ' ups_web不能正常连接.请检查.\n'
        file_zj.writelines(file_nr)
    sys.exit()

login_zc = '{"retMsg":"op.successfully"}'
print(r)

if login_zc != r:  # 登陆失败发送消息,并退出
    msg = 'ups_web登陆出错了.请检查'
    test_token = get_token(wx_url, corpid, corpsecret)
    msg_data = messages(msg)
    send_message(wx_url, test_token, msg_data)
    with open(log_file, 'a', encoding='utf-8') as file_zj:
        file_nr = time.strftime(
            "%Y-%m-%d %X", time.localtime(time.time())) + ' ups_web登陆出错了.请检查.\n'
        file_zj.writelines(file_nr)
    sys.exit()

print(cj)

try:
    req = request.Request(
        'https://localhost:8443/alarmCurrent!initAlarmBoard.action')
    opener = request.build_opener(
        request.HTTPCookieProcessor(cj))  # 调用cookie访问
    r = opener.open(req).read().decode('utf-8')  # 返回状态结果
    print(r)
except:
    # 抛异常时调用企业微信发送,并退出
    msg = 'ups_web不能正常连接.请检查'
    test_token = get_token(wx_url, corpid, corpsecret)
    msg_data = messages(msg)
    send_message(wx_url, test_token, msg_data)
    with open(log_file, 'a', encoding='utf-8') as file_zj:
        file_nr = time.strftime(
            "%Y-%m-%d %X", time.localtime(time.time())) + ' ups_web获取电源状态时出错.请检查.\n'
        file_zj.writelines(file_nr)
    sys.exit()

end_zc = '{"alarmCountMap":{"alarm1":0,"alarm2":0,"alarm3":0,"alarm4":0}}'

req = request.Request(
    'https://localhost:8443/securitys!loginOut.action')  # 退出登陆
opener = request.build_opener(request.HTTPCookieProcessor(cj))  # 调用cookie访问
opener.open(req).read().decode('utf-8')  # 返回状态结果

if end_zc != r:
    with open(log_file, 'a', encoding='utf-8') as file_zj:
        file_nr = time.strftime(
            "%Y-%m-%d %X", time.localtime(time.time())) + ' 检测到电源有故障,请检查是否误报\n'
        file_zj.writelines(file_nr)
    ssh_all = (
        ('192.168.1.31', 'Mzj@Server31', 'root'), ('192.168.1.11', 'Mzj@Server11', 'root'), ('192.168.1.12', 'Mzj@Server12', 'root'), ('192.168.1.20', 'Mzj@Server20', 'root'))
    for ssh_num in ssh_all:
        print(ssh_num)
        run(ssh_num)

    os.system('shutdown -s -t 100')  # 关机,shutdown -a 取消关机


# TODO 需要增加数据可视化
# set CL=/FI"%VCINSTALLDIR%\\INCLUDE\\stdint.h" %CL%

