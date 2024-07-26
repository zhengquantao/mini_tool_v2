import os
from multiprocessing import freeze_support, Process
from common.common import daemon_app, is_program_running


def gui_server():
    from server.gui_server import run_gui
    run_gui()


def file_server():
    from server.file_server import run_file
    run_file()


def main():
    is_program_running()
    Process(target=gui_server).start()
    web = Process(target=file_server)
    web.start()
    daemon_app(web, ppid=os.getpid())


if __name__ == "__main__":
    freeze_support()
    main()
