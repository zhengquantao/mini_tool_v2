import os


# 基础配置

output_path = os.environ.get("output_path", "./output")
tmp_output_path = os.environ.get("tmp_output_path", "./output")

libreoffice_python = os.environ.get("libreoffice_python")
libreoffice = os.environ.get("libreoffice")


img_type = [".jpg", ".png", ".jpeg", ".html"]

# STATUS
WAITING = 0  # 待开始
QUEUING = 1  # 排队中
IN_PROGRESS = 2  # 进行中
SUCCESS = 3  # 成功
FAILED = 4  # 失败
DELETE = 5  # 删除

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

