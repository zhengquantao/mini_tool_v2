#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 绘图工具函数
# 功能描述：绘制散点图、曲线等工具函数
#
# 基于seaborn、matplotlib的绘图工具函数
# > 1. 曲线
# > 2. 散点
# > 3. 其它
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
import logging

import numpy as np
import pandas as pd

# import statsmodels.api as sm
from scipy.optimize import curve_fit

import seaborn as sns

from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from mpl_toolkits.mplot3d import Axes3D

#? 中文乱码问题
font = fm.FontProperties(fname='微软雅黑.ttf')
#? 字体设置：SimHei
plt.rcParams["font.sans-serif"]=["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"]=False

plt.rcParams.update(
    {
        # 'text.usetex': False,
        'mathtext.fontset': 'stix',
        'font.family': 'serif',
        "font.serif": ['Microsoft YaHei'],
    }
)

#
from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, wind_speed_bin_label, mark_label
from models.bin_analysis.quant.cloud.wind_base_tool import plot_save


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
# 绘图辅助函数
# ***
# --------------------------------------------------------------------

def bin_curve_plot(data, col_x, col_y, xlabel, ylabel, title, file_path, 
                   bin_df, hue=None, size=None):
    """
    按照指定数据列绘制曲线图 【单台风机分仓曲线】
    包括散点图、曲线和偏差展示
    
    :param data: 时序数据集
    :param col_x: x数据列名
    :param col_y: y数据列名

    :param xlabel: x坐标名称
    :param ylabel: y坐标名称
    :param title: 图像标题

    :param file_path: 图像文件完整路径
    :param bin_df (dataframe): 分仓数据集
    
    :return:
    """

    plt.figure() # figsize=(12, 8)
    #? hue="label": 标记异常数据与否 , kind="line" 
    #? hue_order = ('down','normal','up')
    sns.relplot(data=data, x=col_x, y=col_y, hue=hue, size=size, alpha=0.5) # hue_order='down', 
    # sns.lineplot(data=data, x=col_x, y=col_y, hue=hue, size=size)

    plt.plot(bin_df[col_x], bin_df[col_y])
    plt.errorbar(bin_df[col_x], bin_df[col_y], yerr=bin_df['{}_std'.format(col_y)], 
                 fmt='o', ecolor='orangered', color='b', elinewidth=2, capsize=4,
                 markersize=4, mfc='yellow', mec='green', mew=0.5, alpha=0.2)
    
    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    #
    plt.tight_layout()
    
    # plt.show()
    plt.savefig(file_path)
    plt.close()


def curve_plot(data, col_x, col_y, xlabel, ylabel, title, file_path, hue=None, size=None, alpha=0.5):
    """
    按照指定数据列绘制曲线图
    
    :param data: 时序数据集
    :param col_x: x数据列名
    :param col_y: y数据列名 [str or list]

    :param xlabel: x坐标名称
    :param ylabel: y坐标名称
    :param title: 图像标题

    :param file_path: 图像文件完整路径
    
    :return:
    """

    plt.figure()

    '''
    #? hue="label": 标记异常数据与否 , kind="line" 
    #? hue_order = ('down','normal','up')
    sns.relplot(data=data, x=col_x, y=col_y, hue=hue, size=size, alpha=alpha) # hue_order='down', 
    # sns.lineplot(data=data, x=col_x, y=col_y, hue=hue, size=size)
    '''

    legend_flag = False
    if isinstance(col_y, list):
        legend_flag = True
        for item in col_y:
            sns.lineplot(data=data, x=col_x, y=item, hue=hue, size=size, alpha=alpha, label=item)
    else:
        sns.relplot(data=data, x=col_x, y=col_y, hue=hue, size=size, alpha=alpha)
    
    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    #? 要显示图例必须在sns绘图函数（本例lineplot）添加"label"参数
    #? 否则图例不会显示内容
    if legend_flag:
        plt.legend()
        # ax = plt.gca()
        # ax.legend()

    plt.tight_layout()
    
    # plt.show()
    plt.savefig(file_path)
    plt.close()


def scatter_plot(data, col_x, col_y, xlabel, ylabel, title, file_path, hue=None, size=None):
    """
    按照指定数据列绘制散点图
    
    :param data: 时序数据集
    :param col_x: x数据列名
    :param col_y: y数据列名

    :param xlabel: x坐标名称
    :param ylabel: y坐标名称
    :param title: 图像标题

    :param file_path: 图像文件完整路径
    
    :return:
    """

    plt.figure()
    #? hue="label": 标记异常数据与否
    sns.scatterplot(data=data, x=col_x, y=col_y, hue=hue, size=size)
    
    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    
    # plt.show()
    plt.savefig(file_path)
    plt.close()


