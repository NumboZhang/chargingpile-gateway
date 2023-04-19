#!/usr/bin/python3
#coding=utf-8

import cmd_struct
from protocol import Protocol
from logger import log
from utility import TimeUtil
from utility import IdUtil
from manage import Manage


proto = Protocol()


def CMD5_control_cmd_req(info, gun_id, cmd_index, cmd_para, serial_number = ''):
    '''CMD5:服务器下发充电桩控制命令'''
    reserve = 0
    stop_reason = 0     # 停止充电原因(0-后台主动下发)
    serial_number_byte = IdUtil.string2bytes(serial_number) # 订单号/流水号
    packed_data = cmd_struct.CMD5_struct.pack(reserve, stop_reason, gun_id, cmd_index, 1, 4, cmd_para, serial_number_byte)
    packed_frame = proto.pack(info, 5, packed_data)
    return packed_frame

def CMD7_start_charging_req(info, gun_id, card_id = '', serial_number = ''):
    '''CMD7:服务器下发开启充电控制命令'''
    reserve = 0
    type = 0            # 充电生效类型(0-即时充电)
    stop_password = 0   # 充电停止密码
    strategy = 0        # 充电策略(0-充满为止)
    strategy_para = 0   # 充电策略参数
    begin_time_byte = TimeUtil.localtimeBCD()   # 预约/定时启动时间(标准时间)
    timeout_min =  60                           # 预约超时时间(min)
    card_id_byte = IdUtil.string2bytes(card_id) # 用户卡号
    offline_charging_en = 1                     # 断网充电标志(0‐不允许,1‐允许)
    offline_charging_quantity = 1000            # 离线可充电电量(0.01kwh)
    serial_number_byte = IdUtil.string2bytes(serial_number) # 订单号/流水号
    packed_data = cmd_struct.CMD7_struct.pack(reserve, reserve, gun_id, type, stop_password, strategy, strategy_para, begin_time_byte, timeout_min, card_id_byte, offline_charging_en, offline_charging_quantity, serial_number_byte)
    packed_frame = proto.pack(info, 7, packed_data)
    return packed_frame

def CMD9_update_para_req(info, id, gun_id, type):
    '''CMD9:服务器下发参数更新命令'''
    reserve = 0
    id_byte = IdUtil.string2bytes(id)   # 充电桩编号
    packed_data = cmd_struct.CMD9_struct.pack(reserve, reserve, id_byte, gun_id, type)
    packed_frame = proto.pack(info, 9, packed_data)
    return packed_frame

def CMD6_control_cmd_result(data):
    '''CMD6:充电桩对后台控制命令应答'''
    status = 0
    id = ''
    gun_id = 0
    result = 0
    struct_size = cmd_struct.CMD6_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, gun_id, result
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD6_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])
        gun_id = d[3]       # 充电枪口号
        cmd_index = d[4]    # 命令地址索引
        cmd_num = d[5]      # 命令个数
        result = d[6]       # 命令执行结果
        serial_number  = IdUtil.bytes2string(d[7])  # 订单号/流水号
        log.info("[{}]控制命令执行结果:{},充电枪口:{},命令地址索引:{},命令个数:{},流水号:{}".format(id, result, gun_id, cmd_index, cmd_num, serial_number))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, gun_id, result

def CMD8_start_charging_result(data):
    '''CMD8:充电桩对开启充电控制命令应答'''
    status = 0
    id = ''
    gun_id = 0
    result = 0
    struct_size = cmd_struct.CMD8_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, gun_id, result
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD8_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])
        gun_id = d[3]       # 充电枪口号
        result = d[4]       # 命令执行结果(具体参阅附录3)
        serial_number  = IdUtil.bytes2string(d[5])  # 订单号/流水号
        log.info("[{}]开启充电控制命令执行结果:{},充电枪口:{},流水号:{}".format(id, result, gun_id, serial_number))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, gun_id, result

def CMD11_query_accounting_strategy(data):
    '''CMD11:充电桩查询该桩的充电计费策略'''
    status = 0
    id = ''
    index = 0
    struct_size = cmd_struct.CMD11_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, index
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD11_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])
        index = int(d[3])   # 充电枪口号
        log.info("[{}]查询计费策略,充电枪口:{}".format(id, index))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, index

