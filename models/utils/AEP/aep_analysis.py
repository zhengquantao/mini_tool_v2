#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 基于实际和理论功率曲线的AEP分析
# 功能描述：为实现发电量提升目标，基于实际和理论功率曲线进行发电量分析
# ! 项目名称：【福建尖峰项目】
#
# 数据预处理、数据清洗、诊断分析、结果导出
# > 1. 数据预处理
# > 2. 数据清洗
# > 3. 发电量对比计算【实际和理论功率曲线】
# > 4. 结果导出
# --------------
#
# 输入Input：
# 输出Output：
#
# 其它模块、文件关系：
#
# 备注:
# ~~~~~~~~~~~~~~~~~~~~~~
#
# <--------------------------------------------------------------------


# --------------------------------------------------------------------
# ***
# 加载包 (import package)
# ***
# --------------------------------------------------------------------
import os
# ? 为了处理读入的CSV数据当中，发电机转速"1,147.00"转为浮点数类型
import locale
import shutil

import pandas as pd

from ..data_integration import extra_data

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from .wind_base_tool import wind_speed_binning
from .power_curve_tool import calc_actual_power_curve, scatter_curve
from .aep_tool import aep_calc
from .log_util import get_mp_rotating_logger
from ..data_cleansing import *


# --------------------------------------------------------------------
#
# main function
#
# --------------------------------------------------------------------
def aep_main(file_path, real_time, wind_col, dirction_col, temperature_col, airdensity_col, target_columns,
             curve_line_path, result_path, img_path, confidence_num, logger, farm_name):
    """

    Parameters
    ----------
    file_path scada files path
    wind_col  : speed label
    dirction_col :   dirction label
    temperature_col : temperature label
    airdensity_col  : airdensity label
    target_columns  : power label
    curve_line :power_line file path
    root_dir : root path
    Returns
    -------

    """

    # *** ---------- 1 基础设置和参数初始化 ----------

    scada_files = os.listdir(file_path)

    # # 平均空气密度
    # avg_air_density = 1.0496
    #
    # # 叶轮直径
    # rotor_diameter = 104
    #
    # # 机组装机容量
    # power_cap = 2000
    #
    # # 额定风速
    # rated_wind_speed = 10
    #
    # # 切入风速
    # cut_in_wind_speed = 3
    #
    # # 切出风速
    # cut_out_wind_speed = 20
    #
    # # 最小发电机转速：【并网转速】
    # min_generator_speed = 1000
    #
    # # 传动比：gear ratio，transmission ratio，drive ratio
    # gear_ratio = 131.58
    #
    # # 使用项目名称创建项目分析的文件目录 【项目文件夹】
    # proj_name = "aep_analysis"
    # proj_dir = create_proj_dir(proj_name, __file__)
    # power_curve_dir = create_dir("curve_img", proj_dir)

    # *** ---------- 2 按SCADA文件进行分析处理 ----------
    all_statistics = pd.DataFrame()
    for scada_file in scada_files:
        try:
            # *** ---------- 3 数据提取 ----------
            # ** 3.1 CSV数据读取 **
            # SCADA数据文件夹
            turbine_code = scada_file.split(".csv")[0]
            data = pd.read_csv(os.path.join(file_path, scada_file)).fillna(1)  # , encoding="GB2312"

            # 当前SCADA数据机组编号           # turbine_code = data.loc[0, "风机"]

            # ** 3.2 运行模式数据提取 **
            # 提取正常运行的数据，并只提取相关标签，并限制风速、功率的标签为speed和power
            # ! "运行模式" == 20: 并网模式的数据
            # ? 没有运行模式数据
            # data = data[data["平均机组运行模式"] == 20].reset_index(drop=True)

            # ** 3.3 字段名称转换 **
            # ! 没有发电机功率： "平均发电机功率实时值(kW)",
            table = []
            data = data[real_time + wind_col + dirction_col + temperature_col + airdensity_col + target_columns]
            # "power",
            if len(real_time) != 0:
                table.append("real_time")
            if len(wind_col) != 0:
                table.append("wind_speed")
            if len(dirction_col) != 0:
                table.append("wind_direction")
            if len(temperature_col) != 0:
                table.append("OutdoorTemperature")
            if len(airdensity_col) != 0:
                table.append("air_density")
            if len(target_columns) != 0:
                table.append("power")

            data.columns = table
            data["real_time"] = pd.to_datetime(data["real_time"])
            data = data.sort_values(by="real_time")
            # ** 3.4 数值类型转换 **
            ### np.issubdtype  or pandas.api.types.****
            for col in data.columns:
                if np.issubdtype(data[col], np.float) or np.issubdtype(data[col], np.int):
                    data.loc[:, col] = data.loc[:, col].astype("float")

            # data.loc[:, "power"] = data.loc[:, "power"].apply(lambda x: locale.atof(x))
            # data.loc[:, "generator_speed"] = data.loc[:, "generator_speed"].astype("float")
            # data.loc[:, "generator_speed"] = data.loc[:, "generator_speed"].apply(lambda x: locale.atof(x))

            if len(airdensity_col) != 0:
                if airdensity_col[0] in data.columns:
                    # ** 3.5 风速换算：当地实际空气密度 到 标密 **
                    data = data[data[airdensity_col] >= 0.7]
                    # ? 根据实时的空气密度进行标准空气密度风速换算
                    data[wind_col] = data.apply(lambda row: row[wind_col] /
                                                            pow((row[airdensity_col] / 1.225), 1 / 3), axis=1)

                    # ** 3.6 空气密度分类：用于叶尖速比和空气密度关系分析 **
                    air_density_list = data.loc[:, "air_density"].apply(lambda x: round(x, 2))
                    data.insert(len(data.columns), "air_density_x", air_density_list)

            #
            logger.info("-------------------------------------------------------")
            logger.info("开始处理机组{}的数据".format(turbine_code))

            # *** ---------- 4 数据预处理和异常值清洗 ----------

            # TODO: 修改添加了功率数据

            ##将风速分仓
            norm_data_2, speed_list = wind_speed_binning(data, "generator_speed", logger=logger)

            ## 使用拟合功率曲线+置信区间进行数据清洗
            norm_data, clean_percentage = confidence_interval(norm_data_2, confidence_num, ["wind_speed"], ["power"],
                                                              logger=logger, plot_name=turbine_code[-3:], plot_flag=1)
            if clean_percentage > 0.3:
                if os.path.exists(os.path.join("E:\scy\能效评估数据\hlh\old_data\异常风机-采样平均值", scada_file)):
                    os.remove(os.path.join(file_path, scada_file))
                shutil.move(os.path.join(file_path, scada_file), "E:\scy\能效评估数据\hlh\old_data\异常风机-采样平均值")
            # *** ---------- 5 拟合实际功率曲线 ----------
            # 拟合实际功率曲线，将生成的实际功率曲线到表中

            # ? 分为[功率曲线拟合]和[求实际的平均值]两种方式

            # TODO: 可以根据项目实际选择项
            # ? 方式一：基于sigmoid函数的实际功率曲线拟合
            # popt, actual_curve = curve_fitting(norm_data, speed_list)

            # ? 方式二：基于分箱区间的平均值
            actual_curve = calc_actual_power_curve(norm_data, speed_list, logger)

            # *** ---------- 5 理论和实际功率曲线对比 ----------
            # 结合理论功率进行计算对比
            # data_dir = "C:/Users/QC/Desktop/产品/D-发电量提升/交付项目/福建尖峰项目/"
            if "csv" in curve_line_path:
                theory_curve = pd.read_csv(curve_line_path)
            elif "xls" in curve_line_path or "xlsx" in curve_line_path:
                theory_curve = pd.read_excel(curve_line_path)

            ## 处理功率曲线的函数
            theory_curve = extra_data(scada_file, theory_curve, farm_name)

            theory_curve.columns = ["wind_speed", "theory_power"]

            # ** 5.1 理论功率曲线数值提取  **
            # ! 考虑当地空气密度的换算
            # ? 注意拟合模式需要【二选一】
            # ? 如果不需要进行空气密度换算，则该步骤不需要
            # theory_curve = theory_curve_prep(theory_curve, speed_list)

            power_curve = pd.merge(theory_curve, actual_curve, left_on="wind_speed", right_on="wind_speed", how="inner")

            # ** 5.2 功率曲线绘制，并保存理论和实际功率曲线对比图片  **
            # curve_file_name = "{}.png".format(turbine_code)
            # curve_full_path = os.path.join(img_path, curve_file_name)
            # scatter_curve(norm_data_2, power_curve, turbine_code, curve_full_path)

            # *** ---------- 6 AEP计算 ----------
            statistics = aep_calc(norm_data_2, power_curve, turbine_code, clean_percentage)
            all_statistics = all_statistics.append(statistics).reset_index(drop=True)
            type_flie = scada_file.split(".")[1]

        except Exception as e:
            logger.error(e)
    # *** ---------- 7 结果数据导出 ----------

    all_statistics.index = all_statistics["turbine_code"].apply(lambda x: int(x[-3:]))
    all_statistics.to_excel(os.path.join(result_path, farm_name + "_aep_result.xlsx"))
    performance_ratio = all_statistics[["turbine_code", "performance_ratio"]]
    base_turbine = performance_ratio.sort_values(by="performance_ratio").iloc[int(len(performance_ratio) / 2), :][
        "turbine_code"]

    return base_turbine + "." + type_flie, all_statistics

# if __name__ == "__main__":
#     main()
