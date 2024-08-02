import datetime
import os
import typing as t
from copy import deepcopy

import pandas as pd

from common.common import detect_encoding, random_name
from models.dswe_main import iec_main_export
from models.yaw_main import yaw_main_export
from report.core.template_report import TemplateReport
from settings.settings import ignore_files


def report_main(file_path, project_path, title=None):
    factor_name = project_path.split(os.sep)[-1]
    iec_table = iec_main_export(file_path, project_path)
    yaw_table, yaw_dict = yaw_main_export(file_path, project_path, title)
    start_time, end_time, cnt = get_time_and_count(file_path)
    build_report_dict = [{
        "filename": os.path.join(os.path.dirname(__file__), "bin", "能效评估报告模版.docx"),
        "content": {
            "farmName": factor_name,
            "author": "深圳量云",
            "checker": "深圳量云",
            "approver": "深圳量云",
            "createTime": datetime.datetime.now().strftime("%Y-%m-%d"),
            "fanNum": cnt,
            "fanModel": "明阳1.5",
            "startTime": start_time,
            "endTime": end_time,
            "energy_coeff_list": build_energy_coeff_list(iec_table),
            "yaw_list": build_yaw_list(yaw_table),
            "turbine_detail_list": build_turbine_detail(yaw_table, yaw_dict)}
    }]
    new_dict = deepcopy(build_report_dict)
    report_result = TemplateReport(
        output_path=os.path.join(project_path, "result"),
        tmp_output_path=os.path.join(project_path, "result"),
    ).run(build_report_dict, pdf=False, filename=random_name(factor_name, title, f_type="docx"), update_index=False)
    rm_file(new_dict)
    return report_result


def rm_file(data, file_type=".html"):
    if isinstance(data, str):
        if not data.endswith(file_type):
            return
        os.path.exists(data) and os.remove(data)
        return

    elif isinstance(data, list):
        for item in data:
            rm_file(item)
    elif isinstance(data, dict):
        for key in data:
            rm_file(data[key])
    else:
        return


def build_energy_coeff_list(energy_coeff_df) -> t.List[t.Any]:
    energy_coeff_df = energy_coeff_df.sort_values(by="Weighted_diff", ascending=False)
    energy_coeff_df = energy_coeff_df[["turbine_code", "Weighted_diff", "EBA_ratio", "pdf_power(mWh)", "iec_power(mWh)"]]
    # headers = ["排行", "风机号", "能效系数(%)", "能量可利用率(%)", "理论发电量(kw/h)", "实际发电量(kw/h)"]
    rows = [[idx] + row.tolist() for idx, row in enumerate(energy_coeff_df.values, start=1)]
    return rows


def build_yaw_list(yaw_list) -> t.List:
    yaw_list_copy = deepcopy(yaw_list)
    yaw_list_copy.sort(key=lambda item: abs(item[1]))
    map = {
        "注意": {"val": "注意", "bg": "ffff00"},
        "故障": {"val": "故障", "bg": "ff0000"},
        "告警": {"val": "告警", "bg": "ffc000"},
        "正常": {"val": "正常", "bg": ""},
    }
    for yaw in yaw_list_copy:
        # headers = ["排行", "风机号", "偏航对风误差", "偏航状态", "简单描述"]
        yaw[2] = map.get(yaw[2], {"val": "故障", "bg": ""})

    return yaw_list_copy


def build_turbine_detail(yaw_list, yaw_dict, ) -> t.List:
    ret_dict = {}
    for item in yaw_list:
        turbine_code = item[0]
        if turbine_code in ret_dict:
            continue

        ret_dict[turbine_code] = {
            "farm_turbine_num": f"{turbine_code}机组",
            "yaw_img": yaw_dict[turbine_code],
            "yaw_desc": item[3] or item[2],
            "torque_img": yaw_dict[turbine_code],
            "torque_desc": "正常",
            "fault_status": False,
        }
    return list(ret_dict.values())


def get_time_and_count(project_path) -> t.Tuple[str, str, int]:
    has_init = False
    start_time, end_time, cnt = "2023-12-01", "2023-12-30", 0
    for file in os.listdir(project_path):
        if file.endswith(".csv") and file not in ignore_files:
            cnt += 1
            if has_init:
                continue
            file_path = os.path.join(project_path, file)
            data_df = pd.read_csv(file_path, usecols=["real_time"], encoding=detect_encoding(file_path))
            start_time = data_df["real_time"].min()
            end_time = data_df["real_time"].max()
            has_init = True

    return start_time, end_time, cnt
