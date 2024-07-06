#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# Power Curve Analysis for Wind Turbines
# 功能描述：风电机组功率曲线分析
#
# -----------------------
# 1. 功率曲线评估
# 功率曲线评估能够帮助相关人员通过散点图和拟合功率曲线、设计功率曲线，找出功率曲线之间的
# 差异、离散度以及优化空间。
#
# -----------------------
# 2. 风机BIN曲线对比分析
# 展示风机的各种BIN曲线（包括风速-功率曲线、风速-风能利用系数Cp曲线、风速-桨距角曲线、
# 桨距角-功率曲线、风速-转速曲线、转速-功率曲线），找到性能较差的风机，并可对风机的问题
# 开展诊断分析。提供不同的风场和不同的机型风机的BIN曲线对比分析功能，相关人员可对风机出
# 力不足（实际出力情况和额定的出力曲线相差大，预测功率和实际功率情况相差较大等情况）、风
# 机爬坡能力差（小风期风机运行正常，大风下爬坡能力差，故障频发的情况）、高负荷运行能力差
# （风机处于高负荷运行中，运行时间较长时，频繁启停机等情况）开展对比分析。 
#
# -----------------------
# 3. 风机BIN曲线趋势分析
# BIN趋势分析将各种BIN曲线随着时间的趋势变化展现给相关人员，能够帮助相关人员了解风机的性
# 能变化趋势，找出性能突变点。提供功率曲线月度对比图形，结合风资源情况的功率曲线量化方法。
# 相关人员可查看机组某年度的功率曲线月度对比情况。 
#
# -----------------------
# 4.多维交叉分析和自定义交叉分析
# 在实现基本的机组性能分析及诊断功能基础上，提供更加精细和更多维度的分析工具，如频率分布分
# 析、多位联动分析、变点分析等高级功能。对风机性能问题开展诊断分析工作。具体包括：
# 1) 频率分布分析，系统提供不同参数的频率分布展示与分析图。
# 2) 多维联动分析，系统提供交叉分析图形上散布点数据在时间轴上展开的功能，即实现散布图数据
# 和趋势图数据的联动。
# 3) 变点分析，通过寻找变位点的方法自动分析机组功率曲线发生变化的时间。
#
# ~~~~~~~~~~~~~~~~~~~~~~
#
# <--------------------------------------------------------------------

# --------------------------------------------------------------------
# ***
# 加载包 (import package)
# ***
# --------------------------------------------------------------------
import os
# import logging

import math
import numpy as np
import pandas as pd

from common.common import common_cut
from graph.bins_chart import build_html

#
import warnings
warnings.filterwarnings("ignore")

#
# from models.bin_analysis.quant.cloud.file_dir_tool import create_dir
# from models.bin_analysis.quant.cloud.plot_tool import curve_plot, bin_curve_plot, scatter_plot, hue_scatter_plot

from models.bin_analysis.quant.cloud.wind_base_tool import binning_proc, plot_save, cp_label
from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, wind_direction_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_speed_bin_label, gen_speed_bin_label, power_bin_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_direction_bin_label, air_density_bin_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, turbine_code_label

from models.bin_analysis.quant.cloud.power_curve_tool import calc_actual_power_curve

from models.bin_analysis.quant.cloud.pitch_analysis import pitch_label, pitch1_label, pitch2_label, pitch3_label, pitch_bin_label
from models.bin_analysis.quant.cloud.pitch_analysis import speed_pitch_plot_x, power_pitch_plot, pitch_power_plot_x

from models.bin_analysis.quant.cloud.tsr_tool import tsr_label, tsr_calc



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
# 数据字段名称配置
# data field name [column name]
# ***
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# ***
# 曲线分仓分析
# ***
# --------------------------------------------------------------------

def month_bin_curve_analysis(dataset, turbine_code, air_density_tag=None, dir_path=None, 
                             cp_factor=1.0, rotor_radius=None):
    """
    基于SCADA数据的BIN曲线分析

    风速-功率曲线、风速-风能利用系数Cp曲线、风速-桨距角曲线、
    桨距角-功率曲线、风速-转速曲线、转速-功率曲线

    #? cp_factor 和 rotor_radius两个参数二选一，优先采用 rotor_radius数值
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param air_density_tag: 空气密度标签
    :param dir_path: 存储路径
    :param cp_factor: 风能利用系数因子
    :param air_density_tag (str, optional): 空气密度标签. Defaults to None.

    :return:
    """

    #? 如果rotor_radius参数存在，覆盖cp_factor参数数值
    if rotor_radius is not None:
        cp_factor = 0.5 * math.pi * pow(rotor_radius, 2) / 1000

    ''''''
    # *** ---------- 1 风速-功率曲线 ----------
    wind_speed_power_bin(dataset, turbine_code, dir_path, hue='month') 

    # *** ---------- 2 风速-风能利用系数Cp曲线 ----------
    wind_speed_cp_bin(dataset, turbine_code, air_density_tag, dir_path, cp_factor, hue='month')
    
    # *** ---------- 3 风速-桨距角曲线 ----------
    speed_pitch_plot_x(dataset, turbine_code, dir_path, hue='month')  
    
    # *** ---------- 4 桨距角-功率曲线 ----------
    pitch_power_plot_x(dataset, turbine_code, dir_path, hue='month')
    

    # *** ---------- 5 风速-转速曲线 ----------
    speed_wind_gen_bin(dataset, turbine_code, dir_path, hue='month')

    # *** ---------- 6 转速-功率曲线 ----------
    gen_speed_power_bin(dataset, turbine_code, dir_path, hue='month')

    # *** ---------- 7 空气密度-功率曲线 ----------
    if air_density_tag is not None:
        air_density_power_bin(dataset, air_density_tag, turbine_code, dir_path, hue='month')
    
    # *** ---------- 8 风向-功率曲线 ----------
    wind_direction_power_bin(dataset, turbine_code, dir_path, hue='month')


    # *** ---------- 9 风速-叶尖速比曲线 ----------
    wind_speed_tsr_bin(dataset, turbine_code, dir_path, hue='month')


