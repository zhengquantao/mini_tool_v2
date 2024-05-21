#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 转矩控制——叶尖速比优化分析
# 功能描述：为实现发电量提升目标，对机组转矩控制、叶尖速比控制进行分析、诊断
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
import math

import logging

import numpy as np
import pandas as pd

# import statsmodels.api as sm
from scipy.optimize import curve_fit

#
import warnings
warnings.filterwarnings("ignore")

#
from models.bin_analysis.quant.cloud.file_dir_tool import create_dir

from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, wind_speed_bin_label, mark_label

from models.bin_analysis.quant.cloud.plot_tool import curve_plot, scatter_plot, hue_scatter_plot



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
# ** 分析结果标签 **
torque_label = "torque"
torque_coef_label = "torque_coef"

thrust_coef_label = "thrust_coef"

tsr_label = "TSR"

# K_opt
# ** 转矩增益系数 **
k_label = "K"

power_coef_label = "C_p"


# --------------------------------------------------------------------
# ***
# 分析处理
# ***
# --------------------------------------------------------------------

def cp_calc(dataset, cp_factor=1.0, air_density_tag=None, rotor_radius=None, inplace=False):
    """风能利用系数计算
    #? cp_factor 和 rotor_radius两个参数二选一，优先采用 rotor_radius数值

    Args:
        dataset (DataFrame): 时序数据集
        cp_factor (float): _description_
        air_density_tag (str, optional): 空气密度标签. Defaults to None.
        rotor_radius (float, optional): 叶轮半径. Defaults to None.
        inplace (bool): 是否增加对应数据列

    Returns:
        list: 风能利用系数 列表
    """

    if rotor_radius is not None:
        cp_factor = 0.5 * math.pi * pow(rotor_radius, 2) / 1000

    # **  风能利用系数计算 **
    if air_density_tag is not None:
        cp_list = dataset.apply(lambda row: row[power_label] /
                                 (cp_factor * row[air_density_tag] * pow(row[wind_speed_label], 3)), axis=1)
    else:
        cp_list = dataset.apply(lambda row: row[power_label] /
                                 (cp_factor * 1.225 * pow(row[wind_speed_label], 3)), axis=1)
    
    if inplace:
        dataset[power_coef_label] = cp_list
    
    return cp_list


def gen_torque_calc(dataset, inplace=False):
    """发电机转矩计算

    Args:
        dataset (DataFrame): 时序数据集
        inplace (bool): 是否增加对应数据列

    Returns:
        list: 发电机转矩 列表
    """

    # torque_list = 9549.297 * dataset.loc[:,power_label].divide(dataset.loc[:,gen_speed_label])
    torque_list = 9549.297 * dataset.apply(lambda row: row[power_label]/row[gen_speed_label], axis=1)

    if inplace:
        # dataset.insert(len(dataset.columns), torque_label, torque_list)
        dataset[torque_label] = torque_list

    return torque_list


def gen_torque_coef_calc(dataset, rotor_radius, inplace=False):
    """发电机转矩系数 计算

    Args:
        dataset (DataFrame): 时序数据集
        inplace (bool): 是否增加对应数据列

    Returns:
        list: 发电机转矩系数 列表
    """

    area_size = math.pi * pow(rotor_radius, 2)
    factor = 0.5 * area_size * rotor_radius
    torque_coef_list = dataset.apply(lambda row: row[torque_label] / 
        (factor * row[air_density_label] * pow(row[wind_speed_label], 2)), axis=1)

    if inplace:
        # dataset.insert(len(dataset.columns), torque_coef_label, torque_coef_list)
        dataset[torque_coef_label] = torque_coef_list

    return torque_coef_list


def thrust_coef_by_cp_func(power_coef):
    """基于CP风能利用系数计算推力系数
    #? Specifically, the thrust coefficient and power coefficient equations are here:
    #? github.com/NREL/ssc/blob/7b84c5b5eb73ab77bc72e081277c6c27a3a00f31/shared/lib_windwakemodel.cpp#L123

    Args:
        power_coef (float): 风能利用系数

    Returns:
        float: 推力系数
    """

    temp = -1.453989e-2 + 1.473506*power_coef - 2.330823*pow(power_coef, 2) + 3.885123*pow(power_coef, 3)
    return round(max(0.0, temp), 4)


