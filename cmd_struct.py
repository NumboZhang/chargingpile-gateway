#!/usr/bin/python3
#coding=utf-8

from struct import Struct

'''数据域中的帧结构定义'''

# 服务器->充电桩:控制命令
CMD5_struct = Struct('<HHBIBHI32s')

# 充电桩->服务器:对CMD5控制命令的应答
CMD6_struct = Struct('<HH32sBIBB32s')

# 服务器->充电桩:开启充电控制命令
CMD7_struct = Struct('<HHBIIII8sB32sBI32s')

# 充电桩->服务器:对CMD7开启充电控制的应答
CMD8_struct = Struct('<HH32sBI32s')

# 服务器->充电桩:参数更新命令
CMD9_struct = Struct('<HH32sBB')

# 充电桩->服务器:查询计费策略
CMD11_struct = Struct('<HH32sB')

# 服务器->充电桩:下发计费策略命令
CMD12_struct = Struct('<HH32sH3s3s3s3s3s3s3s3s3s3sBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBH')

# 服务器->充电桩:下发充电桩二维码
CMD13_struct = Struct('<HH32s8s64s64s64s64s')

# 充电桩->服务器:查询充电桩二维码
CMD14_struct = Struct('<HH32sB')

# 服务器->充电桩:应答心跳包信息
CMD101_struct = Struct('<HHH')

# 充电桩->服务器:心跳包信息
CMD102_struct = Struct('<HH32sH')

# 服务器->充电桩:应答状态信息包
CMD103_struct = Struct('<HHBII32s')

# 充电桩->服务器:状态信息包上报
CMD104_struct = Struct('<HH32sBBBBBIBIIIHHHHBHHHHHHHIIIIBBIB32sB8sIIIIIIBBBB32s')

# 服务器->充电桩:应答签到信息
CMD105_struct = Struct('<HHIBB128sI')

# 充电桩->服务器:签到信息上报
CMD106_struct = Struct('<HH32sBIHIBHBBBBI8s8s8s8sIH')

# 充电桩->服务器:告警信息上报
CMD108_struct = Struct('<HH32s32s')

# 服务器->充电桩:应答充电记录信息
CMD201_struct = Struct('<HHB32sII32s')

# 充电桩->服务器:上报充电记录信息
CMD202_struct = Struct('<HH32sBB32s8s8sIBBIIIIIIIIIBBI17s8sHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHB32s')

# 服务器->充电桩:应答BMS信息
CMD301_struct = Struct('<HH')

# 充电桩->服务器:上报BMS信息
CMD302_struct = Struct('<HHHH32sBB3sBIIIIHBBIBB17s8sIIIIBHIBIIBIIIBHIBBBBBBBBBBBBBBBBBBBBBBBBBBHIIBBBBBBBBBBBBBBBBBBBBBHHHHBBI32s')

