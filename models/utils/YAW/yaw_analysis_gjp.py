#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 风电机组偏航分析
# 功能描述：为实现发电量提升目标，对机组叶偏航控制性能进行分析、诊断
# ! 项目名称：【国电电力山西高家堡】
#
# 数据预处理、数据清洗、诊断分析、结果导出
# > 1. 数据预处理
# > 2. 数据清洗
# > 3. 诊断分析
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
import pandas as pd

from file_dir_tool import create_proj_dir, create_dir

from log_util import get_mp_rotating_logger

from yaw_tool import yaw_bin_analysis
from yaw_tool import yaw_deviation_calc, data_cut_proc, yaw_quant_reg
from yaw_tool import yaw_misalignment_calc1, yaw_misalignment_calc2
from yaw_tool import yaw_misalignment_proc, energy_loss_calc

from yaw_tool import yaw_deviation_label


# --------------------------------------------------------------------
#
# main function
#
# --------------------------------------------------------------------
def main():
    """
    主程序执行
    :return:
    """

    # *** ---------- 1 基础设置和参数初始化 ----------
    data = pd.read_csv(
        "C:/VSCode_space/Improvement/IEC_calculate/高家堡收资/高家堡202207-202307_分钟数据2023-07-17 15-48-20.csv",
        encoding="gbk")
    all_turbine_code = data["风机"].unique()

    # *** ---------- 2 数据提取 ----------
    # 提取正常运行的数据，并只提取相关标签，并限制风速、功率的标签为speed和power
    # ! "运行模式" == 20: 并网模式的数据
    data = data[data["平均机组运行模式"] == 20].reset_index(drop=True)
    data = data[["时间", "风机", "平均风速实时值(m/s)", "平均发电机功率实时值(kW)", "平均发电机转速实时值",
                 "平均变桨角度", "平均风向1秒平均值"]]

    wind_speed_label = "平均风速实时值(m/s)"
    power_label = "平均发电机功率实时值(kW)"

    # ! 该项目"平均风向1秒平均值"即为 '机舱对北角度'和'风向对北角度'的差异值 【偏航对风偏差角度】
    data.columns = ["real_time", "turbine_code", "wind_speed", "power", "generator_speed",
                    "pitch_angle", yaw_deviation_label]

    # *** ---------- 3 主机机型标签配置 ----------
    #
    # 风速和功率标签名称
    wind_speed_label = "wind_speed"
    power_label = "power"

    # 使用项目名称创建项目分析的文件目录 【项目文件夹】
    proj_name = "gjp"
    proj_dir = create_proj_dir(proj_name, __file__)

    # 日志配置
    log_dir = 'logs'
    log_name = 'log'
    logger = get_mp_rotating_logger(log_dir=os.path.join(proj_dir, log_dir), log_name=log_name)

    # *** ---------- 4 按风机进行分析处理 ----------
    for turbine_code in all_turbine_code:
        #
        logger.info("-------------------------------------------------------")
        logger.info("机组{}的偏航诊断分析：".format(turbine_code))

        # *** ---------- 4 数据预处理和异常值清洗 ----------
        # ** 4.1 基本信息准备 **
        turbine_data = data[data["turbine_code"] == turbine_code].reset_index(drop=True)

        # ** 4.2 偏航对风偏差计算和字段配置 **
        # turbine_data = yaw_deviation_calc(turbine_data, "grWindDirctionToNorth", "grNacellePositionToNorth")
        # turbine_data.rename(columns={"平均风向（机舱）": yaw_deviation_label}, inplace=True)
        turbine_data = data_cut_proc(turbine_data, wind_speed_label)

        # ? 不同的处理模式：模式一
        # ? 参考论文: 2020_风力发电机组对风偏差检测算法研究与应用_李闯
        # *** ---------- 5 分箱进行偏航性能诊断分析 ----------
        dev_angle = yaw_misalignment_proc(turbine_data, wind_speed_label, power_label,
                                          turbine_code, proj_dir)
        energy_loss = energy_loss_calc(dev_angle)
        logger.info("偏航对风偏差造成的发电量损失：{}".format(energy_loss))

        '''
        #? 不同的处理模式：模式二
        #? 参考论文: 2019_基于风机运行数据的偏航误差分析与校正
        # *** ---------- 6 分箱进行偏航性能诊断分析 ----------
        cap_data, count_data = yaw_bin_analysis(turbine_data, wind_speed_label, power_label)

        # *** ---------- 7 偏航分析统计结果导出 ----------
        cap_data.to_excel(r"./output/turbine{}出力.xlsx".format(turbine_code),encoding="gbk")
        count_data.to_excel(r"./output/turbine{}容量.xlsx".format(turbine_code), encoding="gbk")
        '''


if __name__ == "__main__":
    main()
