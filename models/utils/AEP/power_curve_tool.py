#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 风电机组功率曲线分析
# 功能描述：绘制实际功率曲线，与理论功率曲线对比计算发电量偏差等
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
import math
import numpy as np

import pandas as pd

import logging

import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit

#
from .wind_base_tool import cut_speed

#
from .wind_base_tool import power_label, wind_speed_label, generator_speed_label
from .wind_base_tool import air_density_label, wind_speed_bin_label, mark_label

# --------------------------------------------------------------------
# ***
# 日志和参数配置
# ***
# --------------------------------------------------------------------

# *** ---------- 日志 ----------
# logger
logger = logging.getLogger()

# --------------------------------------------------------------------
# ***
# 数据字段名称配置
# data field name [column name]
# ***
# --------------------------------------------------------------------

actual_power_label = "actual_power"
theory_power_label = "theory_power"


# --------------------------------------------------------------------
# ***
# 曲线拟合
# ***
# --------------------------------------------------------------------
def sigmoid(x, L, x0, k, b):
    """
    sigmoid函数拟合回归
    $ \sigma(x) = \frac{1}{1 + e^{-x}} $
    
    :param x:
    :param L: 曲线左右偏移
    :param x0:
    :param k:
    :param b: 曲线上下偏移

    :return: sigmoid函数公式
    """

    y = L / (1 + np.exp(-k * (x - x0))) + b

    return y


def curve_fitting(data, wind_speed_list):
    """
    使用sigmoid函数拟合功率曲线
    :param data: 输入数据时序集
    :param wind_speed_list: 风速分箱区间

    :return:
    popt - Optimal values for the parameters
    curve - 拟合的功率曲线数据点集合
    """

    try:
        data = data.reset_index(drop=True)
    except Exception as e:
        logger.info("无需执行此步骤！")

    # ? p0：函数参数的初始值，从而减少计算机的计算量
    p0 = [data[power_label].max(), data[wind_speed_label].mean(), 1, data[power_label].min()]

    # 基于sigmoid拟合功率曲线
    popt, pcov = curve_fit(sigmoid, data[wind_speed_label], data[power_label], p0, method="dogbox")

    # ! sigmoid拟合可能没有到达额定功率：到达额定风速以后，额定功率数值线偏下
    # ? sigmoid拟合修正：保证功率曲线到达额定功率数值线
    if sigmoid(20, *popt) > data[power_label].max():
        k = 1 + np.exp(-popt[2] * (20 - popt[1]))
        popt[0] = (data[power_label].max() - popt[3]) * k

    #
    curve = pd.DataFrame(wind_speed_list)
    curve[power_label] = pd.DataFrame(sigmoid(wind_speed_list, *popt))
    curve.columns = [wind_speed_label, actual_power_label]

    return popt, curve


def calc_actual_power_curve(data, speed_list, logger):
    """
    计算实际功率曲线数值点【计算每个分箱平均值】
    :param data: 输入数据时序集

    :return: 功率曲线数据点集合
    """

    # # *** ---------- 1 对风速划分区间 ----------
    # data, speed_list = cut_speed(data,logger)

    # *** ---------- 2 根据2个思路绘制实际功率曲线 ----------
    speed_data = data.groupby("groups")
    actual_power_df = pd.DataFrame()

    for index, subdata in speed_data:
        # ? 分箱区间点太少，不操作：功率曲线不考虑该部分数值
        if len(subdata) > 0.0001 * len(data):
            # 2.1 根据IEC按照风速分箱生成实际功率
            actual_power = subdata[power_label].mean()
            actual_power_curve = pd.DataFrame([index, actual_power]).T
            actual_power_curve.columns = [wind_speed_label, actual_power_label]
            actual_power_df = actual_power_df.append(actual_power_curve)

    # 2.2 最终的实际功率曲线数据
    actual_power_df = actual_power_df[actual_power_df[wind_speed_label] != -1].sort_values(
        wind_speed_label).reset_index(drop=True)

    return actual_power_df


