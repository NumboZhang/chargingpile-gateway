#!/usr/bin/python3
#coding=utf-8

import cmd_struct_byd
from protocol_byd import Protocol_byd
from logger import log
from utility import TimeUtil_Byd
from utility import IdUtil
from manage import Manage


proto = Protocol_byd()


def CMD103_control_cmd_req(ver, id, gun, id2, serial_number, cmd, unit_price, balance, total_price):
    '''CMD103:服务器下发充电桩控制命令'''
    id_byte = IdUtil.string2bytes(id)
    id2_byte = IdUtil.string2bytes(id2)
    serial_number_byte = IdUtil.int2BCDbytes(serial_number)
    datetime = TimeUtil_Byd.localtimeBCD()
    packed_data = cmd_struct_byd.CMD103_struct.pack(id2_byte, serial_number_byte, cmd, unit_price, balance, total_price, datetime, b'')
    packed_frame = proto.pack(ver, 103, id_byte, gun, packed_data)
    return packed_frame

def CMD102_heartbeat(id, gun, data):
    '''CMD102:充电桩上传心跳包信息'''
    status = 0
    struct_size = cmd_struct_byd.CMD102_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct_byd.CMD102_struct.unpack(data)
        network = d[0]  # 网络制式
        signal = d[1]   # 信号级别
        log.info("[{}]心跳, 网络制式:{}, 信号级别{}".format(id, network, signal))
    except Exception as e:
        log.warning(e)
        status = 1
    return status

def CMD101_heartbeat_resp(ver, id, gun):
    '''CMD101:服务器应答心跳包信息'''
    id_byte = IdUtil.string2bytes(id)
    datetime = TimeUtil_Byd.localtimeBCD()
    packed_data = cmd_struct_byd.CMD101_struct.pack(datetime)
    packed_frame = proto.pack(ver, 101, id_byte, gun, packed_data)
    return packed_frame

def CMD104_status_info(id, gun, data):
    '''CMD104:充电桩上报状态信息'''
    status = 0
    struct_size = cmd_struct_byd.CMD104_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct_byd.CMD104_struct.unpack(data)
        serial_number = IdUtil.BCDbytes2int(d[0])  # 订单号/流水号
        id2 = IdUtil.bytes2string(d[1]) #充电桩编码(VIN码)
        work_status = d[2]              # 工作状态
        card_id = d[3]                  # 卡号
        pile_id = d[4]                  # 桩号
        ac_A = d[5]                     # 交流电流
        ac_V = d[6]                     # 交流电压
        electric1 = d[7]                # 充电电量(0.01kwh)
        total_electric = d[8]           # 累计充电电量(0.001kwh)
        temp_gun1 = d[9]                # 充电枪1温度
        temp_gun2 = d[10]               # 充电枪2温度
        temp_3 = d[11]                  # 温度3(预留)
        temp_4 = d[12]                  # 温度4(预留)
        error_code1 = d[13]             # 故障码1(见附录)
        error_code2 = d[14]             # 故障码2(预留)
        rated_power = d[15]             # 额定功率(0.1kw)
        current_power = d[16]           # 当前功率(0.1kw)
        gateway_sw_ver = IdUtil.bytes2string(d[17]) # 网关软件版本
        ICCID = IdUtil.bytes2string(d[18])          # 物联卡编号
        mobile_operator = d[19]         # 移动通信运营商
        pile_sw_ver = d[20]             # 充电桩软件版本
        electric2 = d[21]               # 充电电量(0.001kwh)
        gateway_hw_ver = d[22]          # 网关硬件版本
        log.info("[{}]状态信息,充电枪:{},工作状态:{},流水号:{},VIN码:{}卡号:{},桩号:{},电流:{},电压:{},充电电量:{},累计充电电量:{},枪1温度:{},枪2温度:{},故障码:{},额定功率:{},当前功率:{},网关软件版本:{},网关硬件版本:{},运营商:{}"\
            .format(id, gun, work_status, serial_number, id2, card_id, pile_id, ac_A, ac_V, electric2, total_electric, temp_gun1, temp_gun2, error_code1, rated_power, current_power, gateway_sw_ver, gateway_hw_ver, mobile_operator))
    except Exception as e:
        log.warning(e)
        status = 1
    return status

