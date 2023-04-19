#!/usr/bin/python3
#coding=utf-8

import time
import threading
from client import Client
from logger import log

class Manage:

    lock = threading.Lock()
    clients_dict = {}
    alive_threshold = 2 # 客户端的alive值小于此门限，则认为该客户端已经失联
    check_connection_period = 60 * 2 # 检查连接有效性的时间周期(s)

    def __init__(self):
        pass

    @staticmethod
    def add_client(id, socket, client_address, send_func, close_func, protocol_type=0):
        client = None
        with Manage.lock:
            if id in Manage.clients_dict:
                client = Manage.clients_dict[id]
        if client is None:
            client = Client(id, socket, client_address)
            client.set_send_func(send_func)
            client.set_close_func(close_func)
            client.set_protocol_type(protocol_type)
            with Manage.lock:
                Manage.clients_dict[id] = client
        else:
            client.update_alive()
            if client.get_socket() != socket:
                log.info("[{}]关闭旧的socket{}".format(client.get_id(), client.get_client_address()))
                client.close()
                client.set_socket(socket)
                client.set_client_address(client_address)
                client.set_send_func(send_func)
                client.set_close_func(close_func)
                client.set_protocol_type(protocol_type)
                for i in range(Manage.alive_threshold * 2):
                    client.update_alive()
                
    @staticmethod
    def remove_client(id):
        client = None
        with Manage.lock:
            if id in Manage.clients_dict:
                client = Manage.clients_dict[id]
        if client is not None:
            with Manage.lock:
                Manage.clients_dict.pop(client.get_id())

    @staticmethod
    def get_client(id):
        client = None
        with Manage.lock:
            if id in Manage.clients_dict:
                client = Manage.clients_dict[id]
        return client

    @staticmethod
    def get_clients_list():
        with Manage.lock:
            clients_list = list(Manage.clients_dict.values())
        return clients_list
    
    @staticmethod
    def __check_connection():
        while True:
            time.sleep(Manage.check_connection_period)
            with Manage.lock:
                clients_list = list(Manage.clients_dict.values())
            if len(clients_list) > 0:
                log.info("开始检查{}个连接的活跃度,周期{}秒...".format(len(clients_list), Manage.check_connection_period))
            
            for client in clients_list:
                if client.get_alive() < Manage.alive_threshold:
                    log.info("[{}]关闭活跃度小于{}的连接{}".format(client.get_id(), Manage.alive_threshold, client.get_client_address()))
                    client.close()
                    with Manage.lock:
                        if client.get_id() in Manage.clients_dict:
                            Manage.clients_dict.pop(client.get_id())
                else:
                    client.clean_alive()
    
    @staticmethod
    def start_check_connection():
        threading.Thread(target = Manage.__check_connection, name="check_connection", daemon=True).start()


def manage_test():
    Manage.add_client(b'0001', None, ('180.140.153.239', 17159))
    Manage.add_client(b'0002', None, ('180.140.153.240', 17160))
    Manage.add_client(b'0003', None, ('180.140.153.241', 17161))
    print(Manage.get_client(b'0001').get_client_address())
    print(Manage.get_client(b'0002').get_client_address())
    print(Manage.get_client(b'0003').get_client_address())
    Manage.start_check_connection()

    while True:
        cmd = input(">>>")
        if cmd.strip() == "quit":
            break
        elif cmd.strip() == "thread":
            for e in threading.enumerate():
                print(e)

if __name__ == '__main__':
    manage_test()




