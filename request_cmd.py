#!/usr/bin/python3
#coding=utf-8

from protocol import Protocol
from manage import Manage
from logger import log
import frame
import frame_byd


def request_start_charge(id, gun_id):
    '''请求充电桩开始充电'''
    status = 0
    client = Manage.get_client(id)
    if client is None:
        status = 1
        log.warning('[{}]不存在'.format(id))
    else:
        log.info("[{}:{}]开始充电".format(id, gun_id))
        if client.get_protocol_type() == 0: # 小桔协议
            info = Protocol.pack_info_field(client.get_encrypt_en(), client.get_protocol_ver())
            f = frame.CMD7_start_charging_req(info, gun_id)
            client.send(f)
        elif client.get_protocol_type() == 1: # 比亚迪协议
            ver = 1
            f = frame_byd.CMD103_control_cmd_req(ver, id, gun_id, id2='', serial_number=0, cmd=1, unit_price=0, balance=0, total_price=0)
            client.send(f)
        else:
            status = 2
            log.warning('[{}]协议不支持'.format(id))
    return status


def request_stop_charge(id, gun_id):
    '''请求充电桩停止充电'''
    status = 0
    client = Manage.get_client(id)
    if client is None:
        status = 1
        log.warning('[{}]不存在'.format(id))
    else:
        log.info("[{}:{}]停止充电".format(id, gun_id))
        if client.get_protocol_type() == 0: # 小桔协议
            info = Protocol.pack_info_field(client.get_encrypt_en(), client.get_protocol_ver())
            f = frame.CMD5_control_cmd_req(info, gun_id, 2, 0x55)
            client.send(f)
        elif client.get_protocol_type() == 1: # 比亚迪协议
            ver = 1
            f = frame_byd.CMD103_control_cmd_req(ver, id, gun_id, id2='', serial_number=0, cmd=4, unit_price=0, balance=0, total_price=0)
            client.send(f)
        else:
            status = 2
            log.warning('[{}]协议不支持'.format(id))
    return status

def request_update_accounting_strategy(id):
    '''请求充电桩更新计费策略'''
    status = 0
    client = Manage.get_client(id)
    if client is None:
        status = 1
        log.warning('[{}]不存在'.format(id))
    else:
        if client.get_protocol_type() == 0: # 小桔协议
            log.info("[{}]更新计费策略".format(id))
            info = Protocol.pack_info_field(client.get_encrypt_en(), client.get_protocol_ver())
            f = frame.CMD9_update_para_req(info, id, 1, 1)
            client.send(f)
        else:
            status = 2
            log.warning('[{}]协议不支持'.format(id))
    return status

def request_update_QR_code(id):
    '''请求充电桩更新二维码'''
    status = 0
    client = Manage.get_client(id)
    if client is None:
        status = 1
        log.warning('[{}]不存在'.format(id))
    else:
        if client.get_protocol_type() == 0: # 小桔协议
            log.info("[{}]更新二维码".format(id))
            info = Protocol.pack_info_field(client.get_encrypt_en(), client.get_protocol_ver())
            f = frame.CMD9_update_para_req(info, id, 1, 3)
            client.send(f)
        else:
            status = 2
            log.warning('[{}]协议不支持'.format(id))
    return status