def thrust_coef_calc(dataset, rotor_radius, inplace=False):
    """推力系数 计算 [Thrust coefficient]

    #? 风机推力系数是衡量空气动力性能的一个重要指标，它是指在同样的进口面积和转速
    #? 下，风机所产生的推力和风机所需的能量之间的比值。风机推力系数一般用Ct表示。

    #?【计算方法】
    #? 风机推力系数的计算方法为：Ct=T/(0.5*rho*A*V^2)，其中，T为风机产生的推力，
    #? rho为空气密度，A为进口面积，V为风机前进速度。
    #? 风机的产生的推力可以通过测试或者计算得到，而风机所需的能量可以通过计算功率
    #? 来得到，即：P=T*V。因此，风机推力系数也可以写成：Ct=2P/(rho*A*V^3)。

    #?【作用】
    #? 风机推力系数可以反映出风机空气动力性能的好坏，直接影响风机的性能。推力系数越
    #? 大，说明风机的推力越大，风能利用效率越高；反之，则说明风机的能量利用效率越低。
    #? 因此，在设计和选择风机时，需要根据实际需求选择适当的风机推力系数。
    
    #?【总结】
    #? 在风机领域，风机推力系数是一个非常重要的指标，它可以反映出风机空气动力性能的
    #? 好坏，同时也可以影响风机的能量利用效率。

    Args:
        dataset (DataFrame): 时序数据集
        inplace (bool): 是否增加对应数据列

    Returns:
        list: 发电机推力系数 列表
    """

    '''
    #TODO:
    area_size = math.pi * pow(rotor_radius, 2)

    # Ct=T/(0.5*rho*A*V^2)
    factor = 0.5 * area_size
    thrust_coef_list = dataset.apply(lambda row: row[thrust_label] / 
        (factor * row[air_density_label] * pow(row[wind_speed_label], 2)), axis=1)
    '''
    
    #? Specifically, the thrust coefficient and power coefficient equations are here:
    #? github.com/NREL/ssc/blob/7b84c5b5eb73ab77bc72e081277c6c27a3a00f31/shared/lib_windwakemodel.cpp#L123
    thrust_coef_list = dataset.apply(lambda row: thrust_coef_by_cp_func(row[power_coef_label]), axis=1)

    if inplace:
        # dataset.insert(len(dataset.columns), thrust_coef_label, thrust_coef_list)
        dataset[thrust_coef_label] = thrust_coef_list

    return thrust_coef_list


def tsr_calc(dataset, gear_ratio, rotor_radius, inplace=False):
    """
    基于SCADA数据计算叶尖速比TSR 【基于发电机转速】
    
    :param dataset: 时序数据集
    :param gear_ratio: 齿轮箱传动比
    :param rotor_radius: 叶轮半径

    :param inplace (bool): 是否增加对应数据列
    
    :return: (list) 叶尖速比 列表
    """

    #? 没有考虑齿轮箱的传动比，现在的速度是发动机转速，数值偏大
    #? 机型的叶轮直径
    #? 发电机和齿轮箱之间传动比是 1:1
    #! Tip speed ratio (TSR) = 风力机旋转角速度(rad/s) ω * 风力机风轮半径(m) R / 风速 V
    #! Tip speed ratio (TSR) = [ pi * 风力机旋转速度(r/min) n * 风力机风轮半径(m) R ] / [30 * 风速 V]
    #? 基于发电机转速的叶尖速比计算
    tsr_factor = math.pi * rotor_radius / gear_ratio / 30
    tsr_list = tsr_factor * dataset.loc[:, gen_speed_label].divide(dataset.loc[:, wind_speed_label])
    
    # 增加 叶尖速比-数据列 到时序数据集
    if inplace:
        # dataset.insert(len(dataset.columns), tsr_label, tsr_list)
        dataset[tsr_label] = tsr_list

    return tsr_list


