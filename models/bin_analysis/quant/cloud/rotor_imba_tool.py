#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# Rotor Imbalance Analysis for Wind Turbines
# 功能描述：风电机组转子不平衡分析
#
# -----------------------
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
import logging

import numpy as np
import pandas as pd

import seaborn as sns

#
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
#? 中文乱码问题
font = fm.FontProperties(fname='微软雅黑.ttf')
#? 字体设置：SimHei
plt.rcParams["font.sans-serif"]=["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"]=False

#
import warnings
warnings.filterwarnings("ignore")

#
from models.bin_analysis.quant.cloud.file_dir_tool import create_dir
from models.bin_analysis.quant.cloud.plot_tool import curve_plot, bin_curve_plot, scatter_plot, hue_scatter_plot

from models.bin_analysis.quant.cloud.wind_base_tool import binning_proc, plot_save, cp_label
from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, wind_direction_label
from models.bin_analysis.quant.cloud.wind_base_tool import gen_speed_label, rotor_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_speed_bin_label, gen_speed_bin_label, power_bin_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_direction_bin_label, air_density_bin_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, mark_label, turbine_code_label

from models.bin_analysis.quant.cloud.power_curve_tool import calc_actual_power_curve, theory_curve_prep, scatter_curve



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

#


# --------------------------------------------------------------------
# ***
# 转子不平衡Rotor Imbalance分析
# ***
# --------------------------------------------------------------------

def plot_rotor_imba_timeseries(df, time_label, imba_label1, imba_label2, 
                               turbine_code, file_path):
    """
    To plot the time series data for rotor imbalance.
    
    input: 
        df(DataFrame): Pandas DataFrame data to plot
        time_label(string): the name of timestamp to plot
        imba_label1(string): the variable name of rotor imbalance
        imba_label2(string): the variable name of rotor imbalance
        turbine_code(string): 机组编码
        file_path(string): 图像文件完整路径
    output: 
        none
    """

    plt.figure(figsize=(16,10))

    sns.scatterplot(data=df, x=time_label, y=rotor_speed_label, hue=imba_label2, size=imba_label2)
    plt.plot(df[time_label], df[imba_label1], color='b')
    plt.plot(df[time_label], df[imba_label2], color='g')

    plt.xlabel(time_label)
    plt.ylabel('Rotor Imbalance')

    title = 'Rotor Imbalance Analysis for {}'.format(turbine_code)
    plt.title(title)
    
    plt.legend()

    # 绘图和保存文件
    plt.show()
    '''
    file_name = "{}.png".format(title)
    plot_save(file_path, file_name)
    '''


def plot_1p_vs_rpm(df, rotor_speed_var, imba_var1, imba_var2, turbine_code, file_path):
    """
    To plot the time series data for rotor imbalance.
    
    input: 
        df(DataFrame): Pandas DataFrame data to plot
        rotorspeed_label(string): the variable name of rotor speed
        imba_var1(string): the variable name of rotor imbalance
        imba_var2(string): the variable name of rotor imbalance
        turbine_code(string): 机组编码
        file_path(string): 图像文件完整路径
    output: 
        none
    """

    plt.figure(figsize=(16,10))

    sns.scatterplot(data=df, x=rotor_speed_var, y=imba_var1)
    sns.scatterplot(data=df, x=rotor_speed_var, y=imba_var2)

    plt.xlabel(rotor_speed_var)
    plt.ylabel('Rotor Imbalance Indicator')

    title = '1P magnitude vs. RPM for {}'.format(turbine_code)
    plt.title(title)
    
    plt.legend()
    plt.tight_layout()

    # 绘图和保存文件
    plt.show()
    '''
    file_name = "{}.png".format(title)
    plot_save(file_path, file_name)
    '''


def farm_rotor_imba_plot(farm_df, x_var, y_var, xlabel, ylabel, title, file_path):
    """多风机分仓binning曲线绘制 【风场多风机分仓binning曲线对比】
    #! 参见 models.bin_analysis.quant.cloud.pitch_analysis 的"common_bin_pitch_plot"方法

    Args:
        farm_df (dataframe): 风场数据集
        x_var (str): x变量【数据列名称】
        y_var (str): y变量【数据列名称】
        xlabel (str): x轴标签
        ylabel (str): y轴标签
        title (str): 图像标题
        file_path (str): 图像文件完整路径
    """

    plt.figure(figsize=(16,10))

    # , markers=True, dashes=True
    sns.scatterplot(data=farm_df, x=x_var, y=y_var, hue=turbine_code_label, 
                    style=turbine_code_label)

    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.tight_layout()

    # 绘图和保存文件
    # plt.show()
    
    file_name = "{}.png".format(title)
    plot_save(file_path, file_name)
    ''''''


def farm_1p_vs_rpm_plot(farm_df, rotor_speed_var, imba_var, file_path):
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

    plt.figure(figsize=(16,10))

    sns.scatterplot(data=farm_df, x=rotor_speed_var, y=imba_var, hue=turbine_code_label, 
                    style=turbine_code_label) # , markers=True, dashes=False
    
    xlabel = '转速RPM/(r·min$^{-1}$)'
    ylabel = 'Rotor Imbalance Indicator'
    title = '1P magnitude vs. RPM'

    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.tight_layout()

    # 绘图和保存文件
    # plt.show()
    
    file_name = "{}.png".format(title)
    plot_save(file_path, file_name)
    ''''''