def bin_curve_analysis(dataset, turbine_code, air_density_tag=None, dir_path=None, 
                       cp_factor=1.0, rotor_radius=None, plot_flag=False, run_func_list=None):
    """
    基于SCADA数据的BIN曲线分析，返回分仓曲线数据词典

    风速-功率曲线、风速-风能利用系数Cp曲线、风速-桨距角曲线、
    桨距角-功率曲线、风速-转速曲线、转速-功率曲线
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param air_density_tag: 空气密度标签
    :param dir_path: 存储路径
    :param cp_factor: 风能利用系数因子
    :param air_density_tag (str, optional): 空气密度标签. Defaults to None.
    :param plot_flag: 是否针对每个风机分仓曲线绘图 【单个风机】【分仓曲线】

    :return (dict): 分仓曲线数据词典，词典名称：key名称'_'之后的进行分仓的变量，之前的是分仓后进行求平均的变量
    """
    bin_dict = {}

    #? 如果rotor_radius参数存在，覆盖cp_factor参数数值
    if rotor_radius is not None:
        cp_factor = 0.5 * math.pi * pow(rotor_radius, 2) / 1000

    if "power_windspeed" in run_func_list:
        # *** ---------- 1 风速-功率曲线 ----------
        path, file_name = wind_speed_power_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag)

    elif "cp_windspeed" in run_func_list:
        # # ? 分仓曲线异常数据清洗与填充
        # # TODO: 针对不同的问题需要进一步补充
        # power_windspeed_bin_df = wind_speed_power_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag,)
        # wind_speed_power_bin_fix(power_windspeed_bin_df)

        # *** ---------- 2 风速-风能利用系数Cp曲线 ----------
        path, file_name = wind_speed_cp_bin(dataset, turbine_code, air_density_tag, dir_path,
                                            cp_factor, hue=air_density_tag, plot_flag=plot_flag)

    elif "pitch_windspeed" in run_func_list:
        # *** ---------- 3 风速-桨距角曲线 ----------
        # speed_pitch_plot_x(dataset, turbine_code, dir_path)
        path, file_name = wind_speed_pitch_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag)


    elif "power_pitch" in run_func_list:
        # *** ---------- 4 桨距角-功率曲线 ----------
        # pitch_power_plot_x(dataset, turbine_code, dir_path)
        path, file_name = pitch_power_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag)
    
    elif "gen_wind_speed" in run_func_list:
        # *** ---------- 5 风速-转速曲线 ----------
        path, file_name = speed_wind_gen_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag)

    elif "power_genspeed" in run_func_list:
        # *** ---------- 6 转速-功率曲线 ----------
        path, file_name = gen_speed_power_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag)

    elif "power_airdensity" in run_func_list:
        # *** ---------- 7 空气密度-功率曲线 ----------

        if air_density_tag is not None:
            path, file_name = air_density_power_bin(dataset, air_density_tag, turbine_code, dir_path,
                                                    hue=None, plot_flag=plot_flag)

    elif "power_winddir" in run_func_list:
        # *** ---------- 8 风向-功率曲线 ----------
        path, file_name = wind_direction_power_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag)

    elif "tsr_windspeed" in run_func_list:
        # *** ---------- 9 风速-叶尖速比曲线 ----------
        path, file_name = wind_speed_tsr_bin(dataset, turbine_code, dir_path, plot_flag=plot_flag)
    
    return path, file_name


def dict_df_merge(data_dict, new_dict, turbine_code):
    """合并基于DataFrame数值类型的两个词典

    Args:
        data_dict (dict): 合并词典
        new_dict (dict): 新加入的数据词典
        turbine_code (str): 机组编码

    Returns:
        dict: 合并后的词典数据
    """

    for key in new_dict.keys():
        if new_dict[key] is not None:
            new_dict[key][turbine_code_label] = turbine_code
    
    if len(data_dict.keys()) == 0:
        data_dict = new_dict
    else:
        for key in data_dict.keys():
            data_dict[key] = pd.concat([data_dict[key], new_dict[key]])
            data_dict[key].reset_index(drop=True, inplace=True)

    return data_dict