def tsr_analysis(dataset, turbine_code, gear_ratio, rotor_radius, dir_path=None, air_density_tag=None):
    """
    基于SCADA数据的叶尖速比分析
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param gear_ratio: 齿轮箱传动比
    :param rotor_radius: 叶轮半径

    :param dir_path: 存储路径
    :param air_density_tag: 空气密度标签
    
    :return:
    """

    # *** ---------- 1 计算叶尖速比TSR ----------
    tsr_calc(dataset, gear_ratio, rotor_radius, inplace=True)

    # *** ---------- 2 拆选清除异常值【外点】 ----------
    #TODO: 根据具体情况设置叶尖速比最大值，筛除外点异常值
    dataset = dataset[dataset[tsr_label] <= 20]
    
    # *** ---------- 3 绘图并保存文件 ----------
    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "叶尖速比"
    title = "叶尖速比分析" + "   " + turbine_code

    file_path = create_dir("tsr_img", dir_path)
    file_name = "{}.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    scatter_plot(dataset, wind_speed_label, tsr_label, xlabel, ylabel, title, full_path)

    # *** ---------- 4 考虑空气密度-绘图并保存文件 ----------
    #! 必须要有当地实时空气密度数据
    if air_density_tag is not None:
        file_path = create_dir("tsr_ρ_img", dir_path)
        full_path = os.path.join(file_path, file_name)

        hue_scatter_plot(dataset, wind_speed_label, tsr_label, xlabel, ylabel, title,
                         full_path, hue=air_density_tag, size=air_density_tag)
    