def CMD12_query_accounting_strategy_resp(info, id, index):
    '''CMD12:服务器下发充电资费策略'''
    reserve = 0
    id_byte = IdUtil.string2bytes(id)
    p1 = (250).to_bytes(3, byteorder = 'little')    # 尖峰电价
    p2 = (250).to_bytes(3, byteorder = 'little')    # 尖峰服务费
    p3 = (250).to_bytes(3, byteorder = 'little')    # 高峰电价
    p4 = (250).to_bytes(3, byteorder = 'little')    # 高峰服务费
    p5 = (250).to_bytes(3, byteorder = 'little')    # 平谷电价
    p6 = (250).to_bytes(3, byteorder = 'little')    # 平谷服务费
    p7 = (250).to_bytes(3, byteorder = 'little')    # 低谷电价
    p8 = (250).to_bytes(3, byteorder = 'little')    # 低谷服务费
    p9 = (250).to_bytes(3, byteorder = 'little')    # 通用电价
    p10 = (250).to_bytes(3, byteorder = 'little')   # 通用服务费
    t1 = 6  # 尖峰（小时）开始时间1
    t2 = 30 # 尖峰（分钟）开始时间1
    t3 = 12 # 尖峰（小时）结束时间1
    t4 = 50 # 尖峰（分钟）结束时间1
    t5 = 16 # 尖峰（小时）开始时间2
    t6 = 40 # 尖峰（分钟）开始时间2
    t7 = 18 # 尖峰（小时）结束时间2
    t8 = 40 # 尖峰（分钟）结束时间2
    t9 = 6  # 高峰（小时）开始时间1
    t10 = 30 # 高峰（分钟）开始时间1
    t11 = 12 # 高峰（小时）结束时间1
    t12 = 50 # 高峰（分钟）结束时间1
    t13 = 16 # 高峰（小时）开始时间2
    t14 = 40 # 高峰（分钟）开始时间2
    t15 = 18 # 高峰（小时）结束时间2
    t16 = 40 # 高峰（分钟）结束时间2
    t17 = 6  # 平谷（小时）开始时间1
    t18 = 30 # 平谷（分钟）开始时间1
    t19 = 12 # 平谷（小时）结束时间1
    t20 = 50 # 平谷（分钟）结束时间1
    t21 = 16 # 平谷（小时）开始时间2
    t22 = 40 # 平谷（分钟）开始时间2
    t23 = 18 # 平谷（小时）结束时间2
    t24 = 40 # 平谷（分钟）结束时间2
    t25 = 6  # 低谷（小时）开始时间1
    t26 = 30 # 低谷（分钟）开始时间1
    t27 = 12 # 低谷（小时）结束时间1
    t28 = 50 # 低谷（分钟）结束时间1
    t29 = 16 # 低谷（小时）开始时间2
    t30 = 40 # 低谷（分钟）开始时间2
    t31 = 18 # 低谷（小时）结束时间2
    t32 = 40 # 低谷（分钟）结束时间2
    parking_fee = 200 # 停车费用
    packed_data = cmd_struct.CMD12_struct\
        .pack(reserve, reserve, id_byte, index, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10,\
            t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16,\
                t17, t18, t19, t20, t21, t22, t23, t24, t25, t26, t27, t28, t29, t30, t31, t32,\
                    parking_fee)
    packed_frame = proto.pack(info, 12, packed_data)
    return packed_frame

def CMD14_query_QR_code(data):
    '''CMD14:充电桩查询枪二维码'''
    status = 0
    id = ''
    num = 0
    struct_size = cmd_struct.CMD14_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, num
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD14_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])
        num = d[3]   # 充电枪数量
        log.info("[{}]查询枪二维码,充电枪数量:{}".format(id, num))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, num

