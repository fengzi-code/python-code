#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 备份服务器web网站和数据库数据
# 异地ftp备份10天

import ftplib
import os
import zipfile
import time


# 逐行读取ftp文本文件
# f.retrlines('RETR %s' % file)

# def ftp_download():
#     '''以二进制形式下载文件'''
#     file_remote = '1.txt'
#     file_local = 'D:\\test_data\\ftp_download.txt'
#     bufsize = 1024  # 设置缓冲器大小
#     fp = open(file_local, 'wb')
#     f.retrbinary('RETR %s' % file_remote, fp.write, bufsize)
#     fp.close()


def ftp_upload(host, username, password, port, romatepath, file_local, ftp_del_file):
    f = ftplib.FTP()  # 实例化FTP对象
    f.encoding = 'utf-8'  # 解决中文乱码问题
    f.set_debuglevel(2)        # 打开调试级别2，显示详细信息
    f.connect(host, port)
    f.login(username, password)  # 登录

    # 获取当前路径
    pwd_path = f.pwd()
    print("FTP当前路径:", pwd_path)
    f.cwd(romatepath)
    if ftp_del_file:
        f.delete(ftp_del_file)
    '''以二进制形式上传文件'''
    bufsize = 1024  # 设置缓冲器大小
    fp = open(file_local, 'rb')
    f.storbinary('STOR ' + file_remote, fp, bufsize)
    fp.close()
    f.quit()


# 压缩文件
def toZip(startdir):
    '''startdir:要压缩文件夹的绝对路径 '''
    file_news = time.strftime(
        "%Y%m%d%H%M%S", time.localtime()) + '.zip'  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
            print('压缩成功')
    z.close()
    return file_news


def del_bakfile(bak_log_path, file_remote):
    with open(bak_log_path+r'web_log.log', 'a+') as bak_log:
        bak_log.writelines(file_remote+'\n')
        bak_log.seek(0)     # 追加模式,移动到行首
        file_lines = bak_log.readlines()
    print(len(file_lines))
    if len(file_lines) > 10:
        with open(bak_log_path+r'web_log.log', 'w') as bak_log_in:
            print(len(file_lines))
            del_file = file_lines[0].strip()
            print(del_file)
            bak_log_in.writelines(file_lines[1:])   # 去除首行,重新写入文件
            os.remove(bak_log_path+del_file)
            return del_file
    return False


host = '172.16.184.10'
port = 12121
username = 'bak_user'
password = 'LYj!8031..'
romatepath = '木材管理系统\\web'     # ftp远程目录
local_bak_dir = 'F:\\bakup\\yunshu\\web\\'     # 本地保存目录
os.chdir(local_bak_dir)     # 切换工作目录
file_remote = toZip(r'E:\\yunshupublish')        # 压缩指定文件夹
ftp_del_file = del_bakfile(local_bak_dir, file_remote)     # 备份文件删除增加
file_local = local_bak_dir + file_remote     # 上传到ftp的文件
ftp_upload(host, username, password, port,romatepath, file_local, ftp_del_file)
