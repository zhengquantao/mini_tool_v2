#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 风电机组变桨控制分析
# 功能描述：为实现发电量提升目标，对机组变桨控制进行分析
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
# import logging

import numpy as np
import pandas as pd

#
import warnings
warnings.filterwarnings("ignore")


#
from models.bin_analysis.quant.cloud.file_dir_tool import create_dir

from models.bin_analysis.quant.cloud.plot_tool import curve_plot, scatter_plot, hue_scatter_plot

from models.bin_analysis.quant.cloud.wind_base_tool import binning_proc, plot_save
from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import power_bin_label, wind_speed_bin_label, gen_speed_bin_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, turbine_code_label, mark_label



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

pitch_label = "pitch_angle"
pitch1_label = "pitch1_angle"
pitch2_label = "pitch2_angle"
pitch3_label = "pitch3_angle"

pitch_bin_label = 'pitch_angle_bin'

'''
#! 在models.bin_analysis.quant.cloud.wind_base_tool中统一定义
power_bin_label = 'power_bin'
wind_speed_bin_label = 'wind_speed_bin'
gen_speed_bin_label = 'gen_speed_bin'
'''


# --------------------------------------------------------------------
# ***
# 分析处理
# ***
# --------------------------------------------------------------------

def pitch_analysis(dataset, turbine_code, dir_path=None, air_density_tag=None):
    """
    基于SCADA数据的叶尖速比分析
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码

    :param dir_path: 存储路径
    :param air_density_tag: 空气密度标签
    
    :return:
    """
    
    # 变桨分析图像保存路径
    file_path = create_dir("pitch_img", dir_path)

    '''
    '''
    # *** ---------- 1 风速与桨距角关系-绘图并保存文件 ----------
    speed_pitch_plot(dataset, turbine_code, file_path)    
    

    # *** ---------- 2 功率与桨距角关系-绘图并保存文件 ----------
    power_pitch_plot(dataset, turbine_code, file_path)


    # *** ---------- 3 变桨控制关系-绘图并保存文件 ----------
    mix_pitch_plot(dataset, turbine_code, file_path)
    

    # *** ---------- 4 变桨相关变量关系-绘图并保存文件 ----------
    pitch_relation_plot(dataset, turbine_code, file_path)


def pitch_relation_plot(dataset, turbine_code, file_path):
    """
    绘制风速与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """
    import seaborn as sns

    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    file_name = "{}_relation.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    plt.figure()
    #? To change the diagonal distribution.
    # diag_kind = {‘auto’, ‘hist’, ‘kde’}
    sns.pairplot(dataset, vars = [wind_speed_label, pitch1_label, pitch2_label, pitch3_label, 
                                  power_label])
    
    # plt.show()
    plt.savefig(full_path)
    plt.close()


def mix_pitch_plot(dataset, turbine_code, file_path):
    """
    绘制风速与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """
    import seaborn as sns

    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    target_data = dataset[[wind_speed_label, pitch1_label, pitch2_label, pitch3_label, power_label]]
    target_data[power_label] = target_data[power_label] / 1000
    # target_data.set_index(wind_speed_label)
    target_data.sort_values(by=wind_speed_label, axis=0, ascending=True, inplace=True)

    #
    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "桨距角$°$"
    title = "变桨控制分析" + "   " + turbine_code
    
    file_name = "{}_pitch.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    # 
    fig, ax = plt.subplots()
    #? hue="label": 标记异常数据与否
    g = sns.scatterplot(data=target_data, x=wind_speed_label, y=power_label, 
                        hue=pitch1_label, size=pitch1_label, ax=ax)
    
    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # 绘制线性拟合曲线
    # ax.plot(target_data[wind_speed_label], target_data[pitch1_label], 'r--')
    # ax.plot(target_data[wind_speed_label], target_data[pitch2_label], '-', lw=2, color='blue')
    # ax.plot(target_data[wind_speed_label], target_data[pitch3_label], '*', lw=2, color='yellow')

    # 绘制散点图
    ax.scatter(target_data[wind_speed_label], target_data[pitch1_label], marker='v', alpha=0.3, s=15, c='green')
    ax.scatter(target_data[wind_speed_label], target_data[pitch2_label], marker='v', alpha=0.3, s=10, c='blue')
    ax.scatter(target_data[wind_speed_label], target_data[pitch3_label], marker='v', alpha=0.3, s=5, c='yellow')
    
    # plt.show()
    plt.savefig(full_path)
    plt.close()


