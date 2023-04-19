#!/usr/bin/python3
#coding=utf-8

from manage import Manage
from logger import mylogger
from logger import log
import request_cmd
import time
import os

from gevent import monkey
monkey.patch_all(socket=False, thread=False, select=False)  # 打上猴子补丁

from flask import Flask
from flask import request
from flask import json
from flask import abort
from flask import send_file
from flask import render_template


app = Flask(__name__)
start_time = time.localtime(time.time())

'''首页'''
@app.route('/')
def index():
    now_time = time.localtime(time.time())
    return render_template('index.html', \
        title='Welcome to Charging Point Gateway', \
        start_time=start_time, \
        now_time=now_time)

'''设置日志输出级别'''
@app.route('/logLevel', methods=['GET'])
def log_level():
    index = request.values.get('index')
    level = request.values.get('level')
    handle_level = {'0-File': mylogger.get_log_level(0), '1-Terminal': mylogger.get_log_level(1)}
    if ((index == None) or (level == None)):
        return render_template('log_level.html', title='Log Level', dict=handle_level)
    try:
        index = int(index)
        level = int(level)
    except:
        return render_template('log_level.html', title='Log Level', dict=handle_level, info='Set failed!')
    
    mylogger.set_log_level(index, level)
    handle_level = {'0-File': mylogger.get_log_level(0), '1-Terminal': mylogger.get_log_level(1)}
    return render_template('log_level.html', title='Log Level', dict=handle_level, info='Set success!')

'''日志文件列表'''
'''日志文件下载'''
@app.route('/logs/', defaults={'req_path': ''})
@app.route('/logs/<path:req_path>')
def dir_listing(req_path):
    # Joining the base and the requested path
    abs_path = os.getcwd() + os.sep + 'logs' + os.sep + req_path

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)
    
    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        try:
            file = send_file(abs_path)
            return file
        except Exception as e:
            app.logger.error('Send file error.' + ' ' + str(e))
            return abort(500)

    # Show directory contents
    try:
        files_name = os.listdir(abs_path)
        files_size = [os.path.getsize(abs_path + os.sep + file) for file in files_name]
        files = [(files_name[i], round(files_size[i]/1024, 2)) for i in range(len(files_name))]
        total_size = round(sum(files_size)/1024, 2)
        return render_template('files.html', title='Log File List', number=len(files), total_size=total_size, files=files)
    except Exception as e:
        app.logger.error('List dir error.' + ' ' + str(e))
        return abort(500)

'''客户端列表'''
@app.route('/clients', methods=['GET'])
def get_clients():
    info = request.values.get('disp')
    list = []
    clients_list = Manage.get_clients_list()
    if info == 'text':
        return render_template('clients.html', title='Client List', number=len(clients_list), clients=clients_list)
    else:
        for e in clients_list:
            dict = {'id': e.get_id(), 'addr': e.get_client_address(), 'alive' : e.get_alive()}
            list.append(dict)
        jsondata = json.jsonify(list)
        return jsondata

'''指定ID的客户端信息'''
@app.route('/client/<id>', methods=['GET'])
def get_client_info(id):
    jsondata = None
    client = Manage.get_client(id)
    if client != None:
        jsondata = json.jsonify({'id': client.get_id(), 'addr': client.get_client_address(), 'alive' : client.get_alive()})
    else:
        jsondata = json.jsonify({'id': id, 'addr': '', 'alive' : ''})
    return jsondata

'''关闭指定ID的客户端连接'''
@app.route('/client/<id>/close', methods=['GET'])
def close_client(id):
    jsondata = None
    client = Manage.get_client(id)
    if client != None:
        client.close()
        Manage.remove_client(id)
        result = 'ok'
    else:
        result = 'id not exist'
    
    jsondata = json.jsonify({'id': id, 'operate': 'close', 'result': result})
    return jsondata

'''指定ID的充电桩开始充电'''
@app.route('/client/<id>/start', methods=['GET'])
def start_charge(id):
    jsondata = None
    try:
        gun_id = request.values.get('gun_id')
        gun_id = int(gun_id)
    except:
        return json.jsonify({'id': id, 'operate': 'start', 'result': 'para error'})

    status = request_cmd.request_start_charge(id, gun_id)
    if status == 0:
        result = 'ok'
    elif status == 1:
        result = 'id not exist'
    elif status == 2:
        result = 'client not support'
    else:
        result = 'unknow error'
    
    jsondata = json.jsonify({'id': id, 'operate': 'start', 'gun_id': gun_id, 'result': result})
    return jsondata

'''指定ID的充电桩停止充电'''
@app.route('/client/<id>/stop', methods=['GET'])
def stop_charge(id):
    jsondata = None
    try:
        gun_id = request.values.get('gun_id')
        gun_id = int(gun_id)
    except:
        return json.jsonify({'id': id, 'operate': 'stop', 'result': 'para error'})

    status = request_cmd.request_stop_charge(id, gun_id)
    if status == 0:
        result = 'ok'
    elif status == 1:
        result = 'id not exist'
    elif status == 2:
        result = 'client not support'
    else:
        result = 'unknow error'
    
    jsondata = json.jsonify({'id': id, 'operate': 'stop', 'gun_id': gun_id, 'result': result})
    return jsondata

'''更新指定ID的充电桩的参数'''
@app.route('/client/<id>/update', methods=['GET'])
def update_para(id):
    jsondata = None
    try:
        type = request.values.get('type')
        type = int(type)
    except:
        return json.jsonify({'id': id, 'operate': 'update', 'result': 'para error'})

    if type == 1:   # 更新二维码
        status = request_cmd.request_update_QR_code(id)
    elif type == 2: # 更新计费策略
        status = request_cmd.request_update_accounting_strategy(id)
    else:
        return json.jsonify({'id': id, 'operate': 'update', 'result': 'para error'})

    if status == 0:
        result = 'ok'
    elif status == 1:
        result = 'id not exist'
    elif status == 2:
        result = 'client not support'
    else:
        result = 'unknow error'
    
    jsondata = json.jsonify({'id': id, 'operate': 'update', 'type': type, 'result': result})
    return jsondata


def run():
    HOST, PORT = "0.0.0.0", 8088
    app.logger.critical('Http server listening on address {}:{}'.format(HOST, PORT))
    #app.run(host=HOST, port=PORT, threaded=True, debug=True, use_reloader=False)
    #app.run(host=HOST, port=PORT, threaded=True)

    from gevent import pywsgi
    server = pywsgi.WSGIServer( (HOST, PORT ), app, log=log, error_log=log )
    server.serve_forever()
    

if __name__ == '__main__':
    run()