def theory_curve_prep(data, speed_list, avg_air_density=None):
    """
    理论功率曲线处理
    :param data: 标准空气密度下的功率曲线
    :param speed_list: 风速分仓列表
    :param avg_air_density: 当地实际空气密度【年平均值】

    :return: 理论功率曲线数值点
    """

    # *** ---------- 1 空气密度风速转换 ----------
    data1, data2 = data.copy(), data.copy()

    # 空气密度转换：当地空气密度报标准空气密度的风速转换
    if avg_air_density is not None:
        data1[wind_speed_label] = data1[wind_speed_label].apply(lambda x: x / pow((avg_air_density / 1.225), 1 / 3))

    # data1[wind_speed_label] = data1[wind_speed_label] + 0.5

    # TODO: 理论功率曲线的两种生成方式
    # ! 二选一：基于直线拟合和基于sigmoid曲线的两种模式
    # *** ---------- 模式一：2 按照原本的风速采样点提取出功率数据 ----------
    # ! 直接对转换的理论功率曲线进行线性拟合（问题点：曲线不够平滑）
    # 取理论功率曲线
    data2[theory_power_label] = np.nan
    all_data = data1.append(data2).sort_values(wind_speed_label)

    # ! 线性拟合：直线拟合
    all_data = all_data.interpolate()
    # 去除空值
    all_data = all_data.fillna(method="bfill")

    # 由于空气密度转换，风速[wind_speed_label]数值变换，需要提取出[3, 3.5, 4......]以0.5为间隔的数据
    # "theory_power_temp"为临时标签点，进行指定风速点的功率曲线提取
    all_data.columns = [wind_speed_label, "theory_power_temp"]
    theory_curve = pd.merge(all_data, data, left_on=wind_speed_label,
                            right_on=wind_speed_label, how="inner")
    theory_curve = theory_curve[[wind_speed_label, "theory_power_temp"]]
    theory_curve.columns = [wind_speed_label, theory_power_label]

    # 将功率值转换为整数
    theory_curve[theory_power_label] = theory_curve[theory_power_label].astype("int32")

    # *** ---------- 模式二：3 按照sigmoid曲线拟合拟合功率数据 ----------
    '''
    #? 适用sigmoid曲线拟合回归
    data1 = data1.rename(columns={theory_power_label: power_label})
    popt, theory_curve = curve_fitting(data1, speed_list)
    theory_curve = theory_curve.rename(columns={actual_power_label: theory_power_label})
    '''

    # *** ---------- 4 功率数据微调，去除异常值 ----------
    # 理论功率效果过好，进行部分微调，主要是性能过好，将其调低
    # theory_curve[wind_speed_label] = theory_curve[wind_speed_label] + 0.5
    # theory_curve[theory_power_label] = theory_curve[theory_power_label] - 8
    theory_curve.loc[theory_curve[theory_power_label] < 0, theory_power_label] = 0
    theory_curve = theory_curve.reset_index(drop=True)

    return theory_curve


# --------------------------------------------------------------------
# ***
# 数据可视化
# ***
# --------------------------------------------------------------------
def scatter_two(data):
    """
    对数据进行可视化
    :param data: 输入数据时序集
    :return:
    """

    plt.figure()
    # ? hue="label": 标记异常数据与否
    sns.scatterplot(data=data, x=wind_speed_label, y=power_label, hue="label")
    plt.title("speed_power")
    plt.show()


def scatter_curve(data, curve, title, file_path):
    """
    绘制散点图和曲线
    :param data: 输入数据时序集
    :param curve: 理论和实际功率曲线数据
    :param title: 图像标题
    :return:
    """

    plt.figure()
    # ? hue="label": 标记异常数据与否
    # sns.scatterplot(data=data, x=wind_speed_label, y=power_label)
    plt.plot(curve[wind_speed_label], curve[actual_power_label],
             c="blue", label="actual_curve")
    plt.plot(curve[wind_speed_label], curve[theory_power_label],
             c="black", label="theory_curve")
    plt.legend()
    plt.title(title)

    # plt.show()
    plt.savefig(file_path)
