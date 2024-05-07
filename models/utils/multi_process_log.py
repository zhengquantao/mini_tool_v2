#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 日志切分
# 功能描述：多线程日志切分管理
# --------------
#
# 为什么要切分日志？
#
# 将日志信息输出到一个单一的文件中，随着应用程序的持续使用，该日志文件会越来越庞大，进而影响系统的性能。
# 因此，有必要对日志文件按某种条件进行切分。切分日志使得日志更加可读且便于处理。
#
# 日志切割方法：
#
# 当一个日志文件达到触发条件后，对日志文件进行重命名，之后再新建原来名称的日志文件（此时就是空文件了），
# 新产生的日志就写入新的日志文件。
#
# 分割日志的触发条件：大小、日期，或者大小加上日期。
#
# 日志回滚：
# 当分割的日志文件达到指定数目的上限个数时，最老的日志文件就会被删除。日志回滚的目的是为了防止程序产生的
# 日志过多过大，在情况允许的条件下只保留最新的一些日志。
#
# logging库提供了2个可以用于日志滚动的class，一个是RotatingFileHandler，它主要是根据日志文件的大
# 小进行滚动；另一个是TimeRotatingFileHandler，它主要是根据时间进行滚动。
# 在实际应用中，通常根据时间进行滚动。
#
# 备注:
# 1. logging自带handler类TimedRotatingFileHandler 处理多线程时候存在问题 [PermissionError]
# 2. 基于时间间隔切分：TimedRotatingFileHandler类，
#    可以实现根据固定时间间隔（秒、分、小时、天、周等）的日志文件分割
#
# 3. 基于文件大小切分：RotatingFileHandler类
# ------
# handler = logging.handlers.RotatingFileHandler(
#     'log-size/test.log', maxBytes=100, backupCount=5)
# ------
# 4. BaseRotatingHandler: RotatingFileHandler类和TimedRotatingFileHandler类都是一种特例
# ~~~~~~~~~~~~~~~~~~~~~~
#
# <--------------------------------------------------------------------

# --------------------------------------------------------------------
# ***
# 加载包 (import package)
# ***
# --------------------------------------------------------------------

import os
import time
from datetime import datetime

import codecs
from logging.handlers import BaseRotatingHandler


# --------------------------------------------------------------------
# ***
# 多线程日志自动分割
# ***
# --------------------------------------------------------------------

class MultiProcessSafeRotatingFileHandler(BaseRotatingHandler):
    """
    Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported

    TimedRotatingFileHandler多线程冲突最简单直接的一种方法其实是：把多进程的 log handler
    配置改为一个 TimedRotatingFileHandler + N 个 FileHandler，这样就绕过了 多进程 这个
    环境，其余的进程只负责向 error.log 文件写。
    这需要实现进程间的不同配置，可以通过一个锁来实现，第一个成功 acquire 到这个锁的进程才能进行
    rollover操作。  ----> [实现困难和逻辑复杂]

    然而这存在一个切割不精确的问题，即在切割进程成功进行 rollover 之前，其他进程会把新日志写进
    旧文件。因此更好的办法是去修改 TimedRotatingFileHandler。
    改这个类的方法多种多样，本做法是抛弃文件重命名这个操作，将 rollover 的实现变为进程无冲的。
    方法为：写文件时始终向带日期后缀的文件写，然后做一个 error.log 的软链接，指向最新的一条日志。
    这样就抛弃了重命名的过程，行为和 FileHandler 更加类似。软连接的删除和新建也不存在进程间冲突。
    """

    def __init__(self, filename, suffix="%Y-%m-%d", encoding=None,
                 delay=False, utc=False, **kwargs):
        self.utc = utc
        self.suffix = suffix
        self.baseFilename = filename
        self.currentFileName = self._compute_fn()
        BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)

    def shouldRollover(self, record):
        if self.currentFileName != self._compute_fn():
            return True
        return False

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.currentFileName = self._compute_fn()

    def _compute_fn(self):
        """
        核心修改，判断是否需要对日志进行切分
        :return:
        """
        return self.baseFilename + "." + time.strftime(self.suffix, time.localtime())

    def _open(self):
        if self.encoding is None:
            stream = open(self.currentFileName, self.mode)
        else:
            stream = codecs.open(self.currentFileName, self.mode, self.encoding)

        # simulate file name structure of `logging.TimedRotatingFileHandler`
        if os.path.exists(self.baseFilename):
            try:
                os.remove(self.baseFilename)
            except OSError:
                pass

        try:
            os.symlink(self.currentFileName, self.baseFilename)
        except OSError:
            pass

        return stream


class MultiProcessSafeDailyRotatingFileHandler(MultiProcessSafeRotatingFileHandler):
    """
    每日日志分割处理器
    """

    def __init__(self, filename, encoding=None, delay=False, utc=False, **kwargs):
        self.suffix = "%Y-%m-%d"
        MultiProcessSafeRotatingFileHandler.__init__(self, filename, self.suffix,
                                                     encoding, delay, utc)


class MidnightRotatingFileHandler(BaseRotatingHandler):
    """
    凌晨日志文件切分处理器
    """

    def __init__(self, filename):
        self.suffix = "%Y-%m-%d"
        self.date = datetime.date.today()
        super(BaseRotatingHandler, self).__init__(filename, mode='a', encoding=None, delay=0)

    def shouldRollover(self, record):
        return self.date != datetime.date.today()

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        self.date = datetime.date.today()

    def _open(self):
        filename = '%s.%s' % (self.baseFilename, self.date.strftime(self.suffix))

        if self.encoding is None:
            stream = open(filename, self.mode)
        else:
            stream = codecs.open(filename, self.mode, self.encoding)

        if os.path.exists(self.baseFilename):
            try:
                os.remove(self.baseFilename)
            except OSError:
                pass

        try:
            os.symlink(filename, self.baseFilename)
        except OSError:
            pass
        return stream