def hue_scatter_plot(data, col_x, col_y, xlabel, ylabel, title, file_path, hue=None, size=None):
    """
    按照指定数据列绘制散点图
    
    :param data: 时序数据集
    :param col_x: x数据列名
    :param col_y: y数据列名

    :param xlabel: x坐标名称
    :param ylabel: y坐标名称
    :param title: 图像标题

    :param file_path: 图像文件完整路径
    
    :return:
    """
    
    fig, ax = plt.subplots()
    g = sns.scatterplot(
        data=data, x=col_x, y=col_y, hue=hue, size=size,
        sizes=(20, 200), legend="full", ax=ax)
    
    #
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    #? bbox_to_anchor: 图例相对与图的位置，倍数关系
    g.legend(loc='upper right', bbox_to_anchor=(1.4, 1.0), ncol=1)

    if hue is not None:
        norm = plt.Normalize(data[hue].min(), data[hue].max())
        cmap = sns.cubehelix_palette(light=0.35, as_cmap=True)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])

        # cax = fig.add_axes([ax.get_position().x1+0.05, ax.get_position().y0, 
        # 0.06, ax.get_position().height / 2])
        # ax.figure.colorbar(sm, cax=cax)
        ax.figure.colorbar(sm)

    # plt.show()
    plt.savefig(file_path)
    plt.close()


def plot_heatmap(df, vars, turbine_code, file_path):
    """
    To plot the time series data.
    Examples: plot_timeseries(data, 'real_time', 'power')
    
    input: 
        df(DataFrame): Pandas DataFrame data to plot
        vars(list): the list of variables to plot
        turbine_code(string): the turbine code or ID to plot
        file_path(string): the file folder path to save the plot
    output: 
        none
    """
    
    plt.figure()
    sns.heatmap(df[vars].corr(), annot=True)
    
    plt.tight_layout()
    
    # plt.show()
    file_name = "heatmap_{}.png".format(turbine_code)
    plot_save(file_path, file_name)


def plot_timeseries(df, time_label, target_label):
    """
    To plot the time series data.
    Examples: plot_timeseries(data, 'real_time', 'power')
    
    input: 
        df(DataFrame): Pandas DataFrame data to plot
        time_label(string): the name of timestamp to plot
        target_label(string): the name of the variable to plot
    output: 
        none
    """

    fig, ax = plt.subplots(figsize=(16,3))

    ax.scatter(df[time_label], df[target_label])
    ax.set_ylabel(target_label)

    plt.show()



def plot_yaw_timeseries(df, time_label, yaw_oper_label, nacelle_dir_label):
    """
    To plot the time series data.
    Examples: plot_timeseries(data, 'real_time', 'power')
    
    input: 
        df(DataFrame): Pandas DataFrame data to plot
        time_label(string): the name of timestamp to plot
        yaw_oper_label(string): the variable name of yaw operation
        nacelle_dir_label(string): the variable name of nacelle direction
    output: 
        none
    """

    fig, ax = plt.subplots(figsize=(16,3))
    
    ax.scatter(df[time_label], df[yaw_oper_label], color='r')
    ax.plot(df[time_label], df[nacelle_dir_label], color='g')
    ax.plot(df[time_label], df['nacelle_position'], color='b')
    ax.set_ylabel(yaw_oper_label)
    
    plt.show()


def plot_ti_timeseries(df, time_label, yaw_oper_label, nacelle_dir_label):
    """
    To plot the time series data.
    Examples: plot_timeseries(data, 'real_time', 'power')
    
    input: 
        df(DataFrame): Pandas DataFrame data to plot
        time_label(string): the name of timestamp to plot
        yaw_oper_label(string): the variable name of yaw operation
        nacelle_dir_label(string): the variable name of nacelle direction
    output: 
        none
    """

    plt.figure(figsize=(16,3))

    plt.plot(df[time_label], df[yaw_oper_label], color='b')
    plt.plot(df[time_label], df[nacelle_dir_label], color='g')

    plt.xlabel(time_label)
    plt.ylabel("Turbulence Intensity")
    plt.legend()
    
    plt.show()


def draw_time_violinplot(turbine_data, vars_label, vars_legend, time_label, time_tick_labels,
                         turbine_code, file_path, times_order=None, fig_size=(16, 16), orient="v"):
    """
    展示变量的violinplot【箱形图与核密度图的结合体】
    核心：多风机数据分行展示【多风机】【多变量】

    input: 
        turbine_data(dataframe): the dataframe of specific wind turbine to plot
        vars_label(list): the list of variables to plot
        vars_legend(list): the list of the variable names to be shown in the legend
        time_label(string): the turbine code to display
        time_tick_labels(list): the list of the time group name, to be displayed in x-tick
        turbine_code(string): the turbine code or ID to plot
        file_path(string): the file folder path to save the plot
        times_order(list): the list of the time group (e.g. month list) in order
        fig_size(tuple): the figure size 
        orient(string): "v" for vertical orientation, "h" for horizontal orientation
    output: 
        none
    """
    
    fig, ax = plt.subplots(len(vars_label), figsize=fig_size)
    
    if orient == "v":
        for i in range (0, len(vars_label)):
            sns.violinplot(data=turbine_data, y=vars_label[i], x=time_label, 
                           orient=orient, ax=ax[i], order=times_order)
            ax[i].set(ylabel=vars_legend[i], xlabel=time_label)
            ax[i].set_xticklabels(time_tick_labels)

    if orient == "h":
        for i in range (0, len(vars_label)):
            sns.violinplot(data=turbine_data, x=vars_label[i], y=time_label, 
                           orient=orient, ax=ax[i], order=times_order)
            ax[i].set(xlabel=vars_legend[i], ylabel=time_label)
            ax[i].set_yticklabels(time_tick_labels)

    #
    plt.tight_layout()
    
    # plt.show()
    file_name = "{}_violinplot_{}.png".format(time_label, turbine_code)
    plot_save(file_path, file_name)


