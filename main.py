#!/usr/bin/python3
#coding=utf-8

import socketserver
import threading
from server import Handler
from manage import Manage
from logger import log
import request_cmd
import http_server
import sys

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8084
    socketserver.TCPServer.allow_reuse_address = True

    try:
        server = socketserver.ThreadingTCPServer((HOST, PORT), Handler)
        server.daemon_threads = True  #设置所有创建的线程都为Daemo线程
        server.request_queue_size = 10
    except Exception as e:
        log.error(e)
        sys.exit(-1)
    
    threading.Thread(target = server.serve_forever, name="server", daemon=True).start()
    log.critical('Server listening on address {}:{}'.format(HOST, PORT))
    Manage.start_check_connection()
    threading.Thread(target = http_server.run, name="http server", daemon=True).start()
    #http_server.run()
    log.critical('Server Running...')
    log.critical('Press Ctrl+C to stop server.')

    while True:
        try:
            cmd = input(">>>")
        except KeyboardInterrupt:
            server.shutdown() #告诉serve_forever循环停止。
            server.server_close()
            log.critical('Server stop')
            break

        if cmd.strip() == "quit":
            server.shutdown() #告诉serve_forever循环停止。
            server.server_close()
            log.critical('Server stop')
            break
        elif cmd.strip() == "thread":
            for e in threading.enumerate():
                print(e)
        elif cmd.strip() == "client":
            for e in Handler.clients:
                print(e)
        elif cmd.strip().startswith('close'):
            try:
                cmd, ip, port = cmd.strip().split()
                client_address = (ip, int(port))
                client = Handler.getclient(client_address)
                if client is None:
                    print('client {} not exist'.format(client_address))
                else:
                    client[2]() # asyn_close
                    log.critical('Close socket{} manually'.format(client_address))
            except Exception as e:
                print(e)
        elif cmd.strip().startswith('start charge'):
            try:
                cmd1, cmd2, id, gun_id = cmd.strip().split()
                status = request_cmd.request_start_charge(id, int(gun_id))
                if status == 0:
                    log.critical('Start charge {}:{} manually'.format(id, gun_id))
                else:
                    log.critical('Start charge {}:{} manually failed'.format(id, gun_id))
            except Exception as e:
                print(e)
        elif cmd.strip().startswith('stop charge'):
            try:
                cmd1, cmd2, id, gun_id = cmd.strip().split()
                status = request_cmd.request_stop_charge(id, int(gun_id))
                if status == 0:
                    log.critical('Stop charge {}:{} manually'.format(id, gun_id))
                else:
                    log.critical('Stop charge {}:{} manually failed'.format(id, gun_id))
            except Exception as e:
                print(e)
        elif cmd.strip().startswith('update para'):
            try:
                cmd1, cmd2, id = cmd.strip().split()
                status = request_cmd.request_update_accounting_strategy(id)
                status = request_cmd.request_update_QR_code(id)
                if status == 0:
                    log.critical('Update para {} manually'.format(id))
                else:
                    log.critical('Update para {} manually failed'.format(id))
            except Exception as e:
                print(e)
        elif cmd.strip().startswith('help'):
            print('quit                         结束运行服务器程序')
            print('thread                       查看正在运行的线程列表')
            print('client                       查看当前客户端列表')
            print('close <ip> <port>            关闭指定IP和端口的客户端连接')
            print('start charge <id> <gun id>   发送开始充电请求命令')
            print('stop charge <id> <gun id>    发送停止充电请求命令')
            print('update para <id> <gun id>    发送更新参数请求命令')
        else:
            print('Unsupported command, please input help')
            
