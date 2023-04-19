#!/usr/bin/python3
#coding=utf-8

from struct import Struct

'''数据域中的帧结构定义(比亚迪协议)'''

# 服务器->充电桩:应答心跳信息
CMD101_struct = Struct('>7s')

# 充电桩->服务器:心跳信息
CMD102_struct = Struct('>BB')

# 服务器->充电桩:充电控制信息
CMD103_struct = Struct('>17s10sBIII7s173s')

# 充电桩->服务器:上报充电数据
CMD104_struct = Struct('>10s17sBIHHHHIBBBBIIHI4s20sBHIB141s')

# 服务器->充电桩:应答时段电量
CMD105_struct = Struct('>17s10sI10s')

# 充电桩->服务器:上报时段电量
CMD106_struct = Struct('>10s17sBIIHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH10s')

# 服务器->充电桩:升级文件下载指令
CMD251_struct = Struct('>HH32s160s')

# 充电桩->服务器:升级文件下载结果
CMD252_struct = Struct('>HH32sB')

# 服务器->充电桩:远程升级指令
CMD253_struct = Struct('>HH32s')

# 充电桩->服务器:远程升级结果
CMD254_struct = Struct('>HH32sB')
