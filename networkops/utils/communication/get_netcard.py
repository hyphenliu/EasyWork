#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File  : get_netcard.py
@Author: HP.Liew
@Date  : 2020/3/3 10:24
@Desc  : 
'''
from ctypes import *
import os
import socket
import struct


# IP头定义
class IP(Structure):
    _fields_ = [
        ("ihl", c_ubyte, 4),
        ("version", c_ubyte, 4),
        ("tos", c_ubyte),
        ("len", c_ushort),
        ("id", c_ushort),
        ("offset", c_ushort),
        ("ttl", c_ubyte),
        ("protocol_num", c_ubyte),
        ("sum", c_ushort),
        ("src", c_ulong),
        ("dst", c_ulong)
    ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buff=None):
        # 协议字段与协议名称对应
        self.protocol_map = {1: 'ICMP', 2: 'IGMP', 3: 'GGP', 4: 'IP', 6: 'TCP', 17: 'UDP', 41: 'IPV6'}

        # 可读性更强的ip地址
        self.src_address = socket.inet_ntoa(struct.pack("<L", self.src))
        self.dst_address = socket.inet_ntoa(struct.pack("<L", self.dst))

        # 协议类型
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


if __name__ == "__main__":
    # 监听主机（获取本机ip）
    sysinfo = socket.gethostbyname_ex(socket.getfqdn(socket.gethostname()))
    ip_addrs = sysinfo[2] # 获取本机所有的IP地址
    host = ip_addrs[-1]

    # 创建原始套接字， 然后绑定在公开接口上
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))

    # 设置在捕获的数据包中包含的IP头
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # 在windows平台上， 我们需要设置IOCTL以启用混杂模式
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            # 读取数据包
            raw_buffer = sniffer.recvfrom(65535)[0]

            # 将缓冲区前的20个字段按IP头进行解析
            ip_header = IP(raw_buffer[0:20])

            # 输出协议和通信双方ip地址
            print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))


    # 出来CTRL-C
    except KeyboardInterrupt:
        # 如果运行在windows上，关闭混杂模式
        if os.name == "nt":
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
