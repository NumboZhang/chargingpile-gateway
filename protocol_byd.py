#!/usr/bin/python3
#coding=utf-8

import platform
import sys
import ctypes
import struct

def load_tea_lib():
    '''load the shared lib file'''
    system = platform.system()
    x86_x64 = struct.calcsize('P') * 8
    lib_path = None
    
    if system == 'Windows':
        if x86_x64 == 32:
            lib_path = './lib/x86/TEA.dll'
        elif x86_x64 == 64:
            lib_path = './lib/x64/TEA.dll'
    elif system == 'Linux':
        if x86_x64 == 32:
            lib_path = './lib/x86/libtea.so'
        elif x86_x64 == 64:
            lib_path = './lib/x64/libtea.so'
    try:
        tea_lib = ctypes.cdll.LoadLibrary(lib_path)
    except Exception as e:
        print(e)
        tea_lib = None
        
    return tea_lib

# 加载TEA加解密算法库
TEA_LIB = load_tea_lib()
# TEA秘钥(16字节)
TEA_KEY = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10'

class Protocol_byd:
    
    def __init__(self):
        global TEA_LIB
        global TEA_KEY
        self.start = 0xAABB
        self.end = 0x0D0A
        if TEA_LIB == None:
            print('Can not load TEA lib.')
            sys.exit(-1)
        if len(TEA_KEY) != 16:
            print('TEA length error.')
            sys.exit(-1)
        self.tea_lib = TEA_LIB
        self.tea_key = ctypes.create_string_buffer(TEA_KEY, 16)
    
    @staticmethod
    def __calc_check_sum(data):
        check_sum = 0
        for i in range(len(data)):
            check_sum = check_sum + data[i]
        return (check_sum & 0xFF)
        
    def pack(self, ver, cmd, id, gun, data):
        data_len_orig = len(data)   # 原始数据长度
        while len(data) < 8:        # 最小的加密长度为8字节
            data += b'\00'
        while len(data) % 4 != 0:   # 加密长度必须为4的倍数
            data += b'\00'
        data_buf = ctypes.create_string_buffer(data, len(data))         # 创建数据缓冲区
        self.tea_lib.btea_encrypt(data_buf, self.tea_key, len(data))    # 将缓冲区中的数据加密
        check_sum = self.__calc_check_sum(data_buf.raw)                 # 计算加密后数据的校验和
        data_len_enc = len(data_buf.raw)                                # 加密后的数据长度
        format_string = '>HBB13sBBHH{0}sH'.format(data_len_enc)
        protocol_struct = struct.Struct(format_string)
        packed_message = protocol_struct.pack(self.start, ver, cmd, id, gun, check_sum, data_len_enc - data_len_orig, data_len_enc, data_buf.raw, self.end)
        return packed_message
    
    def unpack(self, message):
        status = 0
        ver = 0x00
        cmd = 0
        id = b''
        gun = 0
        data = b''
        if len(message) < 33:           # 报文小于最短长度
            status = 1
            return status, ver, cmd, id, gun, data
        start_field = (message[1] & 0xFF) | ((message[0] & 0xFF) << 8)
        if (start_field != self.start): # 报文起始域不对
            status = 2
            return status, ver, cmd, id, gun, data
        length_field = (message[22] & 0xFF) | ((message[21] & 0xFF) << 8)
        if length_field < 8:            # 报文长度域的值小于数据域最短长度
            status = 3
            return status, ver, cmd, id, gun, data
        if len(message) < length_field + 25: # 报文实际长度小于长度域+其他部分长度的值
            status = 4
            return status, ver, cmd, id, gun, data
        if len(message) > length_field + 25: # 报文实际长度大于长度域+其他部分长度的值
            message = message[:length_field + 25]    # 截断报文
        format_string = '>HBB13sBBHH{0}sH'.format(length_field)
        protocol_struct = struct.Struct(format_string)
        unpacked_message = protocol_struct.unpack(message)
        ver = unpacked_message[1]
        cmd = unpacked_message[2]
        id = unpacked_message[3]
        gun = unpacked_message[4]
        check_sum = unpacked_message[5]
        data_len_append = unpacked_message[6]
        data_len_enc = unpacked_message[7]
        data = unpacked_message[8]
        end = unpacked_message[9]
        if check_sum != self.__calc_check_sum(data):   # 校验和不对
            status = 5
            return status, ver, cmd, id, gun, data
        data_buf = ctypes.create_string_buffer(data, len(data))         # 创建数据缓冲区
        self.tea_lib.btea_decrpyt(data_buf, self.tea_key, len(data))    # 将缓冲区中的数据解密
        if data_len_append > 0:
            if data_len_append > 7:
                status = 6
                return status, ver, cmd, id, gun, data
            else:
                data = data_buf.raw[:data_len_enc - data_len_append]
        if end != self.end:
            status = 7
        return status, ver, cmd, id, gun, data
    
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
        elif status == 6:
            info = '补位长度过长'
        elif status == 7:
            info = '报文结束域不对'
        return info


def unpack_msg_print(protocol, packed_message):
    print('msg:' + packed_message.hex(' '))
    status, ver, cmd, id, gun, data = protocol.unpack(packed_message)
    print('status: ' + Protocol_byd.unpack_status_info(status))
    print('ver: ' + str(ver))
    print('cmd: ' + str(cmd))
    print('id: ' + str(id))
    print('gun: ' + str(gun))
    print('data: ' + data.hex(' '))

def protocol_test():
    ver = 10
    cmd = 102
    id = b'A00000000001'
    gun = 1
    data = b'\x04\x00'

    test_protocol = Protocol_byd()

    print('******<1>*******')
    print('data field: ' + data.hex(' '))
    print('data len: ' + str(len(data)))
    packed_message = test_protocol.pack(ver, cmd, id, gun, data)
    unpack_msg_print(test_protocol, packed_message)

    print('******<2>*******')
    cmd = 101
    data = b'\x19\x03\x27\x13\x59\x22\x03'

    print('data field: ' + data.hex(' '))
    print('data len: ' + str(len(data)))
    packed_message = test_protocol.pack(ver, cmd, id, gun, data)
    unpack_msg_print(test_protocol, packed_message)

    print('******<3>*******')
    packed_message += b'\x01'
    unpack_msg_print(test_protocol, packed_message)

    print('******<4>*******')
    packed_message = packed_message[0:len(packed_message) - 2]
    unpack_msg_print(test_protocol, packed_message)

    print('******<5>*******')
    cmd = 105
    data = b'\x31\x32\x33\x34\x35\x36\x37\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +\
        b'\x25\x01\x00\x00\x00\x00\x00\x00\x00\x00' +\
            b'\x00\x00\x00\x01' +\
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    print('data field: ' + data.hex(' '))
    print('data len: ' + str(len(data)))
    packed_message = test_protocol.pack(ver, cmd, id, gun, data)
    unpack_msg_print(test_protocol, packed_message)

if __name__ == '__main__':
    protocol_test()


