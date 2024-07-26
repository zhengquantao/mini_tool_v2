import base64
import io
import logging
import os
import subprocess
import sys
from urllib.parse import quote

logger = logging.getLogger(__name__)

PHANTOMJS_EXEC = "phantomjs"


def make_snapshot(
    html_path: str, file_type: str, delay: int = 2, pixel_ratio: int = 1, width: int = 1000, height: int = 800, **_
):
    # chk_phantomjs()
    logger.info("Generating file ...")
    proc_params = [
        os.path.join(get_resource_dir(""), PHANTOMJS_EXEC),
        os.path.join(get_resource_dir(""), "snapshot.js"),
        to_file_uri(html_path),
        file_type,
        str(int(delay * 1000)),
        str(pixel_ratio),
        str(width),
        str(height),
    ]
    proc = subprocess.Popen(
        proc_params,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        # shell=True will make Windows happy.
        shell=get_shell_flag(),
    )
    content = io.TextIOWrapper(proc.stdout, encoding="utf-8").read()

    return content


def make_png(
    html_path: str, file_type: str, delay: int = 2, pixel_ratio: int = 1, width: int = 1000, height: int = 800, **_
):
    content = make_snapshot(html_path, file_type, delay, pixel_ratio, width, height, **_)
    return transform_content(content)


def transform_content(content: str) -> io.BytesIO:

    content_array = content.split(",")
    if len(content_array) != 2:
        raise OSError(content_array)

    image_stream = decode_base64(content_array[1])

    return io.BytesIO(image_stream)


def decode_base64(data: str) -> bytes:
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.
    """
    missing_padding = len(data) % 4
    if missing_padding != 0:
        data += "=" * (4 - missing_padding)
    return base64.decodebytes(data.encode("utf-8"))


def get_resource_dir(folder: str) -> str:
    current_path = os.path.dirname(__file__)
    resource_path = os.path.join(current_path, folder)
    return resource_path


def chk_phantomjs():
    try:
        phantomjs_version = subprocess.check_output(
            [PHANTOMJS_EXEC, "--version"], shell=get_shell_flag()
        )
        phantomjs_version = phantomjs_version.decode("utf-8")
        logger.info("phantomjs version: %s" % phantomjs_version)
    except Exception:
        logger.warning("No phantomjs found in your PATH. Please install it!")
        sys.exit(1)


def get_shell_flag() -> bool:
    return sys.platform == "win32"


def to_file_uri(file_name: str) -> str:
    __universal_file_name = file_name.replace("\\", "/")
    if ":" not in file_name:
        __universal_file_name = os.path.abspath(__universal_file_name)
    encode_text = quote(__universal_file_name)
    return "file:///{0}".format(encode_text)


if __name__ == '__main__':
    from pyecharts import options as opts
    from pyecharts.charts import Bar
    from pyecharts.render import make_snapshot

    from report.bin import snapshot


    def bar_chart() -> Bar:
        c = (
            Bar(init_opts=opts.InitOpts(bg_color="white"))
                .add_xaxis(["衬衫", "毛衣", "领带", "裤子", "风衣", "高跟鞋", "袜子"])
                .add_yaxis("商家A", [114, 55, 27, 101, 125, 27, 105])
                .add_yaxis("商家B", [57, 134, 137, 129, 145, 60, 49])
                .reversal_axis()
                .set_series_opts(label_opts=opts.LabelOpts(position="right"))
                .set_global_opts(title_opts=opts.TitleOpts(title="Bar-测试渲染图片"))
        )
        return c

    file_path = "C:\\Users\\EDY\\Desktop\\30057\\result\\30057014-偏航对风分析-20240712151240.html"
    make_snapshot(snapshot, file_path, "bar0.png")