def power_curve_bin(dataset, turbine_code, dir_path, hue=power_label):
    """
    绘制风速-转速关系 图像 【连续月度曲线对比】
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param dir_path: 图像文件存储路径
    
    :return:
    """
    import seaborn as sns

    #
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    ''''''
    plt.rcParams.update(
        {
            # 'text.usetex': False,
            'mathtext.fontset': 'stix',
            'font.family': 'serif',
            "font.serif": ['Microsoft YaHei'],
        }
    )

    
    std_power_label = "std_power"
    actual_power_label = "actual_power"

    # month_list = norm_data[month_label].unique().tolist()
    month_group_dataset = dataset.groupby("month")
    
    count = 0
    pre_month_data = None
    pre_month = None
    for index, month_data in month_group_dataset:
        count = count + 1

        if count == 1:
            pre_month = index
            pre_month_data = month_data

            continue

        #
        pre_actual_curve = calc_actual_power_curve(pre_month_data)
        actual_curve = calc_actual_power_curve(month_data)
        
        plt.figure()
        #? hue="label": 标记异常数据与否
        # palette='vlag' 'deep'【默认】'rainbow'
        sns.scatterplot(data=pre_month_data, x=wind_speed_label, y=power_label, 
                        legend=False, alpha=0.5, color="yellow", size=1) # palette='vlag', 
        sns.scatterplot(data=dataset, x=wind_speed_label, y=power_label, 
                        legend=False, alpha=0.1, color="green", size=1) # palette='deep', 
        
        plt.plot(pre_actual_curve[wind_speed_label], pre_actual_curve[actual_power_label], 
                c="r", label="{} power curve".format(pre_month))
        plt.plot(actual_curve[wind_speed_label], actual_curve[actual_power_label], 
                c="blue", label="{} power curve".format(index))
        
        '''
        #? 使用errorbar绘制功率曲线的方差
        # ecolor='r', color='b', crimson deeppink lime
        #? color与mfc冲突，后者覆盖
        plt.errorbar(actual_curve[wind_speed_label], actual_curve[actual_power_label], yerr=actual_curve[std_power_label],
                    fmt='o', ecolor='orangered', color='b', elinewidth=2, capsize=4,
                    markersize=4, mfc='yellow', mec='green', mew=0.5)
        '''

        plt.legend()
        plt.title("{} VS {} power curve".format(pre_month, index))

        # plt.show()
        file_name = "{} power curve comparison {} VS {}.png".format(turbine_code, pre_month, index)
        plot_save(dir_path, file_name)

        #
        pre_month = index
        pre_month_data = month_data



def wind_speed_power_bin_fix(bin_curve_data):
    """风速-功率 分仓曲线修正

    Args:
        bin_curve_data (DataFrame): 风速-功率 分仓曲线数据集

    Returns:
        DataFrame: 异常数值清洗和插值填充后的分仓曲线数据
    """

    #! 曲线额定风速以上存在功率为零的异常
    #? 分仓存在的缺陷：风速大于15以后，部分分仓可能存在没有数据点的情况，导致拟合后的曲线功率数据为零
    bin_curve_data[power_label] = bin_curve_data.apply(lambda row: np.nan if (row[wind_speed_label]>10 
        and row[wind_speed_label]<20 and row[power_label]<=50) else row[power_label], axis=1)
    
    #? 不同的数据插值拟合方式
    # method="ffill", 
    bin_curve_data.interpolate(inplace=True) 
    # bin_curve_data[power_label] = bin_curve_df[power_label].interpolate(method="linear").bfill().values

    return bin_curve_data


def wind_speed_power_bin(dataset, turbine_code=None, file_path=None,
                         hue=None, plot_flag=False):
    """
    绘制风速-功率关系 图像 【对风速分仓】【功率曲线建模】【IEC Bin】
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的风速-功率分仓曲线
    """

    # *** ---------- 1. wind speed分仓binning ----------
    wind_speed_bins = np.arange(0, np.ceil(dataset[wind_speed_label].max()), 0.25)
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
    if plot_flag:
        # 功率
        xlabel = "风速(m/s$^{-1}$)"
        ylabel = "功率(kW)"
        title = "风速-功率分析" + " " + turbine_code
        
        # 绘图和保存文件
        file_name = "wind_speed_power_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)

        #
        bin_curve_plot(dataset, wind_speed_label, power_label, xlabel, ylabel,
                       title, full_path, power_windspeed_bin_df,
                       hue=hue, size=hue)
    else:
        file_name = None
        full_path = None

    return full_path, file_name


def wind_speed_tsr_bin(dataset, turbine_code=None, file_path=None, hue=None, plot_flag=False):
    """
    绘制风速-叶尖速比关系 图像 【对风速分仓】【功率曲线建模】【IEC Bin】
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的风速-叶尖速比分仓曲线
    """

    # *** ---------- 1. wind speed分仓binning ----------
    wind_speed_bins = np.arange(0, np.ceil(dataset[wind_speed_label].max()), 0.25)
    wind_speed_labels = [x for x in wind_speed_bins[1:]]

    dataset[wind_speed_bin_label] = pd.cut(dataset[wind_speed_label], bins=wind_speed_bins, 
                                       labels=wind_speed_labels)
    
    # *** ---------- 2. 分仓binning拟合功率曲线 ----------
    tsr_mean, tsr_std = binning_proc(dataset, wind_speed_labels, wind_speed_bin_label, tsr_label)
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    tsr_windspeed_bin_df = pd.DataFrame()
    tsr_windspeed_bin_df[wind_speed_label] = wind_speed_labels
    tsr_windspeed_bin_df[tsr_label] = tsr_mean
    tsr_windspeed_bin_df['{}_std'.format(tsr_label)] = tsr_std


    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    if plot_flag:
        # 功率
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "叶尖速比"
        title = "风速-叶尖速比分析" + "   " + turbine_code
        
        # 绘图和保存文件
        file_name = "wind_speed_tsr_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)

        #
        bin_curve_plot(dataset, wind_speed_label, tsr_label, xlabel, ylabel,
                       title, full_path, tsr_windspeed_bin_df,
                       hue=hue, size=hue)
    
    return tsr_windspeed_bin_df


