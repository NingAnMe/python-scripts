#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2019/2/14
@Author  : AnNing
"""
from ftplib import FTP


if __name__ == '__main__':
    ftp_host = 'ftp.bou.class.noaa.gov'
    port = 21
    dir_name = '3914729564/001'
    file_name = 'RETR README'
    user = 'user'
    password = 'password'

    # 第一种
    ftp = FTP(host=ftp_host)
    ftp.login(user=user, passwd=password)  # 登录

    ftp = FTP()
    ftp.connect(host=ftp_host, port=port)

    ftp.retrlines('LIST')  # 列出详细模式的文件列表
    ftp.cwd(dir_name)  # 进入目录
    ftp.nlst()  # 列出文件名
    ftp.retrbinary(file_name, open('README', 'wb').write)  # 使用2进制模式下载文件
    ftp.storbinary('STOR filepath/test.xlsx', open('text.xlsx', 'rb'))  # 使用2进制模式上传文件
