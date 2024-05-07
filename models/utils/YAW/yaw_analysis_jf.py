#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 风电机组偏航分析
# 功能描述：为实现发电量提升目标，对机组叶偏航控制性能进行分析、诊断
# ! 项目名称：【福建尖峰项目】
# ! 合并了风机功率数据
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

# ? 为了处理读入的CSV数据当中，发电机转速"1,147.00"转为浮点数类型
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


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
    # root_path = "C:/VSCode_space/Improvement/Jianfeng/scada"
    root_path = "C:/Users/QC/Desktop/产品/D-发电量提升/交付项目/福建尖峰项目/处理完的数据/"
    file_name_list = os.listdir(root_path)

    # 使用项目名称创建项目分析的文件目录 【项目文件夹】
    proj_name = "jf"
    proj_dir = create_proj_dir(proj_name, __file__)

    # 日志配置
    log_dir = 'logs'
    log_name = 'log'
    logger = get_mp_rotating_logger(log_dir=os.path.join(proj_dir, log_dir), log_name=log_name)

    for file_name in file_name_list:
        data = pd.read_csv(os.path.join(root_path, file_name), low_memory=False)  # , encoding="GB2312"
        data = data.drop_duplicates('时间')

        # *** ---------- 2 不同主机机型标签配置 ----------
        # 当前SCADA数据机组编号
        turbine_code = data.loc[0, "风机"]

        #
        logger.info("-------------------------------------------------------")
        logger.info("机组{}的偏航诊断分析：".format(turbine_code))

        # ** 2.1 主机基本信息准备 **
        # 风速和功率标签名称
        wind_speed_label = "平均风速(m/s)"
        # ! 没有功率数据，使用发电机替代
        # power_label = "平均发电机功率实时值(kW)"
        power_label = "平均功率"

        # ** 2.2 偏航对风偏差计算和字段配置 **
        # TODO: 数据同时提供'机舱对北角度'和'风向对北角度'，亦提供了偏航对风偏差角
        # data = yaw_deviation_calc(data, "平均风角度（对北）", "平均机舱角度")
        data.rename(columns={"平均风向（机舱）": yaw_deviation_label}, inplace=True)
        data = data_cut_proc(data, wind_speed_label)

        # *** ---------- 3 数据预处理 ----------
        data.loc[:, wind_speed_label] = data.loc[:, wind_speed_label].astype("float")
        # data.loc[:, "generator_speed"] = data.loc[:, "generator_speed"].astype("float")
        data.loc[:, power_label] = data.loc[:, power_label].apply(lambda x: locale.atof(x))

        # ? 不同的处理模式：模式一
        # ? 参考论文: 2020_风力发电机组对风偏差检测算法研究与应用_李闯
        # *** ---------- 4 分箱进行偏航性能诊断分析 ----------
        # ! 如果有空气密度数据，这里应该乘以考虑空气密度系数
        air_density_label = "平均空气密度"
        dev_angle = yaw_misalignment_proc(data, wind_speed_label, power_label,
                                          turbine_code, proj_dir, air_density_label)
        energy_loss = energy_loss_calc(dev_angle)
        logger.info("偏航对风偏差造成的发电量损失：{}".format(energy_loss))

        '''
        #? 不同的处理模式：模式二
        #? 参考论文: 2019_基于风机运行数据的偏航误差分析与校正
        # *** ---------- 5 分箱进行偏航性能诊断分析 ----------
        cap_data, count_data = yaw_bin_analysis(data, wind_speed_label, power_label)

        # *** ---------- 6 偏航分析统计结果导出 ----------
        cap_data.to_excel(r"./output/turbine{}出力.xlsx".format(turbine_code),encoding="gbk")
        count_data.to_excel(r"./output/turbine{}容量.xlsx".format(turbine_code), encoding="gbk")
        '''


if __name__ == "__main__":
    main()
