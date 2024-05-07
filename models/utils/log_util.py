#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 全生命周期健康度管理
# 功能描述：日志工具类
# --------------
#
# 输入Input：
# 输出Output：
#
# 其它模块、文件关系：
#
# 备注:
# ~~~~~~~~~~~~~~~~~~~~~~
#
# <--------------------------------------------------------------------

# --------------------------------------------------------------------
# ***
# 加载包 (import package)
# ***
# --------------------------------------------------------------------

import os
import sys

import time
import logging

from multi_process_log import MultiProcessSafeRotatingFileHandler

from logging.handlers import TimedRotatingFileHandler


# --------------------------------------------------------------------
# ***
# 日志配置
# ***
# --------------------------------------------------------------------


def get_mp_rotating_logger(log_dir='logs', log_name='log'):
    """
    进程安全的、基于时间后缀分割的日志切片实例

    :param log_dir: 日志文件夹
    :param log_name: 日志文件名称【前缀名称】

    :return: 日志实例
    """

    # 初始化日志实例
    logger = init_logger(log_dir)

    # *** ---------- 1 处理器 ----------
    # 进程安全的日志切分处理器
    multi_process_handler = MultiProcessSafeRotatingFileHandler(
        log_dir + os.sep + log_name,
        # suffix="%Y-%m-%d_%H-%M",
        suffix="%Y-%m-%d",
        encoding='utf-8'
    )

    # *** ---------- 2 格式化设置 ----------
    # 过滤级别：控制台输出INFO和WARNING级别，文件只记录WARNING级别
    # TODO: 切分关键点（核心逻辑依赖）
    # 设置后缀名称，跟"strftime"的格式一样: "%Y-%m-%d_%H-%M-%S.log"
    # 基于后缀模式判读日志文件是否需要切分
    # multi_process_handler.suffix = "%Y-%m-%d"
    # multi_process_handler.suffix = "%Y-%m-%d_%H-%M"

    # logging格式化设置
    log_fmt = logging.Formatter(fmt='%(levelname)s %(threadName)s %(asctime)s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    multi_process_handler.setFormatter(log_fmt)

    # logging handler management
    logger.addHandler(multi_process_handler)

    # *** ---------- 3 过滤级别 ----------
    # 过滤级别：控制台输出INFO和WARNING级别，文件只记录INFO级别
    info_filter = logging.Filter()
    info_filter.filter = lambda record: record.levelno == logging.INFO  # 设置过滤等级
    multi_process_handler.addFilter(info_filter)

    '''
    '''
    # ? 控制台输出
    err_filter = logging.Filter()
    err_filter.filter = lambda record: record.levelno == logging.error

    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(log_fmt)
    logger.addHandler(streamHandler)
    streamHandler.addFilter(err_filter)

    return logger


def get_timed_rotating_logger(name: str, log_dir="logs", log_name='log'):
    """
    基于时间分割的日志切片实例

    :param name: 日志实例名称
    :param log_dir: 日志文件夹
    :param log_name: 日志文件名称【前缀名称】
    
    :return: 日志实例
    """

    # 初始化日志实例
    logger = init_logger(log_dir)

    # 添加TimedRotatingFileHandler (一种File Handler)
    # 定义一个定期（一秒、一分钟、一小时、一天等）换一次log文件的handler
    # 保留一定数量（设置）个旧log文件
    time_file_handler = TimedRotatingFileHandler(
        log_dir + os.sep + log_name,
        encoding='utf-8',
        when='D',
        interval=1,
        backupCount=365
    )

    # 设置后缀名称，跟"strftime"的格式一样: "%Y-%m-%d_%H-%M-%S.log"
    # time_file_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
    time_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
    # time_file_handler.suffix = "%Y-%m-%d"

    # second
    # time_file_handler.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$"
    # day
    # time_file_handler.extMatch = r"^\d{4}-\d{2}-\d{2}.log$"
    # day
    # time_file_handler.extMatch = r"^\d{4}-\d{2}-\d{2}(\.\w+)?$"
    # minutes
    # time_file_handler.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}(\.\w+)?$"
    # time_file_handler.extMatch = re.compile(time_file_handler.extMatch)

    # logging格式化设置
    log_fmt = logging.Formatter(fmt='%(levelname)s %(threadName)s %(asctime)s %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    time_file_handler.setFormatter(log_fmt)

    # logging handler management
    logger.addHandler(time_file_handler)

    return logger


def init_logger(log_dir):
    """
    日志初始化、基本处理操作

    :param log_dir: 日志文件夹

    :return:日志实例
    """

    # 创建日志路径
    '''
    log_path = os.getcwd() + os.sep + log_dir
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    '''

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)

    # logging初始化工作：控制台日志输出
    logging.basicConfig()

    # logging initialization
    logger = logging.getLogger()

    # logging level
    logger.setLevel(logging.INFO)

    return logger


def get_logger_level(name: str, log_dir):
    """
    获取多级别日志

    :param name: 日志实例名称
    :param log_dir: 日志文件夹

    :return: 日志实例
    """

    logger = logging.getLogger(name)

    if os.path.exists(log_dir):
        pass
    else:
        os.mkdir(log_dir)

    # 设置日志基础级别
    logger.setLevel(logging.DEBUG)

    # 日志格式
    formatter = '%(asctime)s | %(levelname)s | %(thread)d | %(filename)s - %(funcName)s : %(message)s'

    log_formatter = logging.Formatter(formatter)

    # *** ---------- 1. 控制台日志 ----------
    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)

    # *** ---------- 2. info日志 ----------
    # info日志文件名
    info_file_name = 'info-' + time.strftime(
        '%Y-%m-%d', time.localtime(time.time())) + '.log'

    # info日志处理器
    # filename：日志文件名
    # when：日志文件按什么维度切分。'S'-秒；'M'-分钟；'H'-小时；'D'-天；'W'-周
    #       这里需要注意，如果选择 D-天，那么这个不是严格意义上的'天'，而是从你
    #       项目启动开始，过了24小时，才会从新创建一个新的日志文件，
    #       如果项目重启，这个时间就会重置。所以这里选择'MIDNIGHT'-是指过了午夜
    #       12点，就会创建新的日志。
    # interval：是指等待多少个单位 when 的时间后，Logger会自动重建文件。
    # backupCount：是保留日志个数。默认的0是不会自动删除掉日志。
    info_handler = TimedRotatingFileHandler(filename='logs/info/' +
                                                     info_file_name,
                                            when='MIDNIGHT',
                                            interval=1,
                                            backupCount=7,
                                            encoding='utf-8')
    info_handler.setFormatter(log_formatter)
    info_handler.setLevel(logging.INFO)

    # *** ---------- 3. error日志 ----------
    # error日志文件名
    error_file_name = 'error-' + time.strftime('%Y-%m-%d',
                                               time.localtime(time.time())) + '.log'
    # 错误日志处理器
    err_handler = TimedRotatingFileHandler(filename='logs/error/' +
                                                    error_file_name,
                                           when='MIDNIGHT',
                                           interval=1,
                                           backupCount=7,
                                           encoding='utf-8')
    err_handler.setFormatter(log_formatter)
    err_handler.setLevel(logging.ERROR)

    # 添加日志处理器
    logger.addHandler(info_handler)
    logger.addHandler(err_handler)
    logger.addHandler(console_handler)

    return logger
