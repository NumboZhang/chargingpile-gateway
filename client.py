#!/usr/bin/python3
#coding=utf-8

class Client:

    def __init__(self, id, socket, client_address):
        self.id = id
        self.socket = socket
        self.client_address = client_address
        self.alive = 10 # 活跃度的初始值
        self.protocol_type = 0  # 通信协议类型,0为默认的小桔协议
        self.protocol_ver = 0x03 # 当前协议版本
        self.encrypt_en = 0 # 当前是否启用加密通信
        self.close_func = None
        self.send_func = None
    
    def set_socket(self, socket):
        self.socket = socket

    def get_socket(self):
        return self.socket

    def get_id(self):
        return self.id
    
    def get_client_address(self):
        return self.client_address

    def set_client_address(self, client_address):
        self.client_address = client_address

    def get_alive(self):
        return self.alive
    
    def update_alive(self):
        self.alive = self.alive + 1
    
    def clean_alive(self):
        self.alive = 0
    
    def set_protocol_type(self, protocol_type):
        self.protocol_type = protocol_type

    def get_protocol_type(self):
        return self.protocol_type
    
    def set_protocol_ver(self, protocol_ver):
        self.protocol_ver = protocol_ver

    def get_protocol_ver(self):
        return self.protocol_ver

    def set_encrypt_en(self, encrypt_en):
        self.encrypt_en = encrypt_en

    def get_encrypt_en(self):
        return self.encrypt_en

    def set_close_func(self, func):
        self.close_func = func
    
    def close(self):
        if self.close_func is not None:
            self.close_func()
    
    def set_send_func(self, func):
        self.send_func = func

    def send(self, data):
        if self.send_func is not None:
            self.send_func(data)

def client_test():
    client_dict = {}
    client1 = Client(b'0001', None, ('180.140.153.239', 17159))
    client_dict[client1.get_id()] = client1
    client2 = Client(b'0002', None, ('180.140.153.239', 17160))
    client_dict[client2.get_id()] = client2
    print(client_dict)

if __name__ == '__main__':
    client_test()