def speed_pitch_plot(dataset, turbine_code, file_path):
    """
    绘制风速与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """

    # target_data = dataset[[wind_speed_label, pitch1_label, pitch2_label, pitch3_label, power_label]] #
    # target_data.sort_values(by=wind_speed_label, axis=0, ascending=True, inplace=True)

    # 桨距角1
    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "桨距角1$°$"
    title = "风速与桨距角分析" + "   " + turbine_code
    
    file_name = "{}_speed_p1.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    curve_plot(dataset, wind_speed_label, pitch1_label, xlabel, ylabel, title, full_path,
               hue=power_label, size=power_label)
    
    # 桨距角2
    ylabel = "桨距角2$°$"
    file_name = "{}_speed_p2.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)
    curve_plot(dataset, wind_speed_label, pitch2_label, xlabel, ylabel, title, full_path,
               hue=power_label, size=power_label)

    # 桨距角3
    ylabel = "桨距角3$°$"
    file_name = "{}_speed_p3.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)
    curve_plot(dataset, wind_speed_label, pitch3_label, xlabel, ylabel, title, full_path,
               hue=power_label, size=power_label)


def speed_pitch_plot_x(dataset, turbine_code, file_path):
    """
    绘制风速与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """

    # 桨距角1
    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "桨距角$°$"
    title = "风速与桨距角分析" + "   " + turbine_code
    
    # 绘图和保存文件
    file_name = "speed_pitch_{}.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    curve_plot(dataset, wind_speed_label, pitch1_label, xlabel, ylabel, title, full_path,
               hue=power_label, size=power_label)


def power_pitch_plot(dataset, turbine_code, file_path):
    """
    绘制功率与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """

    # target_data.sort_values(by=power_label, axis=0, ascending=True, inplace=True)
    xlabel = "功率/(kW)"
    title = "功率与桨距角分析" + "   " + turbine_code

    # 桨距角1
    ylabel = "桨距角1$°$"
    file_name = "{}_power_p1.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)
    curve_plot(dataset, power_label, pitch1_label, xlabel, ylabel, title, full_path,
               hue=wind_speed_label, size=wind_speed_label)
    
    # 桨距角2
    ylabel = "桨距角2$°$"
    file_name = "{}_power_p2.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)
    curve_plot(dataset, power_label, pitch2_label, xlabel, ylabel, title, full_path,
               hue=wind_speed_label, size=wind_speed_label)
    
    # 桨距角3
    ylabel = "桨距角3$°$"
    file_name = "{}_power_p3.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)
    curve_plot(dataset, power_label, pitch3_label, xlabel, ylabel, title, full_path,
               hue=wind_speed_label, size=wind_speed_label)


def power_pitch_plot_x(dataset, turbine_code, file_path):
    """
    绘制功率与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """

    xlabel = "功率/(kW)"
    title = "功率与桨距角分析" + "   " + turbine_code

    # 绘图和保存文件
    ylabel = "桨距角$°$"
    file_name = "power_pitch_{}.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)
    curve_plot(dataset, power_label, pitch1_label, xlabel, ylabel, title, full_path,
               hue=wind_speed_label, size=wind_speed_label)


def pitch_power_plot_x(dataset, turbine_code, file_path):
    """
    绘制桨距角与功率关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """

    xlabel = "桨距角1$°$"
    ylabel = "功率/(kW)"
    title = "桨距角与功率分析" + "   " + turbine_code

    # 绘图和保存文件
    file_name = "pitch_power_{}.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)
    curve_plot(dataset, pitch1_label, power_label, xlabel, ylabel, title, full_path,
               hue=wind_speed_label, size=wind_speed_label)


def bin_pitch_power_curve(dataset, pitch_label):
    """Binned Pitch angle checks
    对功率数据分仓分析变桨角度曲线

    Args:
        dataset (dataframe): 时序数据集
        pitch_label (str): 变桨数据列名称

    Returns:
        DataFrame: 拟合后的功率-变桨角度分仓曲线
    """

    # *** ---------- 1. power分仓binning ----------
    power_bins = np.arange(0, np.ceil(dataset[power_label].max()/100.0)*100, 50)
    power_labels = [x for x in power_bins[1:]]

    dataset[power_bin_label] = pd.cut(dataset[power_label], bins=power_bins, labels=power_labels)

    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    pitch_mean, pitch_std = binning_proc(dataset, power_labels, power_bin_label, pitch_label)

    '''
    pitch_mean = np.ones(len(power_labels)) * np.nan
    pitch_std = np.ones(len(power_labels)) * np.nan
    for index, power_bin_item in enumerate(power_labels):
        bin_data = dataset[dataset[power_bin_label] == power_bin_item]
        
        pitch_mean[index] = bin_data[pitch_label].mean()
        pitch_std[index] = bin_data[pitch_label].std()

    # 插值
    pitch_mean = pd.Series(data=pitch_mean).interpolate(method="linear").bfill().values
    pitch_std = pd.Series(data=pitch_std).interpolate(method="linear").bfill().values
    '''

    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    pitch_power_bin_df = pd.DataFrame()
    pitch_power_bin_df[power_bin_label] = power_labels
    pitch_power_bin_df['pitch'] = pitch_mean
    pitch_power_bin_df['pitch_std'] = pitch_std

    return pitch_power_bin_df