def CMD13_query_QR_code_resp(info, id, qr1=b'', qr2=b'', qr3=b'', qr4=b''):
    '''CMD13:服务器下发枪二维码'''
    reserve = 0
    time = TimeUtil.localtimeBCD()      # 标准时钟时间(用于同步充电桩时钟)
    id_byte = IdUtil.string2bytes(id)   # 充电桩编码
    packed_data = cmd_struct.CMD13_struct.pack(reserve, reserve, id_byte, time, qr1, qr2, qr3, qr4)
    packed_frame = proto.pack(info, 13, packed_data)
    return packed_frame

def CMD104_status_info(data):
    '''CMD104:充电桩上报状态信息'''
    status = 0
    id = ''
    gun_id = 0
    serial_number = ''
    struct_size = cmd_struct.CMD104_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, gun_id, serial_number
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD104_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])
        gun_id = d[4]       # 充电口号
        work_status = d[6]  # 工作状态
        soc = d[7]          # SOC %
        alarm_code = d[8]   # 当前最高告警编码(具体参阅附录1)
        car_conn = d[9]     # 车连接状态
        total_fee = d[10]   # 累计充电费用
        dc_V = d[13]        # 直流充电电压
        dc_A = d[14]        # 直流充电电流
        remain_time = d[24] # 剩余充电时间(min)
        charging_time = d[25]   # 充电时长(s)
        usage_electric = d[26]  # 累计充电电量(0.01kwh)
        start_mode = d[29]      # 充电启动方式
        appointment = d[32]     # 预约标志
        begin_time = TimeUtil.BCD2str(d[35]) # 预约/开始充电时间
        power = d[38]       # 充电功率
        serial_number  = IdUtil.bytes2string(d[46])  # 订单号/流水号
        log.info("[{}]状态信息,充电枪:{},工作状态:{},SOC:{}%,告警:{},车连接:{},费用:{},电压:{},电流:{},剩余时间:{}min,充电时长:{}s,累计电量:{},启动方式:{},预约:{},开始时间:{},功率:{},流水号:{}"\
            .format(id, gun_id, work_status, soc, alarm_code, car_conn, total_fee, dc_V, dc_A, remain_time, charging_time, usage_electric, start_mode, appointment, begin_time, power, serial_number))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, gun_id, serial_number

def CMD103_status_info_resp(info, gun_id, total_fee, balance, serial_number):
    '''CMD103:服务器应答充电桩状态信息'''
    reserve = 0
    serial_number_byte = IdUtil.string2bytes(serial_number) # 订单号/流水号
    packed_data = cmd_struct.CMD103_struct.pack(reserve, reserve, gun_id, total_fee, balance, serial_number_byte)
    packed_frame = proto.pack(info, 103, packed_data)
    return packed_frame

def CMD106_attendance(data):
    '''CMD106:充电桩上报签到信息'''
    status = 0
    id = ''
    rand = 0
    struct_size = cmd_struct.CMD106_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, rand
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD106_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])      # 充电桩编码
        time_str = TimeUtil.BCD2str(d[14])  # 当前充电桩系统时间
        rand = d[18]    # 桩生成随机数
        log.info("[{}]签到,功能标志:{},版本:{},签到间隔时间:{},充电枪:{},心跳周期:{},心跳超时次数:{},充电记录:{},系统时间:{},随机数:{}"\
            .format(id, d[3], d[4], d[8], d[10], d[11], d[12], d[13], time_str, rand))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, rand

def CMD105_attendance_resp(info, rand_resp):
    '''CMD105:服务器应答充电桩签到命令'''
    reserve = 0
    verification_en = 0         # 登入验证开关
    encryption_en = 0           # 加密开关
    rsa_public_modulus = b''    # RSA 公共模数(加密开时有效)
    rsa_public_key = 0          # RSA 公密(加密开时有效)
    packed_data = cmd_struct.CMD105_struct.pack(reserve, reserve, rand_resp, verification_en, encryption_en, rsa_public_modulus, rsa_public_key)
    packed_frame = proto.pack(info, 105, packed_data)
    return packed_frame

def CMD102_heartbeat(data):
    '''CMD102:充电桩上传心跳包信息'''
    status = 0
    id = ''
    count = 0
    struct_size = cmd_struct.CMD102_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, count
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD102_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])  # 充电桩编码
        count = d[3]                    # 心跳序号
        log.info("[{}]心跳序号:{}".format(id, count))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, count