def draw_violinplot(df, vars_label, vars_legend, turbines_order, turbine_tick_labels,
                    turbine_label='turbine_code', fig_size=(16, 16), orient="v"):
    """
    展示变量的violinplot【箱形图与核密度图的结合体】
    核心：多风机数据分行展示【多风机】【多变量】

    input: 
        df(dataframe): the dataframe to plot
        vars_label(list): the list of variables to plot
        vars_legend(list): the list of the variable names to be shown in the legend
        turbines_order(list): the list of the turbine IDs in order
        turbine_tick_labels(list): the list of the turbine IDs name, to be displayed in x-tick
        turbine_label(string): the turbine codes (IDs) column label in the dataframe
        fig_size(tuple): the figure size
        orient(string): "v" for vertical orientation, "h" for horizontal orientation
    output: 
        none
    """
    
    fig, ax = plt.subplots(len(vars_label), figsize=fig_size)
    
    if orient == "v":
        for i in range (0, len(vars_label)):
            sns.violinplot(data=df, y=vars_label[i], x=turbine_label, orient=orient, 
                           ax=ax[i], order=turbines_order)
            ax[i].set(ylabel=vars_legend[i], xlabel='Turbine Code')
            ax[i].set_xticklabels(turbine_tick_labels)

    if orient == "h":
        for i in range (0, len(vars_label)):
            sns.violinplot(data=df, x=vars_label[i], y=turbine_label, orient=orient, 
                           ax=ax[i], order=turbines_order)
            ax[i].set(xlabel=vars_legend[i], ylabel='Turbine Code')
            ax[i].set_yticklabels(turbine_tick_labels)

    plt.show()


def plot_vars(df, turbine_code, ws_range, x_var, figsize=(18,3)):
    """
    展示变量和功率的关系【x轴是所选的变量，y轴是功率数据】
    核心：仅仅展示指定风速范围数据【风速区间】【y变量均是功率】

    input:
        df(dataframe): the dataframe to plot
        turbine_code(string): the turbine code or ID to plot
        ws_range(tuple): the range of wind speed to plot, e.g. (1, 10) 
        x_var(list): the list of variables for the x-axis. if 3 variables are given, there will be 3 plots
        figsize(tuple): the figure size 
    output: 
        none
    """

    df_plot = df[(df['turbine_code']==turbine_code) 
                 & (df[wind_speed_label]>=ws_range[0]) & (df[wind_speed_label]<=ws_range[1])] 

    fig, ax = plt.subplots(1, len(x_var), figsize=(18,3), sharey='row')

    #? x轴是所选的变量，y轴是功率数据
    for c in range(len(x_var)):
        sns.scatterplot(x=df_plot[x_var[c]], y=df_plot[power_label], ax=ax[c], s=1, edgecolor=None)
        ax[c].set_xlabel(x_var[c]) 
        ax[c].set_ylabel("Power") 

    plt.show()


# --------------------------------------------------------------------
# ***
# 3D绘图展示
# ***
# --------------------------------------------------------------------

def scatter_3d_plot(dataset, vars_list, file_path, xlabel=None, ylabel=None, zlabel=None,
                    title=None, color_label=None):
    """
    绘制三个变量之间的3D分析展示 图像 【三维展示】【通用函数】
    
    :param dataset: 时序数据集
    :param vars_list: x、y、z变量名称列表
    :param file_path: 图像文件完整路径

    :param xlabel: x坐标名称
    :param ylabel: y坐标名称
    :param zlabel: z坐标名称
    :param title: 图像标题

    :param color_label: 散点的颜色变量名称
    
    :return:
    """

    #? azim是绕z轴旋转的角度
    #? elev是绕y轴旋转的角度
    #? 默认值：azim=-60, elev=30
    figsize=(7, 5)
    fig = plt.figure(figsize=figsize)
    
    #! 存在两种方式绘制3D图形
    ax = Axes3D(fig, azim=120, elev=10) # azim=-60
    # ax = fig.gca(projection='3d')
    # ax.view_init(elev=10,azim=120)
    if color_label is not None:
        ax.scatter(dataset[vars_list[0]], dataset[vars_list[1]], dataset[vars_list[2]], 
                   c=dataset[color_label], cmap=cm.coolwarm)
    else:
        ax.scatter(dataset[vars_list[0]], dataset[vars_list[1]], dataset[vars_list[2]], 
                   cmap=cm.coolwarm)
    
    ''''''
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    # ax.legend() # loc="upper right"
    fig.add_axes(ax)
    
    # fig.legend(loc="upper right")
    plt.title(title)
    plt.tight_layout()
    
    # plt.show()
    plt.savefig(file_path)
    plt.close()