def bin_pitch_windspeed_curve(dataset, pitch_label):
    """Binned Pitch angle checks
    对风速数据分仓分析变桨角度曲线

    Args:
        dataset (dataframe): 时序数据集
        pitch_label (str): 变桨数据列名称

    Returns:
        DataFrame: 拟合后的功率-变桨角度分仓曲线
    """

    # *** ---------- 1. wind speed分仓binning ----------
    wind_speed_bins = np.arange(0, np.ceil(dataset[wind_speed_label].max()), 0.25)
    # wind_speed_labels = ['-'.join(map(str,(x,y))) for x, y in zip(wind_speed_bins[:-1], wind_speed_bins[1:])]
    wind_speed_labels = [x for x in wind_speed_bins[1:]]

    dataset[wind_speed_bin_label] = pd.cut(dataset[wind_speed_label], bins=wind_speed_bins, 
                                       labels=wind_speed_labels)

    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    pitch_mean, pitch_std = binning_proc(dataset, wind_speed_labels, wind_speed_bin_label, pitch_label)

    '''
    pitch_mean = np.ones(len(wind_speed_labels)) * np.nan
    pitch_std = np.ones(len(wind_speed_labels)) * np.nan
    for index, windspeed_bin_item in enumerate(wind_speed_labels):
        bin_data = dataset[dataset[wind_speed_bin_label] == windspeed_bin_item]
        
        pitch_mean[index] = bin_data[pitch_label].mean()
        pitch_std[index] = bin_data[pitch_label].mean()

    # 插值
    pitch_mean = pd.Series(data=pitch_mean).interpolate(method="linear").bfill().values
    pitch_std = pd.Series(data=pitch_std).interpolate(method="linear").bfill().values
    '''

    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    pitch_windspeed_bin_df = pd.DataFrame()
    pitch_windspeed_bin_df[wind_speed_bin_label] = wind_speed_labels
    pitch_windspeed_bin_df['pitch'] = pitch_mean
    pitch_windspeed_bin_df['pitch_std'] = pitch_std

    return pitch_windspeed_bin_df


def bin_pitch_genspeed_curve(dataset, pitch_label):
    """Binned Pitch angle checks
    对发电机转速数据分仓分析变桨角度曲线

    Args:
        dataset (dataframe): 时序数据集
        pitch_label (str): 变桨数据列名称

    Returns:
        DataFrame: 拟合后的功率-变桨角度分仓曲线
    """

    # *** ---------- 1. generator speed 分仓binning ----------
    gen_speed_bins = np.arange(0, np.ceil(dataset[gen_speed_label].max()/100.0)*100, 10)
    gen_speed_labels = [x for x in gen_speed_bins[1:]]

    dataset[gen_speed_bin_label] = pd.cut(dataset[gen_speed_label], bins=gen_speed_bins, labels=gen_speed_labels)

    # *** ---------- 2. 分仓binning拟合偏航角度曲线 ----------
    pitch_mean, pitch_std = binning_proc(dataset, gen_speed_labels, gen_speed_bin_label, pitch_label)

    # *** ---------- 3. 组装binning分仓曲线数据 ----------
    pitch_genspeed_bin_df = pd.DataFrame()
    pitch_genspeed_bin_df[gen_speed_bin_label] = gen_speed_labels
    pitch_genspeed_bin_df['pitch'] = pitch_mean
    pitch_genspeed_bin_df['pitch_std'] = pitch_std

    return pitch_genspeed_bin_df


