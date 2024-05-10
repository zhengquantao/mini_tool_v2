
'''
coding:utf-8
@Software:PyCharm
@Time:2023/8/25 14:37
@Author: Natsu
'''
import os

from graph import dswe_chart, power_sort_chart
from models.utils.AEP import aep_analysis
from settings.settings import opening_dict, power_theoretical
from common import loggers
"""

这里三个步骤，第一步选择特征，第二部获取IEC发电量相关信息并选取标杆风机，第三步获取性能对比的结果
选取特征使用遍历的方式循环进行，选取RMSE最小的组合,目前由于点位不足，步骤暂时不做。
IEC计算最后返回一个标杆风机

"""

# #IEC代码


def iec_main(file_path, sort_only=False):

    factor_path = opening_dict[os.getpid()]["path"]
    factor_name = factor_path.split(os.sep)[-1]
    curve_line_path = os.path.join(factor_path, power_theoretical)
    turbine_code = file_path.split(os.sep)[-1].split(".")[0]

    _, all_statistics = aep_analysis.aep_main(file_path, factor_name, ["real_time"], ["wind_speed"], ["wind_dirction"],
                                              ["nacelle_temperture"], [], ["power"], curve_line_path,  # ["air_density"]
                                              confidence_num=0.8, logger=loggers.logger)
    if sort_only:
        file_paths, file_name = power_sort_chart.build_html(factor_path, turbine_code, all_statistics)
        return file_paths, file_name

    file_paths, file_name = dswe_chart.build_html(factor_path, turbine_code, all_statistics)

    return file_paths, file_name