def CMD101_heartbeat_resp(info, count):
    '''CMD101:服务器应答心跳包信息'''
    reserve = 0
    packed_data = cmd_struct.CMD101_struct.pack(reserve, reserve, count)
    packed_frame = proto.pack(info, 101, packed_data)
    return packed_frame

def CMD108_alarm_info(data):
    '''CMD108:充电桩上报告警信息'''
    status = 0
    id = ''
    count = 0
    struct_size = cmd_struct.CMD108_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, count
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD108_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])  # 充电桩编码
        alarm_code = d[3]               # 告警编码(具体参阅附录4)
        log.info("[{}]告警位:{}".format(id, alarm_code.hex()))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, count

def CMD202_charging_record(data):
    '''CMD202:充电桩上报充电记录信息'''
    status = 0
    id = ''
    gun_id = 0
    serial_number = ''
    struct_size = cmd_struct.CMD202_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, gun_id, serial_number
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD202_struct.unpack(data)
        id = IdUtil.bytes2string(d[2])  # 充电桩编码
        gun_id = d[4]                   # 充电口号
        card_id = IdUtil.bytes2string(d[5]) # 充电卡号
        begin_time = TimeUtil.BCD2str(d[6]) # 充电开始时间
        end_time = TimeUtil.BCD2str(d[7])   # 充电结束时间
        charging_time = d[8]                # 充电时间长度(s)
        begin_soc = d[9]                # 开始SOC
        end_soc = d[10]                 # 结束SOC
        end_reason = d[11]              # 充电结束原因(具体参阅附录2)
        usage_electric = d[12]          # 本次充电电量
        total_fee = d[15]               # 本次充电金额
        record_index = d[18]            # 当前充电记录索引
        strategy = d[21]                # 充电策略
        strategy_para = d[22]           # 充电策略参数
        start_mode = d[73]              # 启动方式
        serial_number  = IdUtil.bytes2string(d[74])  # 订单号/流水号
        log.info("[{}]充电记录,充电枪:{},充电卡:{},开始时间:{},结束时间:{},充电时长:{}s,开始SOC:{}%,结束SOC:{}%,结束原因:{},充电电量:{},充电金额:{},记录索引:{},充电策略:{},启动方式:{},流水号:{}"\
            .format(id, gun_id, card_id, begin_time, end_time, charging_time, begin_soc, end_soc, end_reason, usage_electric, total_fee, record_index, strategy, start_mode, serial_number))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, gun_id, serial_number

def CMD201_charging_record_resp(info, id, gun_id, total_fee, balance, serial_number):
    '''CMD201:服务器应答充电记录信息'''
    reserve = 0
    data_len = 0        # 业务数据长度(AES加密时有效)
    id_byte = IdUtil.string2bytes(id)                       # 充电桩编号
    serial_number_byte = IdUtil.string2bytes(serial_number) # 订单号/流水号
    packed_data = cmd_struct.CMD201_struct.pack(data_len, reserve, gun_id, id_byte, total_fee, balance, serial_number_byte)
    packed_frame = proto.pack(info, 201, packed_data)
    return packed_frame

def CMD302_bms_info(data):
    '''CMD302:充电桩上报BMS信息'''
    status = 0
    id = ''
    count = 0
    struct_size = cmd_struct.CMD302_struct.size
    if len(data) < struct_size:
        log.error('数据长度{}小于协议长度{}'.format(len(data), struct_size))
        status = 1
        return status, id, count
    elif len(data) > struct_size:
        data = data[:struct_size]
    
    try:
        d = cmd_struct.CMD302_struct.unpack(data)
        count = d[2]            # 报文次序计数
        gun_id = d[3]           # 充电口号
        id = IdUtil.bytes2string(d[4])  # 充电桩编码
        work_status = d[5]      # 工作状态
        car_conn = d[6]         # 车连接状态
        alarm_code = d[94]      # 告警编码
        serial_number  = IdUtil.bytes2string(d[95])  # 订单号/流水号
        log.info("[{}]BMS,报文计数:{},充电口:{},工作状态:{},车连接:{},告警:{},流水号:{}".format(id, count, gun_id, work_status, car_conn, alarm_code, serial_number))
    except Exception as e:
        log.warning(e)
        status = 1
    return status, id, count