def wind_speed_cp_bin(dataset, turbine_code=None, air_density_tag=None, dir_path=None,
                      cp_factor=1.0, rotor_radius=None, hue=None, plot_flag=False):
    """
    基于SCADA数据的风速-风能利用系数Cp曲线 【BIN曲线分析】【对风速分仓】
    
    :param air_density_tag (str): 空气密度标签
    :param cp_factor (float): 风能利用系数因子
    :param air_density_tag (str, optional): 空气密度标签. Defaults to None.
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param dir_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片

    :return: (DataFrame) 拟合后的风速-风能利用系数Cp分仓曲线
    """

    #? 如果rotor_radius参数存在，覆盖cp_factor参数数值
    if rotor_radius is not None:
        cp_factor = 0.5 * math.pi * pow(rotor_radius, 2) / 1000

    #TODO:
    target_data = dataset[dataset[wind_speed_label] >= 0.05]

    # *** ---------- 1 计算风能利用系数 ----------
    if air_density_tag is not None:
        c_p_list = target_data.apply(lambda row: row[power_label] /
                                 (cp_factor * row[air_density_tag] * pow(row[wind_speed_label], 3)), axis=1)
    else:
        c_p_list = target_data.apply(lambda row: row[power_label] /
                                 (cp_factor * 1.225 * pow(row[wind_speed_label], 3)), axis=1)
    
    #? power coefficient label
    # cp_label = "cp"
    target_data[cp_label] = c_p_list

    #! 基于风能利用系数计算筛选数据
    target_data = target_data[(target_data[cp_label] <= 0.597) & (target_data[cp_label] >= 0.100) ]
    
    '''
    #! 发电机转速筛选
    #TODO: 尖峰项目适用
    target_data = target_data[(target_data[gen_speed_label] <= 1500) 
                          & (target_data[gen_speed_label] >= 1200) ]
    '''
    

    # *** ---------- 2. wind speed分仓binning ----------
    wind_speed_bins = np.arange(0, np.ceil(target_data[wind_speed_label].max()), 0.25)
    wind_speed_labels = [x for x in wind_speed_bins[1:]]

    target_data[wind_speed_bin_label] = pd.cut(target_data[wind_speed_label], bins=wind_speed_bins,
                                               labels=wind_speed_labels)
    
    # *** ---------- 3. 分仓binning拟合偏航角度曲线 ----------
    cp_mean, cp_std = binning_proc(target_data, wind_speed_labels, wind_speed_bin_label, cp_label,
                                   split_value=3, interpolate_method="linear", fill_value=0)
    
    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    cp_windspeed_bin_df = pd.DataFrame()
    # bin_label (str): 数据集分仓列名称（标签名称）
    cp_windspeed_bin_df[wind_speed_label] = wind_speed_labels
    cp_windspeed_bin_df[cp_label] = cp_mean
    cp_windspeed_bin_df['{}_std'.format(cp_label)] = cp_std

    cp_windspeed_bin_df = cp_windspeed_bin_df.drop(cp_windspeed_bin_df[cp_windspeed_bin_df[cp_label] == 0].index)

    # *** ---------- 5. 组装binning分仓曲线数据 ----------
    if plot_flag:
        # *** 风能利用系数-绘图并保存文件
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "风能利用系数$C_p$"
        title = "风速-风能利用系数分析" + " " + turbine_code
        
        file_name = "Speed_Cp_{}.png".format(turbine_code)
        full_path = os.path.join(dir_path, file_name)

        target_data.sort_values(by=wind_speed_label, axis=0, ascending=True, inplace=True)

        '''
        # 空气密度 与 风能利用系数关系
        curve_plot(target_data, wind_speed_label, cp_label, xlabel, ylabel,
                title, full_path, hue=air_density_tag, size=air_density_tag)
        '''
        
        bin_curve_plot(target_data, wind_speed_label, cp_label, xlabel, ylabel,
                       title, full_path, cp_windspeed_bin_df,
                       hue=hue, size=air_density_tag)
    else:
        xlabel = "风速(m/s)"
        ylabel = "风能利用系数Cp"
        title = "风速-风能利用系数分析" + " " + turbine_code

        # file_name = "Speed_Cp_{}.png".format(turbine_code)
        # full_path = os.path.join(dir_path, file_name)
        # 空气密度分仓
        target_data = common_cut(target_data, air_density_label, air_density_bin_label, start=0.9, step=0.025)

        target_data.sort_values(by=wind_speed_label, axis=0, ascending=True, inplace=True)

        full_path, file_name = build_html(target_data, wind_speed_label, cp_label, xlabel, ylabel,
                                          title, dir_path, cp_windspeed_bin_df,
                                          hue=air_density_bin_label,
                                          sizes=pd.unique(target_data[air_density_bin_label]),
                                          turbine_code=turbine_code, beside_title="空气密度")
    
    return full_path, file_name