def bin_pitch_power_plot(bin_df, turbine_code, file_path):
    """功率数据分仓变桨角度曲线绘图

    Args:
        bin_df (dataframe): 分仓数据集
        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
    """
    
    title = "{}_pitch_{}".format(power_label, turbine_code)
    xlabel = "功率 [$kW$]"

    # bin_label (str): 数据集分仓列名称（标签名称）
    bin_pitch_plot(bin_df, power_bin_label, file_path, xlabel, title)


def bin_pitch_windspeed_plot(bin_df, turbine_code, file_path):
    """风速数据分仓桨距角曲线绘图

    Args:
        bin_df (dataframe): 分仓数据集
        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
    """
    
    title = "{}_pitch_{}".format(wind_speed_label, turbine_code)
    xlabel = "风速 [m·s$^{-1}$]"

    bin_pitch_plot(bin_df, wind_speed_bin_label, file_path, xlabel, title)


def bin_pitch_genspeed_plot(bin_df, turbine_code, file_path):
    """发电机转速数据分仓桨距角曲线绘图

    Args:
        bin_df (dataframe): 分仓数据集
        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
    """
    
    title = "{}_pitch_{}".format(gen_speed_label, turbine_code)
    xlabel = "转速 [r·min$^{-1}$]"

    bin_pitch_plot(bin_df, gen_speed_bin_label, file_path, xlabel, title)


def bin_pitch_plot(bin_df, bin_label, file_path, xlabel, title):
    """绘制基于不同标签的桨距角分仓分析图像

    Args:
        bin_df (dataframe): 分仓数据集
        bin_label (str): 数据集分仓列名称（标签名称）
        file_path (str): 图像文件完整路径
        xlabel (str): x轴 标注
        title (str): 图像标题
    """
    import seaborn as sns

    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure()

    # , label="XXX_pitch binning"
    plt.plot(bin_df[bin_label], bin_df['pitch'])
    plt.errorbar(bin_df[bin_label], bin_df['pitch'], yerr=bin_df['pitch_std'], 
                 fmt='o', ecolor='orangered', color='b', elinewidth=2, capsize=4,
                 markersize=4, mfc='yellow', mec='green', mew=0.5)
    
    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel('桨距角 [$°$]')
    plt.title(title)

    # 绘图和保存文件
    '''
    file_name = "{}.png".format(title)
    plot_save(file_path, file_name)
    '''
    plt.show()


def all_bin_pitch_power_plot(bin_df, file_path):
    """功率数据分仓变桨角度曲线绘图【所有机组】

    Args:
        bin_df (dataframe): 分仓数据集
        file_path (str): 图像文件完整路径
    """

    xlabel = '功率 [$kW$]'
    ylabel = '桨距角 [$°$]'
    title = "{}_pitch".format(power_label)

    common_bin_pitch_plot(bin_df, power_bin_label, xlabel, ylabel, title, file_path)


def all_bin_pitch_windspeed_plot(bin_df, file_path):
    """风速数据分仓变桨角度曲线绘图【所有机组】

    Args:
        bin_df (dataframe): 分仓数据集
        file_path (str): 图像文件完整路径
    """
    
    xlabel = '风速 [m·s$^{-1}$]'
    ylabel = '桨距角 [$°$]'
    title = "{}_pitch".format(wind_speed_label)

    common_bin_pitch_plot(bin_df, wind_speed_bin_label, xlabel, ylabel, title, file_path)


def all_bin_pitch_genspeed_plot(bin_df, file_path):
    """发电机转速数据分仓变桨角度曲线绘图【所有机组】

    Args:
        bin_df (dataframe): 分仓数据集
        file_path (str): 图像文件完整路径
    """
    
    xlabel = '转速 [r·min$^{-1}$]'
    ylabel = '桨距角 [$°$]'
    title = "{}_pitch".format(gen_speed_label)

    common_bin_pitch_plot(bin_df, gen_speed_bin_label, xlabel, ylabel, title, file_path)


def common_bin_pitch_plot(bin_df, bin_var, xlabel, ylabel, title, file_path):
    """通用的针对变桨桨距角的分仓曲线绘制函数
    #! 参见 models.bin_analysis.quant.cloud.bin_analysis_tool 的"bin_curve_plot"方法

    Args:
        bin_df (dataframe): 分仓数据集
        bin_var (str): 分仓变量【数据列名称】
        xlabel (str): x轴标签
        ylabel (str): y轴标签
        title (str): 图像标题
        file_path (str): 图像文件完整路径
    """
    import seaborn as sns

    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False

    plt.figure(figsize=(16,10))

    sns.lineplot(data=bin_df, x=bin_var, y="pitch", hue=turbine_code_label, 
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


