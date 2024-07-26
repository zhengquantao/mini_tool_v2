import os
import typing as t
import subprocess
import uuid


def create_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def run_command(args, background=False, input=None, capture_output=False, timeout=None, check=False, **kwargs):
    try:
        if background:
            r = subprocess.Popen(args,  **kwargs)
        else:
            r = subprocess.run(args, input=input, capture_output=capture_output, timeout=timeout, check=check, **kwargs)
        return r
    except Exception as e:
        return e


def u_str() -> str:
    # 生成UUID
    raw_uuid = str(uuid.uuid4())
    # 移除连字符
    cleaned_uuid = raw_uuid.replace("-", "")
    return cleaned_uuid


def read_file(filename: str) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


if __name__ == '__main__':
    pass
