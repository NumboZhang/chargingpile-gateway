#!/usr/bin/python3
#coding=utf-8

import socketserver
import socket
import threading
import queue
import selectors
import frame
import frame_byd
from logger import log
from struct import Struct

# 用于唤醒socket所发送的标志字节
SOCK_SEND_FLAG = b"\x00"
SOCK_CLOSE_FLAG = b"\xFF"


class Handler(socketserver.BaseRequestHandler):
    lock = threading.Lock()
    clients = {}
    recv_timeout = 3 # recv_timeout秒内没有接收到后续数据则开始处理下一帧
    frame_head_struct = Struct('<HH')   # 帧头结构
    
    def setup(self):
        '''申请与客户端建立连接所需的资源'''
        super().setup()
        self.selector = selectors.DefaultSelector()
        self.send_queue = queue.Queue()          # Any data received by this queue will be sent
        self.rsock, self.ssock = socket.socketpair()  # Any data sent to ssock shows up on rsock
        self.event = threading.Event()
        self.func_tuple = (self.sender, self.asyn_send, self.asyn_close)
        with self.lock:
            self.clients[self.client_address] = (self.request, self.asyn_send, self.asyn_close)
        log.info('新加入了一个连接%s', self.client_address)

    def handle(self):
        '''与客户端建立连接后的通信过程'''
        super().handle()
        sock = self.request
        self.selector.register(sock, selectors.EVENT_READ)
        self.selector.register(self.rsock, selectors.EVENT_READ)
        
        while not self.event.is_set():
            recv_status = 0
            send_over_flag = 0
            ready_objects = self.selector.select()
            for key, _ in ready_objects:
                if key.fileobj is sock:     # 有数据要接收
                    recv_status, data = self.receiver(2, None) # 读取帧头
                    break
                else:                       # 有数据要发送或其他操作
                    mark = self.rsock.recv(1)  # Dump the ready mark
                    if mark == SOCK_SEND_FLAG: # 服务端想发送数据
                        if 0 == self.sender(self.send_queue.get()):   # Send the data
                            send_over_flag = 1
                        else:           # 发送出错
                            recv_status = 4
                    else:               # 服务端想断开连接
                        recv_status = 5

            if send_over_flag == 1: # 发送完数据
                continue
            if recv_status != 0: # 断开连接
                break

            if len(data) < 2: # 帧头不完整
                recv_status, temp_data = self.receiver(1, self.recv_timeout) # 继续读取帧头
                if (recv_status == 1) or (recv_status == 3): # 客户端断开连接
                    break
                elif recv_status == 2: # 接收超时
                    continue
                else:
                    data += temp_data
            
            frame_head = (data[0] & 0xFF) | ((data[1] & 0xFF) << 8)
            if frame_head == 0xF5AA:    # 小桔协议的帧头
                r = self.process_frame_body(frame_head)
                if r == 0:              # 客户端断开连接
                    break
            elif frame_head == 0xBBAA:  # 比亚迪协议的帧头
                r = self.process_frame_body_byd(frame_head)
                if r == 0:              # 客户端断开连接
                    break
            else:
                log.warning("Frame head(0x{:04X}) is wrong, continue recv".format(frame_head))
                continue
    
    def process_frame_body(self, frame_head):
        '''小桔协议的报文处理'''
        sock = self.request
        recv_status, data = self.receiver(2, self.recv_timeout) # 读取帧长度
        if (recv_status == 1) or (recv_status == 3): # 客户端断开连接
            return 0
        elif recv_status == 2: # 接收超时
            return 1
        if len(data) < 2: # 帧长度不完整
            recv_status, temp_data = self.receiver(1, self.recv_timeout) # 继续读取帧长度
            if (recv_status == 1) or (recv_status == 3): # 客户端断开连接
                return 0
            elif recv_status == 2: # 接收超时
                return 1
            else:
                data += temp_data
        frame_length = (data[0] & 0xFF) | ((data[1] & 0xFF) << 8)
        if (frame_length < 9) or (frame_length > 0x8000):
            log.warning("Frame length({}) is wrong, continue recv".format(frame_length))
            return 1
        
        length = frame_length - 4  # 帧后续内容的长度
        recv_length = 0
        recv_data = b''
        while recv_length < (frame_length - 4):
            recv_status, data = self.receiver(length, self.recv_timeout) # 读取帧后续内容
            if (recv_status == 1) or (recv_status == 3): # 客户端断开连接
                return 0
            elif recv_status == 2: # 接收超时
                return 1
            else:
                length -= len(data)
                recv_data += data
                recv_length += len(data)
        
        data = self.frame_head_struct.pack(frame_head, frame_length)
        data += recv_data
        log.debug('%s-->%s', self.client_address, data.hex())
        frame.parse_frame(sock, self.func_tuple, self.client_address, data)
        return 1

    def process_frame_body_byd(self, frame_head):
        '''比亚迪协议的报文处理'''
        sock = self.request
        length = 21     # 帧头后续内容到数据域之间的长度
        recv_length = 0
        recv_data = bytearray([frame_head & 0xFF, (frame_head & 0xFF00) >> 8])
        while recv_length < 21:
            recv_status, data = self.receiver(length, self.recv_timeout) # 读取帧后续内容
            if (recv_status == 1) or (recv_status == 3): # 客户端断开连接
                return 0
            elif recv_status == 2: # 接收超时
                return 1
            else:
                length -= len(data)
                recv_data += data
                recv_length += len(data)
        data_length = (recv_data[22] & 0xFF) | ((recv_data[21] & 0xFF) << 8)
        if (data_length < 8) or (data_length > 300):
            log.warning("Data length({}) is wrong, continue recv".format(data_length))
            return 1
        
        length = data_length + 2     # 数据域到帧末尾的长度
        recv_length = 0
        while recv_length < data_length + 2:
            recv_status, data = self.receiver(length, self.recv_timeout) # 读取帧后续内容
            if (recv_status == 1) or (recv_status == 3): # 客户端断开连接
                return 0
            elif recv_status == 2: # 接收超时
                return 1
            else:
                length -= len(data)
                recv_data += data
                recv_length += len(data)
        
        log.debug('%s-->%s', self.client_address, recv_data.hex())
        frame_byd.parse_frame(sock, self.func_tuple, self.client_address, recv_data)
        return 1

    def finish(self):
        '''客户端断开后的资源清理'''
        super().finish()
        self.event.set()
        with self.lock:
            if self.client_address in self.clients:
                self.clients.pop(self.client_address)
        self.request.close()
        self.rsock.close()
        self.ssock.close()
        self.selector.close()
        log.info('%s退出了', self.client_address)
    
    def receiver(self, size, timeout):
        '''从socket接收size字节的数据，timeout秒后超时'''
        status = 0
        sock = self.request
        data = b''
        timeout_backup = sock.timeout
        if timeout is not None:
            sock.settimeout(timeout)        # 设置socket通信超时时间
        try:
            data = sock.recv(size)
            if data == b"": # 客户端主动断开连接
                status = 1
        except socket.timeout as e:  # 如果接收超时会抛出socket.timeout异常
            status = 2
            log.warning('%s %s', self.client_address, e)
        except Exception as e:
            status = 3
            log.error('%s %s', self.client_address, e)
        if timeout is not None:
            sock.settimeout(timeout_backup) # 恢复socket通信超时时间
        return status, data
    
    def sender(self, data):
        '''立即发送数据'''
        status = 0
        try:
            log.debug('%s<--%s', self.client_address, data.hex())
            self.request.sendall(data)
        except socket.timeout as e:  # 如果发送超时会抛出socket.timeout异常
            log.warning('%s %s', self.client_address, e)
            status = 2
        except Exception as e:
            log.error('%s %s', self.client_address, e)
            status = 3
        return status

    def asyn_send(self, data):
        '''异步发送:将数据放入发送队列中'''
        self.send_queue.put(data)   # Put the data to send inside the queue
        if getattr(self.ssock, '_closed') == False:
            self.ssock.send(SOCK_SEND_FLAG)    # Trigger the main thread by sending data to ssock which goes to rsock
    
    def asyn_close(self):
        '''异步关闭socket'''
        if getattr(self.ssock, '_closed') == False:
            self.ssock.send(SOCK_CLOSE_FLAG)    # Trigger the main thread by sending data to ssock which goes to rsock
    
    @staticmethod
    def getclient(client_address):
        '''根据客户端地址获取客户端对象'''
        client = None
        with Handler.lock:
            if client_address in Handler.clients:
                client = Handler.clients[client_address]
        return client
        