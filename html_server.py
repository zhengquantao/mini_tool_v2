import os
import http.server
import socketserver

DIRECTORY = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static", "js")
PORT = 38121


class SimpleHTTPRequestHandlerWithDirectory(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    # 重写这个防止服务打包后起不来
    def log_message(self, format, *args):
        pass


def run_server(port=PORT):
    # 创建并启动服务器
    try:
        with socketserver.TCPServer(("", port), SimpleHTTPRequestHandlerWithDirectory) as httpd:
            # print("Serving at port", port)
            httpd.serve_forever()
    except OSError as e:
        pass


if __name__ == '__main__':
    # import sys, os
    # if sys.stdout is None:
    #     sys.stdout = open(os.devnull, "w")
    # if sys.stderr is None:
    #     sys.stderr = open(os.devnull, "w")
    run_server()