def torque_analysis(dataset, turbine_code, dir_path=None, air_density_tag=None):
    """
    基于SCADA数据的转矩诊断分析
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param dir_path: 存储路径
    
    :return:
    """

    # *** ---------- 1 计算转矩torque数据 ----------
    #! 没有考虑齿轮箱的转速比【传动比】
    #? 现在采用的发动机的转速，是不是数值偏大？应该转换到叶轮的转速
    #TODO: 转矩计算修正：当前数值太大
    gen_torque_calc(dataset, inplace=True)
    
    # *** ---------- 2 绘图并保存文件 ----------
    xlabel = "转速/(r·min$^{-1}$)"
    ylabel = "转矩/(N·m)"
    title = "转速-转矩分析" + "   " + turbine_code

    file_path = create_dir("torque_img", dir_path)
    file_name = "{}.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    '''
    target_data = pd.concat([ dataset[(dataset[air_density_tag] == 1.150)],
                          dataset[(dataset[air_density_tag] == 1.200)] ])

    scatter_plot(target_data, generator_speed_label, torque_label, xlabel, ylabel, title, 
                 full_path, hue=air_density_tag, size=air_density_tag)
    '''
    scatter_plot(dataset, gen_speed_label, torque_label, xlabel, ylabel, title, 
                 full_path, hue=air_density_tag, size=air_density_tag)


def k_opt_analysis(dataset, turbine_code, air_density_tag=None, dir_path=None, cp_factor=1.0, rotor_radius=None):
    """
    基于SCADA数据的最优转矩增益系数分析
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param air_density_tag: 空气密度标签
    :param dir_path: 存储路径
    :param cp_factor: 风能利用系数因子
    :param rotor_radius (float, optional): 叶轮半径. Defaults to None.

    :return:
    """

    if rotor_radius is not None:
        cp_factor = 0.5 * math.pi * pow(rotor_radius, 2) / 1000
    
    #! 核心思想：基于运行数据的风电机组转矩控制性能评估
    # dataset = dataset[(dataset[wind_speed_label] >=6) & (dataset[wind_speed_label]<= 7)].reset_index(drop=True)

    # *** ---------- 1 计算转矩torque数据 ----------
    #! 没有考虑齿轮箱的转速比【传动比】
    #? 现在采用的发动机的转速，是不是数值偏大？应该转换到叶轮的转速
    #TODO: 转矩计算修正：当前数值太大
    torque_list = gen_torque_calc(dataset)
    gen_speed_square_list = dataset.loc[:,gen_speed_label].apply(lambda x: pow(2*math.pi*x/60, 2))

    # **  风能利用系数计算 **
    cp_list = cp_calc(dataset, cp_factor, air_density_tag)
    dataset[power_coef_label] = cp_list

    # 
    # ** 转矩增益系数K_a **
    # k_list = [x/y for x, y in zip(torque_list,gen_speed_square_list)]
    k_list = torque_list / gen_speed_square_list
    logger.info(k_list.mean())
    
    #
    ang_speed_square_label = "angular_speed^2"

    dataset[k_label] = k_list
    dataset[torque_label] = torque_list
    dataset[ang_speed_square_label] = gen_speed_square_list

    #! 基于风能利用系数计算筛选数据
    target_data = dataset[(dataset[power_coef_label] <= 0.597) 
                          & (dataset[power_coef_label] >= 0.100) ]
    
    #! 发电机转速筛选
    #TODO: 尖峰项目适用
    target_data = target_data[(target_data[gen_speed_label] <= 1500) 
                              & (target_data[gen_speed_label] >= 1200) ]
    
    # *** ---------- 2 风能利用系数-绘图并保存文件 ----------
    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "风能利用系数$C_p$"
    title = "风能利用系数分析" + "   " + turbine_code
    
    file_path = create_dir("Cp_img", dir_path)
    file_name = "{}.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    target_data.sort_values(by=wind_speed_label,axis=0,ascending=True,inplace=True)

    # 空气密度 与 风能利用系数关系
    curve_plot(target_data, wind_speed_label, power_coef_label, xlabel, ylabel, 
               title, full_path, hue=air_density_tag, size=air_density_tag)
    
    
    # *** ---------- 3 转矩控制-绘图并保存文件 ----------
    xlabel = "发电机转速的平方$ω_g^2$/(rad·s$^-1$)"
    ylabel = "发电机转矩$T_g$/(N·m)"
    title = "发电机转速的平方-转矩关系" + "   " + turbine_code
    
    file_path = create_dir("k_fit_img", dir_path)
    file_name = "{}.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    target_data.sort_values(by=power_coef_label,axis=0,ascending=True,inplace=True)
    linear_fit_scatter_plot(target_data, ang_speed_square_label, torque_label, xlabel, ylabel, 
              title, full_path, hue=power_coef_label, size=power_coef_label)


def torque_coef_proc(dataset, gear_ratio, rotor_radius):
    """
    风轮转矩系数 计算处理逻辑
    
    :param dataset: 时序数据集
    :param gear_ratio: 齿轮箱传动比
    :param rotor_radius: 叶轮半径
    
    :return:
    """

    # *** ---------- 1 计算叶尖速比TSR ----------
    tsr_calc(dataset, gear_ratio, rotor_radius, inplace=True)

    # *** ---------- 2 计算发电机Torque ----------
    gen_torque_calc(dataset, inplace=True)

    # *** ---------- 3 计算风轮转矩系数 ----------
    gen_torque_coef_calc(dataset, rotor_radius, inplace=True)


def thrust_coef_proc(dataset, gear_ratio, rotor_radius):
    """
    推力系数 计算处理逻辑
    
    :param dataset: 时序数据集
    :param gear_ratio: 齿轮箱传动比
    :param rotor_radius: 叶轮半径
    
    :return:
    """

    # *** ---------- 1 计算叶尖速比TSR ----------
    tsr_calc(dataset, gear_ratio, rotor_radius, inplace=True)

    # *** ---------- 2 计算CP系数 ----------
    cp_factor = 0.5 * math.pi * pow(rotor_radius, 2) / 1000
    cp_calc(dataset, cp_factor, air_density_label, inplace=True)
    
    # *** ---------- 3 计算推力系数 ----------
    thrust_coef_calc(dataset, rotor_radius, inplace=True)


def torque_coef_tsr_plot(dataset, turbine_code, dir_path=None):
    """
    风轮转矩系数随叶尖速比的变化曲线
    #? 2009_大型风电机组综合性能评估方法研究_刘昊
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param dir_path: 存储路径
    
    :return:
    """

    # 绘图并保存文件
    xlabel = "叶尖速比"
    ylabel = "风轮转矩系数"
    title = "风轮转矩系数-叶尖速比分析" + "   " + turbine_code

    file_name = "torque_tsr_{}.png".format(turbine_code)
    full_path = os.path.join(dir_path, file_name)

    scatter_plot(dataset, tsr_label, torque_coef_label, xlabel, ylabel, title, full_path)


def torque_coef_windspeed_plot(dataset, turbine_code, dir_path=None):
    """
    风轮转矩系数随风速的变化曲线
    #? 2009_大型风电机组综合性能评估方法研究_刘昊
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param dir_path: 存储路径
    
    :return:
    """

    # 绘图并保存文件
    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "风轮转矩系数"
    title = "风轮转矩系数-风速分析" + "   " + turbine_code

    file_name = "torque_speed_{}.png".format(turbine_code)
    full_path = os.path.join(dir_path, file_name)

    scatter_plot(dataset, wind_speed_label, torque_coef_label, xlabel, ylabel, title, full_path)


def thrust_coef_tsr_plot(dataset, turbine_code, dir_path=None):
    """
    推力系数随叶尖速比的变化曲线
    #? 2009_大型风电机组综合性能评估方法研究_刘昊
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param dir_path: 存储路径
    
    :return:
    """

    # 绘图并保存文件
    xlabel = "叶尖速比"
    ylabel = "风轮推力系数"
    title = "风轮推力系数-叶尖速比分析" + "   " + turbine_code

    file_name = "thrust_tsr_{}.png".format(turbine_code)
    full_path = os.path.join(dir_path, file_name)

    scatter_plot(dataset, tsr_label, thrust_coef_label, xlabel, ylabel, title, full_path)


def thrust_coef_windspeed_plot(dataset, turbine_code, dir_path=None):
    """
    推力系数随风速的变化曲线
    #? 2009_大型风电机组综合性能评估方法研究_刘昊
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param dir_path: 存储路径
    
    :return:
    """

    # 绘图并保存文件
    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "风轮推力系数"
    title = "风轮推力系数-风速分析" + "   " + turbine_code

    file_name = "thrust_speed_{}.png".format(turbine_code)
    full_path = os.path.join(dir_path, file_name)

    scatter_plot(dataset, wind_speed_label, thrust_coef_label, xlabel, ylabel, title, full_path)



# --------------------------------------------------------------------
# ***
# 绘图辅助函数
# ***
# --------------------------------------------------------------------


def linear_fit_scatter_plot(data, col_x, col_y, xlabel, ylabel, title, file_path, hue=None, size=None):
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
    import seaborn as sns

    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False
    # *** ---------- 1 基于最小二乘的线性拟合 ----------
    # 线性拟合函数
    def linear_func(x,a,b):
        return a*x + b
    
    # popt数组中，两个值分别是待求参数a, b
    popt, pcov = curve_fit(linear_func, data[col_x], data[col_y])
    
    step = math.floor((data[col_x].max() - data[col_x].min()) / 250)
    x = np.arange(data[col_x].min(), data[col_x].max(), step)
    ols_y = [linear_func(point, popt[0], popt[1]) for point in x]

    ols_coef = popt[0]
    logger.info("OLS系数：{}".format(ols_coef))

    # *** ---------- 2 基于中位数回归的线性拟合 ----------
    mod = sm.QuantReg(data[col_y], data[col_x])
    res = mod.fit(q=0.5)
    # logger.info(res.summary())

    quant_reg_coef = res.params[col_x]
    logger.info("中位数回归系数：{}".format(quant_reg_coef))

    # *** ---------- 3 绘图 ----------
    # 
    fig, ax = plt.subplots()
    #? hue="label": 标记异常数据与否
    g = sns.scatterplot(data=data, x=col_x, y=col_y, hue=hue, size=size, ax=ax)
    
    #? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # 绘制线性拟合曲线
    ax.plot(x, ols_y, 'r--')

    ax.plot(data[col_x], res.fittedvalues, '-', lw=2, color='blue')
    
    # plt.show()
    plt.savefig(file_path)
    plt.close()


# --------------------------------------------------------------------
# ***
# 其它辅助函数
# ***
# --------------------------------------------------------------------


