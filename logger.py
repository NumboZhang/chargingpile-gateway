#!/usr/bin/python3
#coding=utf-8

import logging
from logging import handlers
import os


class Logger:
    def __init__(self):

        #创建一个logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        #创建一个handler，用于写入日志文件
        log_path = Logger.__get_log_path('server.log')  #指定输出的日志文件名
        print('Log file path: {}'.format(log_path))
        #fh = logging.FileHandler(log_path, encoding = 'utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
        fh = handlers.TimedRotatingFileHandler(filename=log_path, when='H', backupCount=24, encoding='utf-8')  # 自动按时间分割日志文件
        fh.setLevel(logging.DEBUG)

        #创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(threadName)s %(funcName)s %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    @staticmethod
    def __get_log_path(log_filename):
        log_path = os.getcwd() + os.sep + 'logs' + os.sep
        # 如果不存在这个logs文件夹，就自动创建一个
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        log_path = log_path + log_filename
        return log_path
    
    def get_logger(self):
        """定义一个函数，回调logger实例"""
        return self.logger

    def set_log_level(self, index, level):
        """设置指定handler的日志的输出级别"""
        if index >= len(self.logger.handlers):
            return
        self.logger.handlers[index].setLevel(level)
    
    def get_log_level(self, index):
        """获取指定handler的日志的输出级别"""
        if index >= len(self.logger.handlers):
            return
        return self.logger.handlers[index].level
    
mylogger = Logger()
log = mylogger.get_logger()

def test_logger():
    log.debug('debug message')
    log.info('info message')
    log.warning('warning message')
    log.error('error message')
    log.critical('critical message')

if __name__ == '__main__':
    test_logger()