def wind_speed_pitch_bin(dataset, turbine_code=None, file_path=None, hue=power_label, plot_flag=False):
    """
    绘制风速-桨距角关系 图像 【对风速分仓】
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的风速-桨距角分仓曲线
    """

    #! 对变桨角度数据进行处理
    # TODO: 
    dataset[pitch_label] = dataset[pitch_label]

    
    # *** ---------- 1. wind speed分仓binning ----------
    wind_speed_bins = np.arange(0, np.ceil(dataset[wind_speed_label].max()), 0.25)
    wind_speed_labels = [x for x in wind_speed_bins[1:]]

    dataset[wind_speed_bin_label] = pd.cut(dataset[wind_speed_label], bins=wind_speed_bins, 
                                       labels=wind_speed_labels)
    
    
    # *** ---------- 2. 分仓binning拟合桨距角曲线 ----------
    pitch_mean, pitch_std = binning_proc(dataset, wind_speed_labels, wind_speed_bin_label, pitch_label,
                                         split_value=3, interpolate_method="linear", fill_value=0)
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    pitch_windspeed_bin_df = pd.DataFrame()
    pitch_windspeed_bin_df[wind_speed_label] = wind_speed_labels
    pitch_windspeed_bin_df[pitch_label] = pitch_mean
    pitch_windspeed_bin_df['{}_std'.format(pitch_label)] = pitch_std

    pitch_windspeed_bin_df = pitch_windspeed_bin_df.drop(pitch_windspeed_bin_df[pitch_windspeed_bin_df[pitch_label] == 0].index)

    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    if plot_flag:
        #? 风速-桨距角
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "桨距角/($°$)"
        title = "风速-桨距角分析" + " " + turbine_code
        
        # 绘图和保存文件
        file_name = "wind_speed_pitch_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)

        bin_curve_plot(dataset, wind_speed_label, pitch_label, xlabel, ylabel,
                       title, full_path, pitch_windspeed_bin_df,
                       hue=hue, size=power_label)

    else:
        # ? 风速-桨距角
        xlabel = "风速(m/s)"
        ylabel = "桨距角(°)"
        title = "风速-桨距角分析" + " " + turbine_code
        # 功率分仓
        dataset = common_cut(dataset, power_label, power_bin_label, start=0, step=400)
        dataset[power_bin_label] = dataset[power_bin_label].astype('float').fillna(0)

        full_path, file_name = build_html(dataset, wind_speed_label, pitch_label, xlabel, ylabel,
                                          title, file_path, pitch_windspeed_bin_df,
                                          hue=power_bin_label,
                                          sizes=pd.unique(dataset[power_bin_label]),
                                          turbine_code=turbine_code, beside_title="功率")

    return full_path, file_name


def speed_wind_gen_bin(dataset, turbine_code=None, file_path=None, hue=power_label, plot_flag=False):
    """
    绘制风速-转速关系 图像 【对风速分仓】
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的风速-转速分仓曲线
    """
    
    # *** ---------- 1. wind speed分仓binning ----------
    wind_speed_bins = np.arange(0, np.ceil(dataset[wind_speed_label].max()), 0.25)
    wind_speed_labels = [x for x in wind_speed_bins[1:]]

    dataset[wind_speed_bin_label] = pd.cut(dataset[wind_speed_label], bins=wind_speed_bins, 
                                       labels=wind_speed_labels)
    
    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    gen_speed_mean, gen_speed_std = binning_proc(dataset, wind_speed_labels, wind_speed_bin_label, 
            gen_speed_label, split_value=3, interpolate_method="linear", fill_value=0)
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    gen_wind_speed_bin_df = pd.DataFrame()
    gen_wind_speed_bin_df[wind_speed_label] = wind_speed_labels
    gen_wind_speed_bin_df[gen_speed_label] = gen_speed_mean
    gen_wind_speed_bin_df['{}_std'.format(gen_speed_label)] = gen_speed_std
    gen_wind_speed_bin_df = gen_wind_speed_bin_df.drop(gen_wind_speed_bin_df[gen_wind_speed_bin_df[gen_speed_label] == 0].index)

    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    if plot_flag:
        # 风速-转速
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "转速/(r·min$^{-1}$)"
        title = "风速-转速分析" + " " + turbine_code
        
        # 绘图和保存文件
        file_name = "speed_wind_gen_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)

        '''
        curve_plot(dataset, wind_speed_label, gen_speed_label, xlabel, ylabel, title, full_path,
                hue=hue, size=power_label) #
        '''
        
        bin_curve_plot(dataset, wind_speed_label, gen_speed_label, xlabel, ylabel,
                       title, full_path, gen_wind_speed_bin_df,
                       hue=hue, size=power_label)
    else:
        xlabel = "风速(m/s)"
        ylabel = "转速(r/min)"
        title = "风速-转速分析" + " " + turbine_code

        dataset = common_cut(dataset, power_label, power_bin_label, start=0, step=400)
        dataset[power_bin_label] = dataset[power_bin_label].astype('float').fillna(0)

        full_path, file_name = build_html(dataset, wind_speed_label, gen_speed_label, xlabel, ylabel,
                                          title, file_path, gen_wind_speed_bin_df,
                                          hue=power_bin_label,
                                          sizes=pd.unique(dataset[power_bin_label]),
                                          turbine_code=turbine_code, beside_title="功率")

    return full_path, file_name


