#!/usr/bin/python3
#coding=utf-8

import time

class TimeUtil:

    @staticmethod
    def BCD2str(bcd):
        if len(bcd) < 7:
            return bcd.hex()
        year = ((bcd[0] & 0xF0) >> 4) * 1000 + (bcd[0] & 0x0F) * 100 + ((bcd[1] & 0xF0) >> 4) * 10 + (bcd[1] & 0x0F)
        month = ((bcd[2] & 0xF0) >> 4) * 10 + (bcd[2] & 0x0F)
        day = ((bcd[3] & 0xF0) >> 4) * 10 + (bcd[3] & 0x0F)
        hour = ((bcd[4] & 0xF0) >> 4) * 10 + (bcd[4] & 0x0F)
        minute = ((bcd[5] & 0xF0) >> 4) * 10 + (bcd[5] & 0x0F)
        second = ((bcd[6] & 0xF0) >> 4) * 10 + (bcd[6] & 0x0F)
        str = "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second)
        return str

    @staticmethod
    def str2struct(str):
        return time.strptime(str, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def struct2BCD(struct_time):
        year = struct_time.tm_year
        bcd0 = (int(year / 1000) << 4) + int(year % 1000 / 100)
        year = year % 100
        bcd1 = (int(year / 10) << 4) + int(year % 10)
        mon = struct_time.tm_mon
        bcd2 = (int(mon / 10) << 4) + int(mon % 10)
        mday = struct_time.tm_mday
        bcd3 = (int(mday / 10) << 4) + int(mday % 10)
        hour = struct_time.tm_hour
        bcd4 = (int(hour / 10) << 4) + int(hour % 10)
        min = struct_time.tm_min
        bcd5 = (int(min / 10) << 4) + int(min % 10)
        sec = struct_time.tm_sec
        bcd6 = (int(sec / 10) << 4) + int(sec % 10)
        return bytearray([bcd0 & 0xFF, bcd1 & 0xFF, bcd2 & 0xFF, bcd3 & 0xFF, bcd4 & 0xFF, bcd5 & 0xFF, bcd6 & 0xFF, 0xFF])

    @staticmethod
    def localtimeBCD():
        localtime = time.localtime(time.time())
        return TimeUtil.struct2BCD(localtime)

class TimeUtil_Byd:

    @staticmethod
    def BCD2str(bcd):
        if len(bcd) < 7:
            return bcd.hex()
        year = ((bcd[0] & 0xF0) >> 4) * 10 + (bcd[0] & 0x0F)
        month = ((bcd[1] & 0xF0) >> 4) * 10 + (bcd[1] & 0x0F)
        day = ((bcd[2] & 0xF0) >> 4) * 10 + (bcd[2] & 0x0F)
        hour = ((bcd[3] & 0xF0) >> 4) * 10 + (bcd[3] & 0x0F)
        minute = ((bcd[4] & 0xF0) >> 4) * 10 + (bcd[4] & 0x0F)
        second = ((bcd[5] & 0xF0) >> 4) * 10 + (bcd[5] & 0x0F)
        week = ((bcd[6] & 0xF0) >> 4) * 10 + (bcd[6] & 0x0F)
        str = "{}-{}-{} {}:{}:{}".format(year, month, day, hour, minute, second)
        return str

    @staticmethod
    def str2struct(str):
        return time.strptime(str, "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def struct2BCD(struct_time):
        year = struct_time.tm_year % 100
        bcd0 = (int(year / 10) << 4) + int(year % 10)
        mon = struct_time.tm_mon
        bcd1 = (int(mon / 10) << 4) + int(mon % 10)
        mday = struct_time.tm_mday
        bcd2 = (int(mday / 10) << 4) + int(mday % 10)
        hour = struct_time.tm_hour
        bcd3 = (int(hour / 10) << 4) + int(hour % 10)
        min = struct_time.tm_min
        bcd4 = (int(min / 10) << 4) + int(min % 10)
        sec = struct_time.tm_sec
        bcd5 = (int(sec / 10) << 4) + int(sec % 10)
        week = struct_time.tm_wday
        bcd6 = (int(week / 10) << 4) + int(week % 10)
        return bytearray([bcd0 & 0xFF, bcd1 & 0xFF, bcd2 & 0xFF, bcd3 & 0xFF, bcd4 & 0xFF, bcd5 & 0xFF, bcd6 & 0xFF, 0xFF])

    @staticmethod
    def localtimeBCD():
        localtime = time.localtime(time.time())
        return TimeUtil_Byd.struct2BCD(localtime)

class IdUtil:
    @staticmethod
    def bytes2string(bytes):
        str = bytes.decode(errors = "ignore")
        str1 = str.split('\000', 1)
        return str1[0]

    @staticmethod
    def string2bytes(str):
        bytes = str.encode(errors = "ignore")
        return bytes + b'\x00'
    
    @staticmethod
    def BCDbytes2int(bytes):
        ret = 0
        for byte in bytes:
            for val in (byte >> 4, byte & 0xF):
                if val > 9:
                    return ret
                ret = ret * 10 + val
        return ret
    
    @staticmethod
    def int2BCDbytes(value):
        digits = []
        while value > 0:
            digits.append(value % 10)
            value = value // 10
        digits.reverse()
        if (len(digits) == 0):
            digits.append(0)
        if (len(digits) % 2 != 0):
            digits.append(0x0F)
        else:
            digits.append(0x0F)
            digits.append(0x0F)
        digits2 = []
        for i in range(0, len(digits), 2):
            digits2.append(((digits[i] & 0x0F) << 4) | (digits[i + 1] & 0x0F))
        return bytearray(digits2)




def utility_test():
    str_time = TimeUtil.BCD2str(b'\x20\x21\x09\x27\x13\x43\x38\xff')
    print(str_time)
    struct_time = TimeUtil.str2struct(str_time)
    print(struct_time)
    bcd = TimeUtil.struct2BCD(struct_time)
    print(bcd.hex())

    localtimeBCD = TimeUtil.localtimeBCD()
    print(localtimeBCD.hex())

    str = IdUtil.bytes2string(b'\x30\x31\x32\x00\x00\x00\x00\x00')
    print(str)
    bytes = IdUtil.string2bytes(str)
    print(bytes.hex())

    str = IdUtil.bytes2string(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    print(str)
    bytes = IdUtil.string2bytes(str)
    print(bytes.hex())

    print(IdUtil.BCDbytes2int(b'\x20\x21\x09\x27\x13\x43\x38\xff'))
    print(IdUtil.BCDbytes2int(b'\x20\x21\x09\x2a\x13\x43\x38\xff'))
    print(IdUtil.BCDbytes2int(b'\x20\x21\x09\xa7\x13\x43\x38\xff'))
    print(IdUtil.BCDbytes2int(b'\x00\x21\x09\xa7\x13\x43\x38\xff'))
    print(IdUtil.BCDbytes2int(b'\xA0\x21\x09\xa7\x13\x43\x38\xff'))
    print(IdUtil.BCDbytes2int(b'\x20\x21\x09\x27\x13\x43\x38'))
    print(IdUtil.BCDbytes2int(b'\x20\x21\x09\x27\x13\x43\x38\x00'))
    print('============================')
    print(IdUtil.int2BCDbytes(1234).hex())
    print(IdUtil.int2BCDbytes(123).hex())
    print(IdUtil.int2BCDbytes(1).hex())
    print(IdUtil.int2BCDbytes(0).hex())

if __name__ == '__main__':
    utility_test()