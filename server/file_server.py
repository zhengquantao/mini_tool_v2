import os
import time
import http.server
import socketserver
from threading import Thread

import psutil

DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "static", "js")
PORT = 38121


class SimpleHTTPRequestHandlerWithDirectory(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    # 重写这个防止服务打包后起不来
    def log_message(self, format, *args):
        pass


def run_file(port=PORT):
    # 创建并启动服务器
    try:
        current_pid = os.getpid()
        with socketserver.TCPServer(("", port), SimpleHTTPRequestHandlerWithDirectory) as httpd:
            # print("Serving at port", port)
            Thread(target=daemon_app, args=(httpd, current_pid)).start()
            httpd.serve_forever()
    except OSError as e:
        pass


def daemon_app(app, ppid=None):
    current_process = psutil.Process(ppid).name()
    while process_cnt(current_process) > 1:
        time.sleep(3)

    app.shutdown()


def process_cnt(process_name):
    cnt = 0
    for proc in psutil.process_iter(['name']):
        if process_name in proc.info['name']:
            cnt += 1
    return cnt


if __name__ == '__main__':
    # import sys, os
    # if sys.stdout is None:
    #     sys.stdout = open(os.devnull, "w")
    # if sys.stderr is None:
    #     sys.stderr = open(os.devnull, "w")
    run_file()
