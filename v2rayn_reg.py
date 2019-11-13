#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 注册帐号送3G科学上网流量
# 每天自动注册,登陆,取订阅配置并更新
import requests
import re
import random
import time
import datetime
import json
import os
import logging


def register_user(register_token, token_2, cookies):
    url_reg = 'https://www.xyw.link/register?aff=3064'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'Referer': 'https://www.xyw.link/register?aff=3064',
        'Host': 'www.xyw.link'
    }
    src = random.randint(11111111, 9999999999)
    reg_username = str(src)
    data_post = {
        'username': reg_username+'@qq.com',
        'register_token': register_token,
        '_token': token_2,
        'aff': '',
        'password': '00000000',
        'repassword': '00000000',
        'code': ''
    }

    logging.info(datetime.datetime.now().strftime(
        '%H:%M:%S.%f')+" "+reg_username+" "+str(data_post))

    try:
        res_obj = requests.post(
            url=url_reg, data=data_post, headers=headers, cookies=cookies)  # 创建网页访问对象
        logging.info(datetime.datetime.now().strftime(
            '%H:%M:%S.%f')+" 连接网页成功!")
    except:
        logging.info(datetime.datetime.now().strftime('%H:%M:%S.%f')+" 异常")

    try:
        reg_end = re.search('注册成功', res_obj.text)
        logging.info(datetime.datetime.now().strftime(
            '%H:%M:%S.%f')+" "+str(reg_end.group()))
        cookies = res_obj.cookies.get_dict()
        return reg_username+'@qq.com', cookies
    except:
        logging.info(datetime.datetime.now().strftime('%H:%M:%S.%f')+" 注册失败")
        exit()


def register_get_token(url_reg):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0 Safari/537.36'
    }

    try:
        res_obj = requests.get(url=url_reg, headers=headers)  # 创建网页访问对象
        register_tokens = re.compile(r'register_token" value="(.+?)"')  # 定义正则
        token_1 = re.compile(r'"_token" value="(.+?)"')  # 定义正则
        register_token = register_tokens.findall(res_obj.text.encode(
            'utf-8').decode('unicode_escape'))
        token_2 = token_1.findall(res_obj.text.encode(
            'utf-8').decode('unicode_escape'))
        cookies = res_obj.cookies.get_dict()
        logging.info(datetime.datetime.now().strftime(
            '%H:%M:%S.%f')+" "+str(register_token)+str(token_2)+str(cookies))
    except Exception as e:
        logging.error(datetime.datetime.now().strftime('%H:%M:%S.%f') + str(e))
        exit()
    else:             # 没有异常出错，走else的逻辑代码
        pass
    finally:            # 不管有没有错，都执行finnally
        pass

    return register_token, token_2, cookies


def login(username, token_2, cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0 Safari/537.36',
        'Host': 'www.xyw.link',
        'Referer': 'https://www.xyw.link/login'
    }

    url_login = 'https://www.xyw.link/login'
    data_post = {
        '_token': token_2,
        'password': '00000000',
        'username': username
    }

    res_obj = requests.post(url=url_login, data=data_post,
                            headers=headers, cookies=cookies, allow_redirects=False)  # 创建网页访问对象
    time.sleep(1)
    sub_url = 'https://www.xyw.link/nodeList'
    sub_url_re = re.compile(r'https://www.hxs.best/s/(.+?)"')  # 定义正则
    res_obj = requests.get(sub_url, headers=headers,
                           cookies=res_obj.cookies.get_dict())
    sub_url_end = 'https://www.hxs.best/s/'+sub_url_re.findall(res_obj.text.encode(
        'utf-8').decode('unicode_escape'))[0]
    logging.info(datetime.datetime.now().strftime(
        '%H:%M:%S.%f')+" "+sub_url_end)
    return sub_url_end


def v2rayn(sub_url_end, v2_dir):
    with open(v2_dir+'guiNConfig.json', 'r', encoding='UTF-8') as v2_file:
        v2_cfg_dict = json.load(fp=v2_file)
    v2_cfg_dict['subItem'][0]['url'] = sub_url_end
    # logging.info(datetime.datetime.now().strftime('%H:%M:%S.%f')+" "+str(v2_cfg_dict))
    with open(v2_dir+'guiNConfig.json', 'w', encoding='UTF-8') as v2_file:
        json.dump(v2_cfg_dict, fp=v2_file, indent=4,
                  sort_keys=False, ensure_ascii=False)  # 格式化写入

    os.system('taskkill /F /IM v2rayN.exe')
    os.startfile(v2_dir + 'v2rayN.exe')
    logging.info(datetime.datetime.now().strftime('%H:%M:%S.%f')+" 请到软件重新更新订阅")


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.dirname(__file__)+'/v2.log',
                    filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logging.info(datetime.datetime.now().strftime('%H:%M:%S.%f')+" 程序开始执行")


register_token, token_2, cookies = register_get_token(
    'https://www.xyw.link/register?aff=3064')
username, cookies1 = register_user(register_token[0], token_2[0], cookies)
sub_url_end = login(username, token_2[0], cookies)
v2rayn(sub_url_end, v2_dir=r'D:/soft/v2rayN-Core/')


