#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# Consistency Factor Analysis of Power Curve for Wind Turbines
# Based on SCADA Data
# 功能描述：风电机组功率曲线一致性系数分析 【SCADA数据】
#
# -----------------------
# 1. 功率曲线一致性系数
# 所谓功率曲线就是以风速(Vi)为横坐标，以有功功率Pi为纵坐标的一系列规格化数据
# 对(Vi，Pi)所描述的特性曲线。在标准空气密度（ρ=1.225kg/m3）的条件下，风电机
# 组的输出功率与风速的关系曲线称风电机组的标准功率曲线。根据风力发电机组所处位
# 置风速和空气密度，观测机组输出功率与主机厂商提供的额定功率曲线进行比较，选取
# 切入风速和额定风速间以1m/s为步长的若干个取样点进行计算，可得出功率曲线一致性
# 系数。为保证数据的准确性，也可选取更小的风速步长。
#
#! 当机组功率特性一致性系数超过110%时，功率曲线已不能真实地反映机组运行性能，
#! 而机组功率特性一致性系数低于95%时，则严重影响风机发电效能。
# -----------------------
# 2. 功率曲线一致性系数离散率
# 理想状况下同风场同机型的机组运行数据得到的功率曲线应是一致的，功率曲线一致性
# 系数离散率（以下简称离散率）越大，说明同机型不同机组间功率曲线差异越大。
# 
#? 离散率=功率曲线一致性系数标准差/功率曲线一致性系数平均值
# 
# 离散率越大说明机组间功率曲线差异越大，离散率越小说明机组间功率曲线差异越小。
#
# -----------------------
# 3. 相对最小(大)极均差
# 由于功率曲线一致性系数高于110%的机组处于失真状态，不能简单地说一致性系数越高机
# 组性能就越好，所以功率曲线一致性系数只能作为综合治理的一般依据和目标。一般同风
# 场同机型不同机组运行数据得到的功率曲线理论上是一致的，所以在功率曲线分类时以同
# 风场同机型作为基础单位，利用功率曲线一致性系数离散率、相对最小极均差$I_{min}$
# 和相对最大极均差$I_{max}$三个参数来进行分类。
#
#? 相对最小极均差Imin=MIN{(极大值-平均值)/平均值)，(平均值-极小值/平均值)}，
#? 其结果越小说明与平均值最小偏差越小，反之越大。
#? 相对最大极均差Imax=MAX{(极大值-平均值)/平均值，(平均值-极小值/平均值)}，
#? 其结果越小说明与平均值最大偏差越小，反之越大。
#
# -----------------------
#
#! 一般同风场同机型不同机组运行数据得到的功率曲线理论上是一致的，所以在功率曲线分类
#! 时以同风场同机型作为基础单位，利用功率曲线一致性系数离散率、相对最小极均差$I_{min}$
#! 和相对最大极均差$I_{max}$三个参数来进行分类。
# ~~~~~~~~~~~~~~~~~~~~~~
#
# <--------------------------------------------------------------------

# --------------------------------------------------------------------
# ***
# 加载包 (import package)
# ***
# --------------------------------------------------------------------

import logging

import numpy as np
import pandas as pd

#
import warnings
warnings.filterwarnings("ignore")

# *** ---------- custom package ----------
from models.bin_analysis.quant.cloud.wind_base_tool import binning_proc, plot_save, cp_label
from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, wind_direction_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_speed_bin_label, gen_speed_bin_label, power_bin_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_direction_bin_label, air_density_bin_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, mark_label, turbine_code_label


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
# 功率曲线一致性系数分析
# ***
# --------------------------------------------------------------------

def consist_factor_calc(dataset, theory_curve_df, theory_power_label):
    """
    功率曲线一致性系数【对风速分仓】【理论功率曲线偏差】
    
    :param dataset (DataFrame): 时序数据集
    :param theory_curve_df (DataFrame): 标准功率曲线数据
    
    :return: (DataFrame) 功率曲线一致性系数数据
    """

    # *** ---------- 1. wind speed分仓binning ----------
    bin_size = 0.5
    wind_speed_bins = np.arange(0, np.ceil(dataset[wind_speed_label].max()), bin_size)
    wind_speed_labels = [x for x in wind_speed_bins[1:]]

    dataset[wind_speed_bin_label] = pd.cut(dataset[wind_speed_label], bins=wind_speed_bins, 
                                       labels=wind_speed_labels)
    
    # *** ---------- 2. 分仓binning拟合功率曲线 ----------
    power_mean, power_std = binning_proc(dataset, wind_speed_labels, wind_speed_bin_label, power_label,
                                         split_value=3, interpolate_method="linear", fill_value=0)
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    power_windspeed_bin_df = pd.DataFrame()
    power_windspeed_bin_df[wind_speed_label] = wind_speed_labels
    power_windspeed_bin_df[power_label] = power_mean
    power_windspeed_bin_df['{}_std'.format(power_label)] = power_std


    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    #? 功率曲线信息：包含实际和理论功率曲线两部分
    power_curve = pd.merge(theory_curve_df, power_windspeed_bin_df, left_on=wind_speed_label,
                           right_on=wind_speed_label, how="inner")
    
    # *** ---------- 5. 计算功率曲线一致性系数 ----------
    cf_label = "consist_factor"
    power_curve[cf_label] = power_curve.apply(lambda row: (row[power_label]-row[theory_power_label])/row[power_label], axis=1)
    consist_factor = (1 - power_curve[cf_label].sum()/power_curve[cf_label].count()) * 100

    return round(consist_factor, 4)


def variation_coef_calc(cf_list):
    """
    coefficient of variation for Consistency Factor
    功率曲线一致性系数离散率

    在概率论和统计学中，离散系数（coefficient of variation），是概率分布离散程度的
    一个归一化量度，其定义为标准差与平均值之比。
    
    :param cf_list (list): 功率曲线一致性系数列表
    
    :return: (float) 功率曲线一致性系数离散率
    """

    variation_coef = np.std(cf_list) / np.average(cf_list)
    
    return round(variation_coef, 4)


def relative_variation_coef_min(cf_list):
    """
    相对最小极均差Imin=MIN{(极大值-平均值)/平均值)，(平均值-极小值/平均值)}，
    其结果越小说明与平均值最小偏差越小，反之越大。
    
    :param cf_list (list): 功率曲线一致性系数列表
    
    :return: (float) 功率曲线一致性系数-相对最小极均差
    """

    avg = np.average(cf_list)
    relative_var_coef_min = np.min([(np.max(cf_list)-avg)/avg, (avg-np.min(cf_list))/avg])
    
    return round(relative_var_coef_min, 4)


def relative_variation_coef_max(cf_list):
    """
    相对最大极均差Imax=MAX{(极大值-平均值)/平均值，(平均值-极小值/平均值)}，
    其结果越小说明与平均值最大偏差越小，反之越大。
    
    :param cf_list (list): 功率曲线一致性系数列表
    
    :return: (float) 功率曲线一致性系数-相对最大极均差
    """

    avg = np.average(cf_list)
    relative_var_coef_max = np.max([(np.max(cf_list)-avg)/avg, (avg-np.min(cf_list))/avg])
    
    return round(relative_var_coef_max, 4)