def CMD106_charging_record(id, gun, data):
    '''CMD106:充电桩上报充电记录信息'''
    status = 0
    id2  = ''
    serial_number = 0
    struct_size = cmd_struct_byd.CMD106_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id2, serial_number
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct_byd.CMD106_struct.size(data)
        serial_number  = IdUtil.BCDbytes2int(d[0])  # 订单号/流水号
        id2 = IdUtil.bytes2string(d[1]) # 充电桩编码(VIN码)
        work_status = d[2]              # 工作状态
        total_electric = d[3]           # 累计充电电量(0.001kwh)
        total_record = d[4]             # 充电记录条数
        log.info("[{}]充电记录,充电枪:{},工作状态:{},流水号:{},VIN码:{},累计充电电量:{},充电记录条数:{}"\
            .format(id, gun, work_status, serial_number, id2, total_electric, total_record))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id2, serial_number

def CMD105_charging_record_resp(ver, id, gun, id2, serial_number, money=0):
    '''CMD105:服务器应答充电记录'''
    id_byte = IdUtil.string2bytes(id)
    id2_byte = IdUtil.string2bytes(id2)
    serial_number_byte = IdUtil.int2BCDbytes(serial_number)
    packed_data = cmd_struct_byd.CMD105_struct.pack(id2_byte, serial_number_byte, money, b'')
    packed_frame = proto.pack(ver, 105, id_byte, gun, packed_data)
    return packed_frame

def CMD252_download_result(id, gun, data):
    '''CMD252:充电桩升级文件下载结果'''
    struct_size = cmd_struct_byd.CMD252_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct_byd.CMD252_struct.unpack(data)
        sw_ver = IdUtil.bytes2string(d[2])  # 软件版本
        result = d[3]                       # 结果
        log.info("[{}]升级文件下载结果:{}, 软件版本{}".format(id, result, sw_ver))
    except Exception as e:
        log.warning(e)
        status = 1
    return status

def CMD254_download_result(id, gun, data):
    '''CMD254:充电桩升级结果'''
    struct_size = cmd_struct_byd.CMD254_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct_byd.CMD254_struct.unpack(data)
        sw_ver = IdUtil.bytes2string(d[2])  # 软件版本
        result = d[3]                       # 结果
        log.info("[{}]升级结果:{}, 软件版本{}".format(id, result, sw_ver))
    except Exception as e:
        log.warning(e)
        status = 1
    return status


def parse_frame(sock, func_tuple, client_address, frame):
    '''帧解析总入口'''
    sender = func_tuple[0]
    asyn_send = func_tuple[1]
    asyn_close = func_tuple[2]
    status, ver, cmd, id, gun, data = proto.unpack(frame)
    if status != 0:
        log.warning(Protocol_byd.unpack_status_info(status))
        return
    
    id = IdUtil.bytes2string(id)

    if cmd == 102:
        log.info("{}-->CMD({}):充电桩心跳".format(client_address, cmd))
        status = CMD102_heartbeat(id, gun, data)
        if status == 0:
            resp_frame = CMD101_heartbeat_resp(ver, id, gun)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):充电桩心跳应答失败".format(client_address, cmd))
    
    elif cmd == 104:
        log.info("{}-->CMD({}):充电桩上报充电数据".format(client_address, cmd))
        status = CMD104_status_info(id, gun, data)
        if status == 0:
            pass
        else:
            log.warning("{}-->CMD({}):充电桩状态信息上报失败".format(client_address, cmd))
    
    elif cmd == 106:
        log.info("{}-->CMD({}):充电桩上报充电记录".format(client_address, cmd))
        status, id2, serial_number = CMD106_charging_record(id, gun, data)
        if status == 0:
            resp_frame = CMD105_charging_record_resp(ver, id, gun, id2, serial_number)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):充电桩上报充电记录失败".format(client_address, cmd))
    
    elif cmd == 252:
        log.info("{}-->CMD({}):充电桩升级文件下载结果".format(client_address, cmd))
        status = CMD252_download_result(id, gun, data)
        if status == 0:
            pass
        else:
            log.warning("{}-->CMD({}):充电桩升级文件下载结果解析失败".format(client_address, cmd))
    
    elif cmd == 254:
        log.info("{}-->CMD({}):充电桩远程升级结果".format(client_address, cmd))
        status = CMD254_download_result(id, gun, data)
        if status == 0:
            pass
        else:
            log.warning("{}-->CMD({}):充电桩远程升级结果解析失败".format(client_address, cmd))
    
    else:
        log.warning("{}-->CMD({}):未知命令代码".format(client_address, cmd))
    
    Manage.add_client(id, sock, client_address, asyn_send, asyn_close, protocol_type=1)