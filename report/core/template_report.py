import io
import os
import traceback
import typing as t
import datetime
import logging as logger

import requests
from docx import Document
from docxcompose.composer import Composer
from docxtpl import DocxTemplate, InlineImage, RichText
from docx.shared import Cm

from report.core.base_report import BaseReport
from report.bin.snapshot import make_png
from report.common.signals import after_template_rendered, before_render_template
from report.common.common import u_str, run_command

from report.common import constants as cs

FIELD_TYPE = {
    "image": "handle_image",
    "text": "handle_text",
}


class TemplateReport(BaseReport):

    def __init__(self, output_path=cs.output_path, tmp_output_path=cs.tmp_output_path, **kwargs):
        self.kwargs = kwargs
        self.output_path = output_path
        self.tmp_output_path = tmp_output_path
        self.IMG_TYPE = cs.img_type

    def convert_content(self, data: t.Any, document: Document = None) -> t.Any:
        if isinstance(data, str):
            data = self.build_image(document, data)
            return data

        elif isinstance(data, list):
            for i, item in enumerate(data):
                data[i] = self.convert_content(item, document)
            return data

        elif isinstance(data, dict):
            for key in data.keys():
                self.handle_field_type(document, data, key)
                data[key] = self.convert_content(data[key], document)
            return data

        else:
            return data

    def handle_field_type(self, document: Document, data: t.Dict[str, t.Any], key: str) -> None:
        if not isinstance(data[key], dict):
            return

        field_type = data[key].get("FT")
        if field_type and field_type in FIELD_TYPE:
            data[key] = getattr(self, FIELD_TYPE[field_type]).__call__(document, **data[key])

    def handle_text(self, document: Document, **kwargs) -> RichText:
        """
        构建自定义文本
        :param document:
        :param kwargs: {val: "你好", color="FF0000", bold=True}
        :return:
        """
        return RichText(kwargs.get("val"),
                        style=kwargs.get("style"),
                        color=kwargs.get("color"),
                        highlight=kwargs.get("highlight"),
                        size=kwargs.get("size"),
                        subscript=kwargs.get("subscript"),
                        superscript=kwargs.get("superscript"),
                        bold=kwargs.get("bold"),
                        italic=kwargs.get("italic"),
                        underline=kwargs.get("underline"),
                        strike=kwargs.get("strike"),
                        font=kwargs.get("font"),
                        url_id=kwargs.get("url_id"))

    def handle_image(self, document: Document, **kwargs) -> t.Union[str, InlineImage]:
        """
        构建自定义图片
        :param document:
        :param kwargs: {val: "https://img.com/s/a.png" | "/path/b.png", width=12, height=9}
        :return:
        """
        return self.build_image(document, kwargs.get("val"), width=kwargs.get("width"), height=kwargs.get("height"))

    def build_image(self, document: Document, data: str, width=None, height=None) -> t.Union[str, InlineImage]:
        if self.is_image(data):
            if data.startswith("http") or data.startswith("https"):
                data = self.download(data)
                if not data:
                    return data
            elif data.endswith(".html"):
                data = make_png(data, "png")
            width = Cm(float(width)) if width else Cm(13)
            height = Cm(float(height)) if height else None
            data = InlineImage(document, data, width=width, height=height)
        return data

    def download(self, url: str) -> t.Union[t.IO[bytes], str]:
        try:
            response = requests.get(url, headers=cs.HEADERS, timeout=4)
            if response.status_code != 200:
                raise ValueError("request url error")
            stream = response.content
            if not stream:
                raise ValueError("response content null")
            return io.BytesIO(stream)
        except Exception as e:
            logger.error(f"{url} download error err：{e}!")
            return ""

    def is_image(self, data: str) -> bool:
        for img in self.IMG_TYPE:
            if data.endswith(img):
                return True

        return False

    def write_document(self, data_list: t.List[t.Dict], pdf: bool = False, filename: str = "",
                       update_index: bool = True) -> t.Dict[str, str]:
        ret_dict = {}
        file_list = []
        try:
            for data in data_list:
                template_path = self.render_template(data["filename"], data["content"])
                file_list.append(template_path)

            docx_output_file = self.merge_file(file_list, filename)
            ret_dict["docx_output"] = docx_output_file

            if update_index:
                self.update_toc(docx_output_file)

            if pdf:
                self.convert_to_pdf(docx_output_file, ret_dict)

            self.upload_to_file_server(ret_dict)
        except Exception as e:
            logger.error(traceback.format_exc())
            ret_dict["error"] = str(e)

        finally:
            return ret_dict

    def upload_to_file_server(self, ret_dict):
        pass

    def update_toc(self, docx_output_file: str) -> None:
        convert_path = os.path.join(os.path.dirname(__file__), "converter.py")
        new_output_file = os.path.join(self.output_path, self.random_name())
        rt = run_command([cs.libreoffice_python, convert_path, docx_output_file, new_output_file, "docx"])
        if isinstance(rt, Exception):
            logger.error(f"update index err: {rt}")
            return

        if rt.returncode:
            logger.error(rt.stderr)
            return

        os.remove(docx_output_file)
        os.renames(new_output_file, docx_output_file)

    def convert_to_pdf(self, docx_output_file: str, ret_dict: t.Dict[str, str]) -> None:
        pdf_output_file = docx_output_file.replace(".docx", ".pdf")
        convert_path = os.path.join(os.path.dirname(__file__), "converter.py")
        rt = run_command([cs.libreoffice_python, convert_path, docx_output_file, pdf_output_file, "pdf"])
        if isinstance(rt, Exception):
            logger.error(f"convert pdf err: {rt}")
            return

        if rt.returncode:
            logger.error(rt.stderr)
            return

        ret_dict["pdf_output"] = pdf_output_file

    def merge_file(self, files: t.List[str], filename: str) -> t.Union[str, os.PathLike]:
        file_obj = Document(files[0])
        document = Composer(file_obj)

        for file in files[1:]:
            document.append(Document(file))

        file_name = filename or self.random_name()

        output_path = os.path.join(self.output_path, file_name)

        document.save(output_path)

        self.remove_file(files)

        return output_path

    def render_template(self, template_file: str, content: t.Dict[str, t.Any]) -> t.Union[str, os.PathLike]:
        if template_file.startswith("http://") or template_file.startswith("https://"):
            template_file = self.download(template_file)

        doc = DocxTemplate(template_file)

        new_content = self.convert_content(content, document=doc)

        doc.render(new_content, autoescape=True)
        tmp_file_path = os.path.join(self.tmp_output_path, self.random_name())
        doc.save(tmp_file_path)
        return tmp_file_path

    @staticmethod
    def remove_file(file_list: t.List[str]) -> None:
        for file in file_list:
            os.path.exists(file) and os.remove(file)

    @classmethod
    def random_name(cls, f_type: str = "docx") -> str:
        file_name = f"{datetime.datetime.now().strftime('%Y%m%d%H%M')}-{u_str()}.{f_type}"
        return file_name

    def run(self, data_list: t.List[t.Dict[str, t.Any]] = None, pdf=False, filename=None,
            update_index=True) -> t.Dict[str, str]:
        before_render_template.send((data_list, pdf, filename, update_index))
        res = self.write_document(data_list, pdf, filename, update_index)
        after_template_rendered.send((data_list, pdf, filename, update_index, res))
        return res


