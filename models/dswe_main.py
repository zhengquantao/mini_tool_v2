
'''
coding:utf-8
@Software:PyCharm
@Time:2023/8/25 14:37
@Author: Natsu
'''
import os

from graph import dswe_chart, power_sort_chart, table_chart
from models.utils.AEP import aep_analysis
from models.utils.Energy_compare import base_data_process
from settings.settings import power_theoretical
from common import loggers
"""

这里三个步骤，第一步选择特征，第二部获取IEC发电量相关信息并选取标杆风机，第三步获取性能对比的结果
选取特征使用遍历的方式循环进行，选取RMSE最小的组合,目前由于点位不足，步骤暂时不做。
IEC计算最后返回一个标杆风机

"""

# #IEC代码


def iec_main(file_path, project_path, sort_only=False, table=False):
    factor_name = project_path.split(os.sep)[-1]
    curve_line_path = os.path.join(project_path, power_theoretical)
    turbine_code = file_path.split(os.sep)[-1].split(".")[0]

    base_turbine, all_statistics = aep_analysis.aep_main(file_path, factor_name, ["real_time"], ["wind_speed"], ["wind_direction"],
                                              ["nacelle_temperature"], ["air_density"], ["power"], curve_line_path,  # ["air_density"]
                                              confidence_num=0.8, logger=loggers.logger)
    if sort_only:
        file_paths, file_name = power_sort_chart.build_html(project_path, turbine_code, all_statistics)
        return file_paths, file_name

    data_result = base_data_process(file_path, base_turbine, result_path=None,
                                    flag=1, feature_columns=["wind_speed", "wind_direction"], target_columns=["power"],
                                    wind_col=["wind_speed"], confidence=0.8, logger=loggers.logger,
                                    farm_name=factor_name)
    data_result = data_result[["turbine_code", "Weighted_diff"]].sort_values(by="turbine_code")
    all_statistics = all_statistics.sort_values(by="turbine_code")
    all_statistics["Weighted_diff"] = data_result["Weighted_diff"]
    all_statistics.fillna(0, inplace=True)

    if table:
        file_paths, file_name = dswe_chart.build_html(project_path, turbine_code, all_statistics)
        file_paths, file_name = table_chart.build_html(project_path, turbine_code, all_statistics)
    else:
        file_paths, file_name = table_chart.build_html(project_path, turbine_code, all_statistics)
        file_paths, file_name = dswe_chart.build_html(project_path, turbine_code, all_statistics)
    return file_paths, file_name

