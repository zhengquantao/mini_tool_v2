
'''
coding:utf-8
@Software:PyCharm
@Time:2023/8/25 14:37
@Author: Natsu
'''
import os

from graph import dswe_chart
from models.utils.AEP import aep_analysis
from settings.settings import opening_dict, power_theoretical

"""

这里三个步骤，第一步选择特征，第二部获取IEC发电量相关信息并选取标杆风机，第三步获取性能对比的结果
选取特征使用遍历的方式循环进行，选取RMSE最小的组合,目前由于点位不足，步骤暂时不做。
IEC计算最后返回一个标杆风机

"""

# #IEC代码


def iec_main(file_path, real_time=["real_time"], wind_col=["wind_speed"], dirction_col=["wind_dirction"],
             temperature_col=["nacelle_temperture"], airdensity_col=["air_density"],
             target_columns=["power"], confidence_num=0.8,):

    factor_path = opening_dict[os.getpid()]["path"]
    factor_name = factor_path.split(os.sep)[-1]
    curve_line_path = os.path.join(factor_path, power_theoretical)
    turbine_code = file_path.split(os.sep)[-1].split(".")[0]

    _, all_statistics = aep_analysis.aep_main(file_path, factor_name, real_time, wind_col, dirction_col,
                                              temperature_col, [], target_columns, curve_line_path, confidence_num)
    file_paths, file_name = dswe_chart.build_html(factor_path, turbine_code, all_statistics)

    return file_paths, file_name

