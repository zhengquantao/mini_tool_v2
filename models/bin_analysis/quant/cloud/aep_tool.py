#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 风电机组功率曲线分析
# 功能描述：绘制实际功率曲线，与理论功率曲线对比计算发电量偏差等
#! 整体思路：
#? 思路大概就是 拟合出 实际功率曲线，通过实际和理论功率曲线 以及 风速频率信息，计算最后的发电量偏差
#? 风速频率有两种： 基于瑞丽累积概率分布 或者基于实际风频分布
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
# import logging

import math
import numpy as np
import pandas as pd

#
from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, wind_speed_bin_label, mark_label

from models.bin_analysis.quant.cloud.power_curve_tool import actual_power_label, theory_power_label


# --------------------------------------------------------------------
# ***
# 日志和参数配置
# ***
# --------------------------------------------------------------------

# *** ---------- 日志 ----------
# logger
# logger = logging.getLogger()


# --------------------------------------------------------------------
# ***
# 计算发电量
# ***
# --------------------------------------------------------------------
def speed_cdf(wind_speed, speed_avg):
    """
    计算风速的瑞丽累积概率分布函数
    :param wind_speed: 风速
    :return: 风速对应的概率分布
    """

    cdf = 1 - math.exp(-math.pi/4*(wind_speed/speed_avg)**2)

    return cdf


def count_speed(data, speed_high, speed_low):
    """
    统计实际的风频概率
    :param data: 输入数据时序集
    :param speed_high: 风速曲线上限
    :param speed_low: 风速曲线下限
    :return:
    """

    # 计算风速区间的概率
    speed_prob = len(data[(data[wind_speed_label] < speed_high) & (data[wind_speed_label] >= speed_low)])/len(data)
    return speed_prob


def aep_calc(data, power_curve):
    """
    电量计算
    :param data: 输入数据时序集
    :param power_curve: 实际和理论功率曲线

    :return: 发电量统计分析相关的数据
    """

    # *** ---------- 1 取正常运行的数据，并对数据进行降采样，然后统计其风速的平均值 ----------
    # 从10min降为1H
    normal_data = data[data["label"] == 0].set_index("real_time")
    normal_data.index = pd.to_datetime(normal_data.index)
    normal_data = normal_data[[wind_speed_label, power_label]]
    normal_data = normal_data.resample("1H").mean()

    # *** ---------- 2 提取基本信息和计算对应的数据缺失量 ----------
    turbine_code = data.loc[0, "turbine_code"]
    all_length = len(normal_data)
    normal_data = normal_data.dropna().sort_index()
    miss_length = all_length - len(normal_data)
    power_hours = len(normal_data)
    
    # 开始和结束时刻
    start_time = normal_data.index[0]
    end_time = normal_data.index[-1]

    # 风速统计
    min_speed = normal_data[wind_speed_label].min()
    mean_speed = normal_data[wind_speed_label].mean()
    max_speed = normal_data[wind_speed_label].max()

    # 功率统计
    min_power = normal_data[power_label].min()
    mean_power = normal_data[power_label].mean()
    max_power = normal_data[power_label].max()

    # *** ---------- 3 计算发电量 ----------
    iec_power, pdf_power = 0, 0
    for i in range(1, len(power_curve)):
        # 风速区间的上下限：举例[3.25, 2.75]
        speed_high, speed_low = power_curve.loc[i, wind_speed_label], power_curve.loc[i - 1, wind_speed_label]
        #! 基于实际风频计算的风速概率
        speed_prob = count_speed(normal_data, speed_high, speed_low)
        iec_power_high, iec_power_low = power_curve.loc[i, actual_power_label], power_curve.loc[i-1, actual_power_label]
        pdf_power_high, pdf_power_low = power_curve.loc[i, theory_power_label], power_curve.loc[i-1, theory_power_label]
        
        #! 两种方式计算发电量差异：
        #TODO: 可以根据项目实际选择项
        #? 方式一： 基于瑞丽累积概率分布计算发电量差异
        # 根据风速的分布计算对应的发电量
        iec_power = iec_power + (speed_cdf(speed_high, mean_speed) 
                                 - speed_cdf(speed_low, mean_speed)) * (iec_power_high + iec_power_low) / 2
        pdf_power = pdf_power + (speed_cdf(speed_high, mean_speed) 
                                 - speed_cdf(speed_low, mean_speed)) * (pdf_power_high + pdf_power_low) / 2
        
        #? 方式二： 基于实际风频分布计算发电量差异
        # 根据实际的风速分布计算对应的发电量
        # iec_power = iec_power + speed_prob * (iec_power_high + iec_power_low) / 2
        # pdf_power = pdf_power + speed_prob * (pdf_power_high + pdf_power_low) / 2
    
    iec_power = int(iec_power * power_hours)/1000
    pdf_power = int(pdf_power * power_hours)/1000
    
    # 计算机组的性能比
    performance_ratio = (iec_power - pdf_power)/pdf_power * 100
    # logger.info("IEC_aep为{}，pdf_aep为{}，性能比为{}".format(iec_power, pdf_power, performance_ratio))

    # *** ---------- 4 将统计信息和相关的数据组合起来 ----------
    statistics = pd.DataFrame([turbine_code, miss_length, power_hours, 
                               round(min_speed, 2), round(mean_speed, 2), round(max_speed, 2), 
                               round(min_power, 2), round(mean_power, 2), round(max_power, 2), 
                               round(iec_power, 2), round(pdf_power, 2), round(performance_ratio, 2)]).T
    statistics.columns = ["turbine_code", "miss_length", "power_hours", 
                          "min_speed", "mean_speed", "max_speed", 
                          "min_power", "mean_power", "max_power", 
                          "iec_power(mWh)", "pdf_power(mWh)", "performance_ratio"]
    
    return statistics