def gen_speed_power_bin(dataset, turbine_code=None, file_path=None, hue=wind_speed_label, plot_flag=False):
    """
    绘制转速-功率关系 图像 【对转速分仓】
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的转速-功率分仓曲线
    """

    # *** ---------- 1. generator speed分仓binning ----------    
    gen_speed_bins = np.arange(np.floor(dataset[gen_speed_label].min()/100.0)*100, 
                               np.ceil(dataset[gen_speed_label].max()/100.0)*100, 10)
    gen_speed_labels = [x for x in gen_speed_bins[1:]]

    dataset[gen_speed_bin_label] = pd.cut(dataset[gen_speed_label], bins=gen_speed_bins, labels=gen_speed_labels)
    
    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    power_mean, power_std = binning_proc(dataset, gen_speed_labels, gen_speed_bin_label, power_label,
                                         interpolate_method="linear")
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    power_genspeed_bin_df = pd.DataFrame()
    power_genspeed_bin_df[gen_speed_label] = gen_speed_labels
    power_genspeed_bin_df[power_label] = power_mean
    power_genspeed_bin_df['{}_std'.format(power_label)] = power_std
    power_genspeed_bin_df = power_genspeed_bin_df.drop(power_genspeed_bin_df[power_genspeed_bin_df[power_label] == 0].index)

    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    if plot_flag:
        # 转速-功率
        xlabel = "转速(r/min$^{-1}$)"
        ylabel = "功率(kW)"
        title = "转速-功率分析" + " " + turbine_code
        
        # 绘图和保存文件
        file_name = "gen_speed_power_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)

        '''
        curve_plot(dataset, gen_speed_label, power_label, xlabel, ylabel, title, full_path,
                hue=hue, size=wind_speed_label) #
        '''
        
        bin_curve_plot(dataset, gen_speed_label, power_label, xlabel, ylabel,
                       title, full_path, power_genspeed_bin_df,
                       hue=hue, size=wind_speed_label)
    else:
        xlabel = "转速(r/min)"
        ylabel = "功率(kW)"
        title = "转速-功率分析" + " " + turbine_code

        dataset = common_cut(dataset, wind_speed_label, wind_speed_bin_label, start=0, step=3)
        dataset[wind_speed_bin_label] = dataset[wind_speed_bin_label].astype('float').fillna(0)

        full_path, file_name = build_html(dataset, gen_speed_label, power_label, xlabel, ylabel,
                                          title, file_path, power_genspeed_bin_df,
                                          hue=wind_speed_bin_label,
                                          sizes=pd.unique(dataset[wind_speed_bin_label]),
                                          turbine_code=turbine_code, beside_title="风速")
    
    return full_path, file_name


def air_density_power_bin(dataset, air_density_tag, turbine_code=None, file_path=None, hue=None, plot_flag=False):
    """
    绘制空气密度-功率关系 图像
    
    :param air_density_tag: 空气密度标签名称【数据列名称】
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的空气密度-功率分仓曲线
    """

    # *** ---------- 1. air density分仓binning ----------    
    air_density_bins = np.arange(0.9, 1.4, 0.05)
    air_density_labels = [x for x in air_density_bins[1:]]

    dataset[air_density_bin_label] = pd.cut(dataset[air_density_tag], bins=air_density_bins, 
                                               labels=air_density_labels)
    
    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    power_mean, power_std = binning_proc(dataset, air_density_labels, air_density_bin_label, power_label,
                                         fill_value=0)
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    power_airdensity_bin_df = pd.DataFrame()
    power_airdensity_bin_df[air_density_tag] = air_density_labels
    power_airdensity_bin_df[power_label] = power_mean
    power_airdensity_bin_df['{}_std'.format(power_label)] = power_std


    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    if plot_flag:
        #? 空气密度-功率
        xlabel = "空气密度/(Kg/m$^3$)"
        ylabel = "功率/(kW)"
        title = "空气密度-功率分析" + "   " + turbine_code
        
        # 绘图和保存文件
        file_name = "air_density_power_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)

        '''
        curve_plot(dataset, air_density_tag, power_label, xlabel, ylabel, title, full_path,
                hue=hue, size=wind_speed_label)
        '''

        bin_curve_plot(dataset, air_density_tag, power_label, xlabel, ylabel,
                       title, full_path, power_airdensity_bin_df,
                       hue=hue, size=wind_speed_label)
    
    return power_airdensity_bin_df


def wind_direction_power_bin(dataset, turbine_code=None, file_path=None, hue=wind_speed_label, plot_flag=False):
    """
    绘制风向-功率关系 图像 【对风向分仓】
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的风向-功率分仓曲线
    """

    # *** ---------- 1. wind direction分仓binning ----------    
    wind_direction_bins = np.arange(0, 360, 11.25)
    wind_direction_labels = [x for x in wind_direction_bins[1:]]

    dataset[wind_direction_bin_label] = pd.cut(dataset[wind_direction_label], bins=wind_direction_bins, 
                                               labels=wind_direction_labels)
    
    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    power_mean, power_std = binning_proc(dataset, wind_direction_labels, wind_direction_bin_label, power_label,
                                         fill_value=0)
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    power_winddir_bin_df = pd.DataFrame()
    power_winddir_bin_df[wind_direction_label] = wind_direction_labels
    power_winddir_bin_df[power_label] = power_mean
    power_winddir_bin_df['{}_std'.format(power_label)] = power_std


    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    if plot_flag:
        #? 风向-功率
        xlabel = "风向/(°)"
        ylabel = "功率/(kW)"
        title = "风向-功率分析" + "   " + turbine_code
        
        # 绘图和保存文件
        file_name = "wind_direction_power_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)

        '''
        curve_plot(dataset, wind_direction_label, power_label, xlabel, ylabel, title, full_path,
                hue=hue, size=wind_speed_label) #
        '''

        bin_curve_plot(dataset, wind_direction_label, power_label, xlabel, ylabel,
                       title, full_path, power_winddir_bin_df,
                       hue=hue, size=wind_speed_label)
    
    return power_winddir_bin_df


