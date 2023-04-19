#!/usr/bin/python3
#coding=utf-8

from struct import Struct

class Protocol:
    
    def __init__(self):
        self.start = 0xF5AA
        self.serial = 0
    
    def __get_serial(self):
        self.serial = self.serial + 1
        return (self.serial & 0xFF)
    
    @staticmethod
    def __calc_check_sum(cmd, data):
        check_sum = (cmd & 0x00FF) + ((cmd & 0xFF00) >> 8)
        for i in range(len(data)):
            check_sum = check_sum + data[i]
        return (check_sum & 0xFF)
        
    def pack(self, info, cmd, data):
        data_len = len(data)
        serial = Protocol.__get_serial(self)
        check_sum = Protocol.__calc_check_sum(cmd, data)
        format_string = '<HHBBH{0}sB'.format(data_len)
        protocol_struct = Struct(format_string)
        packed_message = protocol_struct.pack(self.start, data_len + 9, info, serial, cmd, data, check_sum)
        return packed_message
    
    def unpack(self, message):
        status = 0
        info = 0x00
        cmd = 0
        data = b''
        if len(message) < 9:            # 报文小于最短长度
            status = 1
            return status, info, cmd, data
        start_field = (message[0] & 0xFF) | ((message[1] & 0xFF) << 8)
        if (start_field != self.start): # 报文起始域不对
            status = 2
            return status, info, cmd, data
        length_field = (message[2] & 0xFF) | ((message[3] & 0xFF) << 8)
        if length_field < 9:            # 报文长度域的值小于报文最短长度
            status = 3
            return status, info, cmd, data
        if len(message) < length_field: # 报文实际长度小于长度域的值
            status = 4
            return status, info, cmd, data
        if len(message) > length_field: # 报文实际长度大于长度域的值
            message = message[:length_field]    # 截断报文
        data_len = length_field - 9
        format_string = '<HHBBH{0}sB'.format(data_len)
        protocol_struct = Struct(format_string)
        unpacked_message = protocol_struct.unpack(message)
        info = unpacked_message[2]
        cmd = unpacked_message[4]
        data = unpacked_message[5]
        check_sum = unpacked_message[6]
        if check_sum != Protocol.__calc_check_sum(cmd, data):   # 校验和不对
            status = 5
        return status, info, cmd, data
    
    @staticmethod    
    def unpack_status_info(status):
        info = '未知错误'
        if status == 0:
            info = 'OK'
        elif status == 1:
            info = '报文小于最短长度'
        elif status == 2:
            info = '报文起始域不对'
        elif status == 3:
            info = '报文长度域的值小于报文最短长度'    
        elif status == 4:
            info = '报文实际长度小于长度域的值'
        elif status == 5:
            info = '校验和不对'
        return info
    
    @staticmethod
    def pack_info_field(encrypt_en, protocol_ver):
        '''组装帧中的信息域'''
        info = (encrypt_en & 0x01) << 7
        info = info | (protocol_ver & 0x0F)
        return info
    
    @staticmethod
    def unpack_info_field(info):
        '''解析帧中的信息域'''
        encrypt_en = (info >> 7) & 0x01
        protocol_ver = info & 0x0F
        return encrypt_en, protocol_ver



def protocol_test():
    info = 0x00
    cmd = 0
    data = b'\x01\x02\x03'

    test_protocol = Protocol()
    print(data)

    print('******<1>*******')
    packed_message = test_protocol.pack(info, cmd, data)
    print(packed_message.hex(' '))
    print(test_protocol.unpack(packed_message))

    print('******<2>*******')
    cmd = 106
    data = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00'
    print(len(data))
    print(data.hex(' '))
    packed_message = test_protocol.pack(info, cmd, data)
    print(packed_message.hex(' '))
    print(test_protocol.unpack(packed_message))

    print('******<3>*******')
    packed_message += b'\x01'
    print(test_protocol.unpack(packed_message))

    print('******<4>*******')
    packed_message = packed_message[0:len(packed_message) - 2]
    print(test_protocol.unpack(packed_message))

if __name__ == '__main__':
    protocol_test()