def get_turbine_kwargs():
    kwargs = [{
        "filename": f'D:\\project\\mini_tool_v2\\report\\bin\\能效评估报告模版.docx',
        "content": {
            "farmName": "测试风场",
            "author": "隔壁老王",
            "checker": "隔壁老张",
            "approver": "隔壁老曾",
            "createTime": "2024-07-19",
            "fanNum": "35",
            "fanModel": "明阳1.5",
            "startTime": "2023-12-01",
            "endTime": "2023-12-30",
            "energy_coeff_list": [[1, "30057016", "8.77%", "105.91%", "4875.67 kW/h", "5163.61 kW/h"],
                            [2, "30057008", "5.1%", "105.27%", "4917.98 kW/h", "5177.18 kW/h"],
                            [3, "30057009", "2.43%", "100.4%", "5662.24 kW/h", "5684.98 kW/h"],
                            [4, "30057010", "0.46%", "99.11%", "5879.4 kW/h", "5827.32 kW/h"],
                            [5, "30057015", "0.0%", "100.8%", "5051.81 kW/h", "5092.05 kW/h"],
                            [6, "30057014", "-2.18%", "98.05%", "5047.58 kW/h", "4949.25 kW/h"]
                            ],
            "yaw_list": [["30057015", "-0.0", {"val": "注意", "bg": "ffff00"}, "正常", "持续关注监测数据"],
                          ["30057009", "0.1", {"val": "故障", "bg": "ff0000"}, "正常", ""],
                          ["30057008", "-0.3", {"val": "注意", "bg": "ffff00"}, "正常", ""],
                         ["30057016", "0.3", {"val": "注意", "bg": "ffff00"}, "正常", ""],
                          ["30057010", "0.6", {"val": "故障", "bg": "ff0000"}, "异常", "误差过大"],
                          ["30057014", "-0.6", {"val": "注意", "bg": "ffff00"}, "正常", "电气故障"],
                          ],
            "turbine_detail_list": [{
                "farm_turbine_num": "测试风场30057015机组",
                "yaw_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057014-偏航对风分析-20240712151240.html",
                "yaw_desc": "正常",
                "torque_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057008-桨距角-功率分析-20240617134628.html",
                "torque_desc": "正常",
                "fault_status": True,
            }, {
                "farm_turbine_num": "测试风场30057009机组",
                "yaw_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057014-偏航对风分析-20240712151240.html",
                "yaw_desc": "正常",
                "torque_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057008-桨距角-功率分析-20240617134628.html",
                "torque_desc": "正常",
                "fault_status": True,
            }, {
                "farm_turbine_num": "测试风场30057008机组",
                "yaw_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057014-偏航对风分析-20240712151240.html",
                "yaw_desc": "正常",
                "torque_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057008-桨距角-功率分析-20240617134628.html",
                "torque_desc": "正常",
                "fault_status": True,
            }, {
                "farm_turbine_num": "测试风场30057016机组",
                "yaw_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057014-偏航对风分析-20240712151240.html",
                "yaw_desc": "正常",
                "torque_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057008-桨距角-功率分析-20240617134628.html",
                "torque_desc": "正常",
                "fault_status": True,
            }, {
                "farm_turbine_num": "测试风场30057010机组",
                "yaw_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057014-偏航对风分析-20240712151240.html",
                "yaw_desc": "正常",
                "torque_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057008-桨距角-功率分析-20240617134628.html",
                "torque_desc": "正常",
                "fault_status": True,
            }, {
                "farm_turbine_num": "测试风场30057014机组",
                "yaw_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057014-偏航对风分析-20240712151240.html",
                "yaw_desc": "正常",
                "torque_img": "C:\\Users\\EDY\\Desktop\\30057\\result\\30057008-桨距角-功率分析-20240617134628.html",
                "torque_desc": "正常",
                "fault_status": True,
            },
            ]}}
        ]
    return kwargs


if __name__ == '__main__':
    report_obj = TemplateReport()
    r = report_obj.run(get_turbine_kwargs(), pdf=False, filename='test.docx')
    print(r)