def pitch_power_bin(dataset, turbine_code=None, file_path=None, hue=wind_speed_label, plot_flag=False):
    """
    绘制桨距角-功率关系 图像 【对桨距角分仓】
    
    :param dataset (DataFrame): 时序数据集
    :param turbine_code (str): 机组编码
    :param file_path (str): 图像文件完整路径
    :param hue (str): seaborn图像hue数据标签
    :param plot_flag (bool): 是否绘制分仓曲线图片
    
    :return: (DataFrame) 拟合后的桨距角-功率分仓曲线
    """

    #! 对变桨角度数据进行处理
    # TODO
    dataset[pitch_label] = dataset[pitch_label]

    # TODO: 对桨距角进行清洗分析
    target_data = dataset[(dataset[pitch_label] <= 25) & (dataset[pitch_label] >= -5)]


    # *** ---------- 1. pitch分仓binning ----------    
    pitch_bins = np.arange(0, 20, 0.5)
    pitch_labels = [x for x in pitch_bins[1:]]

    target_data[pitch_bin_label] = pd.cut(target_data[pitch_label], bins=pitch_bins, labels=pitch_labels)
    
    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    power_mean, power_std = binning_proc(target_data, pitch_labels, pitch_bin_label, power_label,
                                         interpolate_method="linear")
    
    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    power_pitch_bin_df = pd.DataFrame()
    power_pitch_bin_df[pitch_label] = pitch_labels
    power_pitch_bin_df[power_label] = power_mean
    power_pitch_bin_df['{}_std'.format(power_label)] = power_std
    power_pitch_bin_df = power_pitch_bin_df.drop(power_pitch_bin_df[power_pitch_bin_df[power_label] == 0].index)

    # *** ---------- 4. 组装binning分仓曲线数据 ----------
    if plot_flag:
        #? 桨距角-功率
        xlabel = "桨距角(°)"
        ylabel = "功率(kW)"
        title = "桨距角-功率分析" + "   " + turbine_code
        
        # 绘图和保存文件
        file_name = "pitch_power_{}.png".format(turbine_code)
        full_path = os.path.join(file_path, file_name)
        
        bin_curve_plot(target_data, pitch_label, power_label, xlabel, ylabel,
                       title, full_path, power_pitch_bin_df,
                       hue=hue, size=wind_speed_label)
    else:
        xlabel = "桨距角(°)"
        ylabel = "功率(kW)"
        title = "桨距角-功率分析" + " " + turbine_code

        target_data = common_cut(target_data, wind_speed_label, wind_speed_bin_label, start=0, step=3)
        target_data[wind_speed_bin_label] = target_data[wind_speed_bin_label].astype('float').fillna(0)

        full_path, file_name = build_html(target_data, pitch_label, power_label, xlabel, ylabel,
                                          title, file_path, power_pitch_bin_df,
                                          hue=wind_speed_bin_label,
                                          sizes=pd.unique(target_data[wind_speed_bin_label]),
                                          turbine_code=turbine_code, beside_title="风速")
    
    return full_path, file_name


def farm_bin_curve_plot(bin_df, x_var, y_var, xlabel, ylabel, title, file_path):
    """多风机分仓binning曲线绘制 【风场多风机分仓binning曲线对比】
    #! 参见 models.bin_analysis.quant.cloud.pitch_analysis 的"common_bin_pitch_plot"方法

    Args:
        bin_df (dataframe): 分仓数据集
        bin_var (str): 分仓变量【数据列名称】
        xlabel (str): x轴标签
        ylabel (str): y轴标签
        title (str): 图像标题
        file_path (str): 图像文件完整路径
    """
    import seaborn as sns
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    ''''''
    plt.rcParams.update(
        {
            # 'text.usetex': False,
            'mathtext.fontset': 'stix',
            'font.family': 'serif',
            "font.serif": ['Microsoft YaHei'],
        }
    )

    plt.figure(figsize=(16,10))

    sns.lineplot(data=bin_df, x=x_var, y=y_var, hue=turbine_code_label, 
                 style=turbine_code_label, markers=True, dashes=False)

    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.tight_layout()

    # 绘图和保存文件
    # plt.show()
    ''''''
    file_name = "{}.png".format(title)
    plot_save(file_path, file_name)


