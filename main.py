from multiprocessing import freeze_support, Process
from common.common import is_program_running
from server.file_server import run_file
from server.gui_server import run_gui


def main():
    is_program_running()
    Process(target=run_gui).start()
    run_file()


if __name__ == "__main__":
    freeze_support()
    main()