def CMD301_bms_info_resp(info):
    '''CMD301:服务器应答BMS信息'''
    reserve = 0
    packed_data = cmd_struct.CMD301_struct.pack(reserve, reserve)
    packed_frame = proto.pack(info, 301, packed_data)
    return packed_frame

def parse_frame(sock, func_tuple, client_address, frame):
    '''帧解析总入口'''
    id = None
    sender = func_tuple[0]
    asyn_send = func_tuple[1]
    asyn_close = func_tuple[2]
    status, info, cmd, data = proto.unpack(frame)
    if status != 0:
        log.warning(Protocol.unpack_status_info(status))
        return

    #encrypt_en, protocol_ver = Protocol.unpack_info_field(info)

    if cmd == 6:
        log.info("{}-->CMD({}):后台控制命令应答".format(client_address, cmd))
        CMD6_control_cmd_result(data)
    
    elif cmd == 8:
        log.info("{}-->CMD({}):充电桩开启充电控制应答".format(client_address, cmd))
        CMD8_start_charging_result(data)

    elif cmd == 11:
        log.info("{}-->CMD({}):充电桩查询计费策略".format(client_address, cmd))
        status, id, index = CMD11_query_accounting_strategy(data)
        if status == 0:
            resp_frame = CMD12_query_accounting_strategy_resp(info, id, index)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):查询充电桩查询计费策略失败".format(client_address, cmd))

    elif cmd == 14:
        log.info("{}-->CMD({}):充电桩查询枪二维码".format(client_address, cmd))
        status, id, num = CMD14_query_QR_code(data)
        if status == 0:
            resp_frame = CMD13_query_QR_code_resp(info, id)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):查询枪二维码失败".format(client_address, cmd))

    elif cmd == 106:
        log.info("{}-->CMD({}):充电桩签到".format(client_address, cmd))
        status, id, rand = CMD106_attendance(data)
        if status == 0:
            resp_frame = CMD105_attendance_resp(info, rand)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):充电桩签到失败".format(client_address, cmd))
    
    elif cmd == 104:
        log.info("{}-->CMD({}):充电桩状态信息上报".format(client_address, cmd))
        status, id, gun_id, serial_number = CMD104_status_info(data)
        if status == 0:
            resp_frame = CMD103_status_info_resp(info, gun_id, 0, 0, serial_number)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):充电桩状态信息上报失败".format(client_address, cmd))
    
    elif cmd == 102:
        log.info("{}-->CMD({}):充电桩心跳".format(client_address, cmd))
        status, id, count = CMD102_heartbeat(data)
        if status == 0:
            resp_frame = CMD101_heartbeat_resp(info, count)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):充电桩心跳应答失败".format(client_address, cmd))
    
    elif cmd == 108:
        log.info("{}-->CMD({}):充电桩上报告警信息".format(client_address, cmd))
        CMD108_alarm_info(data)

    elif cmd == 202:
        log.info("{}-->CMD({}):充电桩上报充电记录信息".format(client_address, cmd))
        status, id, gun_id, serial_number = CMD202_charging_record(data)
        if status == 0:
            resp_frame = CMD201_charging_record_resp(info, id, gun_id, 0, 0, serial_number)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):充电记录上报失败".format(client_address, cmd))

    elif cmd == 302:
        log.info("{}-->CMD({}):充电桩上报BMS信息".format(client_address, cmd))
        status, id, count = CMD302_bms_info(data)
        if status == 0:
            resp_frame = CMD301_bms_info_resp(info)
            sender(resp_frame)
        else:
            log.warning("{}-->CMD({}):BMS信息应答失败".format(client_address, cmd))
        
    else:
        log.warning("{}-->CMD({}):未知命令代码".format(client_address, cmd))
    
    if id is not None:
        Manage.add_client(id, sock, client_address, asyn_send, asyn_close)