def dict_curve_plot(bin_dict, file_path, cn_label_flag = True):
    """基于分仓binning曲线绘制机组对比图片

    Args:
        bin_dict (dict): 分仓binning曲线数据词典
        file_path (str): 图像文件完整路径
        cn_label_flag (bool): 是否采用中文标注 【否则采用英文】
    """

    '''
    bin_dict = {'cp_windspeed': cp_windspeed_bin_df, 'pitch_windspeed': pitch_windspeed_bin_df,
                'power_pitch': power_pitch_bin_df, 'gen_wind_speed': gen_wind_speed_bin_df,
                'power_genspeed': power_genspeed_bin_df, 'power_airdensity': power_airdensity_bin_df,
                'power_winddir': power_winddir_bin_df, 'power_windspeed': power_windspeed_bin_df}
    '''

    ''''''
    # *** ---------- 1. 风速-风能利用系数 曲线 ----------
    x_var = wind_speed_label
    y_var = cp_label

    if cn_label_flag:
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "风能利用系数$C_p$"
        title = "风速-风能利用系数分仓分析"
    else:
        xlabel = "Wind Speed/(m·s$^{-1}$)"
        ylabel = "Power Coefficient$C_p$"
        title = "Wind Speed-Power Coefficient Binning Analysis"
    
    farm_bin_curve_plot(bin_dict['cp_windspeed'], x_var, y_var, xlabel, ylabel, title, file_path)

    # *** ---------- 2. 风速-桨距角 曲线 ----------
    x_var = wind_speed_label
    y_var = pitch_label

    if cn_label_flag:
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "桨距角/($°$)"
        title = "风速-桨距角分仓分析"
    else:
        xlabel = "Wind Speed/(m·s$^{-1}$)"
        ylabel = "Pitch Angle/($°$)"
        title = "Wind Speed-Pitch Angle Binning Analysis"

    farm_bin_curve_plot(bin_dict['pitch_windspeed'], x_var, y_var, xlabel, ylabel, title, file_path)

    # *** ---------- 3. 桨距角-功率 曲线 ----------
    x_var = pitch_label
    y_var = power_label

    if cn_label_flag:
        xlabel = "桨距角/(°)"
        ylabel = "功率/(kW)"
        title = "桨距角-功率分仓分析"
    else:
        xlabel = "Pitch Angle/(°)"
        ylabel = "Power/(kW)"
        title = "Pitch Angle-Power Binning Analysis"

    farm_bin_curve_plot(bin_dict['power_pitch'], x_var, y_var, xlabel, ylabel, title, file_path)

    # *** ---------- 4. 桨距角-功率 曲线 ----------
    x_var = wind_speed_label
    y_var = gen_speed_label

    if cn_label_flag:
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "转速/(r·min$^{-1}$)"
        title = "风速-转速分仓分析"
    else:
        xlabel = "Wind Speed/(m·s$^{-1}$)"
        ylabel = "Generator Speed/(r·min$^{-1}$)"
        title = "Wind Speed-Generator Speed Binning Analysis"

    farm_bin_curve_plot(bin_dict['gen_wind_speed'], x_var, y_var, xlabel, ylabel, title, file_path)

    # *** ---------- 5. 桨距角-功率 曲线 ----------
    x_var = gen_speed_label
    y_var = power_label

    if cn_label_flag:
        xlabel = "转速/(r·min$^{-1}$)"
        ylabel = "功率/(kW)"
        title = "转速-功率分仓分析"
    else:
        xlabel = "Wind Speed/(r·min$^{-1}$)"
        ylabel = "Power/(kW)"
        title = "Wind Speed-Power Binning Analysis"

    farm_bin_curve_plot(bin_dict['power_genspeed'], x_var, y_var, xlabel, ylabel, title, file_path)

    # *** ---------- 6. 空气密度-功率 曲线 ----------
    x_var = air_density_label
    y_var = power_label

    if cn_label_flag:
        xlabel = "空气密度/(Kg/m$^3$)"
        ylabel = "功率/(kW)"
        title = "空气密度-功率分仓分析"
    else:
        xlabel = "Air Density/(Kg/m$^3$)"
        ylabel = "Power/(kW)"
        title = "Air Density-Power Binning Analysis"

    farm_bin_curve_plot(bin_dict['power_airdensity'], x_var, y_var, xlabel, ylabel, title, file_path)

    # *** ---------- 7. 空气密度-功率 曲线 ----------
    x_var = wind_direction_label
    y_var = power_label

    if cn_label_flag:
        xlabel = "风向/(°)"
        ylabel = "功率/(kW)"
        title = "风向-功率分仓分析"
    else:
        xlabel = "Wind Direction/(°)"
        ylabel = "Power/(kW)"
        title = "Wind Direction-Power Binning Analysis"

    farm_bin_curve_plot(bin_dict['power_winddir'], x_var, y_var, xlabel, ylabel, title, file_path)
    

    # *** ---------- 8. 风速-功率 曲线 ----------
    x_var = wind_speed_label
    y_var = power_label

    if cn_label_flag:
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "功率/(kW)"
        title = "风速-功率分仓分析"
    else:
        xlabel = "Wind Speed/(m·s$^{-1}$)"
        ylabel = "Power/(kW)"
        title = "Wind Speed-Power Binning Analysis"

    farm_bin_curve_plot(bin_dict['power_windspeed'], x_var, y_var, xlabel, ylabel, title, file_path)
    
    
    # *** ---------- 9 风速-叶尖速比曲线 ----------
    x_var = wind_speed_label
    y_var = tsr_label

    if cn_label_flag:
        xlabel = "风速/(m·s$^{-1}$)"
        ylabel = "叶尖速比"
        title = "风速-叶尖速比分仓分析"
    else:
        xlabel = "Wind Speed/(m·s$^{-1}$)"
        ylabel = "Tip Speed Ratio (TSR)"
        title = "Wind Speed-TSR Binning Analysis"

    farm_bin_curve_plot(bin_dict['tsr_windspeed'], x_var, y_var, xlabel, ylabel, title, file_path)


