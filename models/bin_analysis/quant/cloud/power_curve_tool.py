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
import os
import logging

import math
import numpy as np
import pandas as pd

from scipy.optimize import curve_fit

import seaborn as sns

from matplotlib import cm
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D


# *** ---------- openoa package ----------
from scipy.optimize import differential_evolution

from openoa.utils import power_curve
from openoa.utils.plot import plot_windfarm

from openoa.utils.filters import range_flag, bin_filter

from openoa.utils.power_curve.parametric_forms import logistic5param
from openoa.utils.power_curve.parametric_optimize import least_squares, fit_parametric_power_curve

from typing import Callable

def logistic_5_parametric(windspeed_col: str, power_col: str) -> Callable:
    return fit_parametric_power_curve(
        windspeed_col,
        power_col,
        curve=logistic5param,
        optimization_algorithm=differential_evolution,
        cost_function=least_squares,

        #! bounds和风机的额定功率有关系
        #TODO: logistic方法需要根据风机的具体额定功率进行调整
        bounds=((1900, 2100), (-10, -1e-3), (1e-3, 30), (1e-3, 1), (1e-3, 10)),
    )


# *** ---------- custom package ----------
from models.bin_analysis.quant.cloud.file_dir_tool import get_full_path

from models.bin_analysis.quant.cloud.wind_base_tool import cut_speed, plot_save
from models.bin_analysis.quant.cloud.wind_base_tool import power_label, wind_speed_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_direction_label, nacelle_temp_label, power_pred_label
from models.bin_analysis.quant.cloud.wind_base_tool import air_density_label, wind_speed_bin_label, mark_label



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
std_power_label = "std_power"



# --------------------------------------------------------------------
# ***
# 功率曲线上下边界
# ***
#? 1. 基于贝兹理论betz极限的发电功率-上限
#? 2. 根据R. Chedid提出的功率曲线模型(称之为RC模型) 确定功率最低约束-下限
# --------------------------------------------------------------------

def betz_func_closure(rotor_radius, cut_out, rated_speed, rated_power, rated_factor):
    """根据风速计算贝兹理论betz极限的发电功率-函数闭包 【闭包】
    #? 2017_基于INNER-DBSCAN和功率曲线模型的风机异常状态检测
    #? 2019_基于线性插值模型的大型风电机组服役性能在线评估方法

    Args:
        wind_speed (float): 风速
        rotor_radius (float): 叶轮半径
        cut_out (float): 切出风速
        rated_speed (float): 额定风速
        rated_power (float): 额定容量
        rated_factor (float): _description_
        air_density (float, optional): 空气密度. Defaults to None.

    Returns:
        _type_: 基于贝兹理论betz极限的发电功率-计算函数
    """

    def betz_func_inner(wind_speed, air_density=None):
        return betz_func(wind_speed, rotor_radius, cut_out, rated_speed, rated_power, rated_factor, air_density)
    
    return betz_func_inner


def betz_func(wind_speed, rotor_radius, cut_out, rated_speed, rated_power, rated_factor, 
              air_density=None):
    """根据风速计算贝兹理论betz极限的发电功率
    #? 2017_基于INNER-DBSCAN和功率曲线模型的风机异常状态检测
    #? 2019_基于线性插值模型的大型风电机组服役性能在线评估方法

    Args:
        wind_speed (float): 风速
        rotor_radius (float): 叶轮半径
        cut_out (float): 切出风速
        rated_speed (float): 额定风速
        rated_power (float): 额定容量
        rated_factor (float): _description_
        air_density (float, optional): 空气密度. Defaults to None.

    Returns:
        _type_: 基于贝兹理论betz极限的发电功率
    """

    #TODO: 如否考虑切人风速情况： cut_in, 

    # 最大风能利用系数
    #? 实际远小于最大风能利用系数，可以进行调整，缩小边界范围
    #? power coefficient为"0.40"刚好可以平滑连接到额定风速
    # cp = 0.593
    # cp = 0.45
    cp = 0.40

    # 标准空气密度
    if air_density is None:
        # air_density = 1.225
        air_density = 1.40
    
    #TODO: 切出风速柔性拓展控制
    # , cut_out_ext=None, cut_out_ext_factor
    if wind_speed <= rated_speed:
        area_size = math.pi * pow(rotor_radius, 2) / 1000
        power_value = 0.5 * air_density * area_size * pow(wind_speed, 3) * cp

        power_value = min(power_value, rated_power * rated_factor)

        return round(power_value, 2)
    elif wind_speed > cut_out:
        return 0
    elif wind_speed >= rated_speed:
        return rated_power * rated_factor



def rc_func_closure(cut_out, rated_speed, cut_in, rated_power, efficiency=0.05):
    """根据 R. Chedid提出的功率曲线模型(称之为RC模型) 确定功率最低约束-函数闭包 【闭包】
    #? 2017_基于INNER-DBSCAN和功率曲线模型的风机异常状态检测
    #? 2019_基于线性插值模型的大型风电机组服役性能在线评估方法

    Args:
        wind_speed (float): 风速
        rotor_radius (float): 叶轮半径
        cut_out (float): 切出风速
        rated_speed (float): 额定风速
        rated_power (float): 额定容量
        rated_factor (float): _description_
        air_density (float, optional): 空气密度. Defaults to None.

    Returns:
        _type_: 基于RC模型的风机最低发电功率约束-计算函数
    """

    def rc_func_inner(wind_speed):
        return rc_func(wind_speed, cut_out, rated_speed, cut_in, rated_power, efficiency)
    
    return rc_func_inner


def rc_func(wind_speed, cut_out, rated_speed, cut_in, rated_power, efficiency=0.05):
    """根据 R. Chedid提出的功率曲线模型(称之为RC模型) 确定功率最低约束
    #? 2017_基于INNER-DBSCAN和功率曲线模型的风机异常状态检测
    #? 2019_基于线性插值模型的大型风电机组服役性能在线评估方法

    Args:
        wind_speed (float): 风速
        rotor_radius (float): 叶轮半径
        cut_out (float): 切出风速
        rated_speed (float): 额定风速
        rated_power (float): 额定容量
        rated_factor (float): _description_
        air_density (float, optional): 空气密度. Defaults to None.

    Returns:
        _type_: 基于RC模型的风机最低发电功率约束
    """
    
    #? 对应较低的利用效率的额定功率
    rated_power = rated_power * efficiency

    #
    if wind_speed < cut_in:
        return 0
    elif wind_speed < rated_speed:
        '''
        a = rated_power / (pow(rated_speed, 3) - pow(cut_in, 3))
        b = pow(cut_in, 3) / (pow(rated_speed, 3) - pow(cut_in, 3))
        return a * pow(wind_speed, 3) - b * rated_power
        '''

        #? 两种不同的计算步骤，结果一致
        cut_in_3 = pow(cut_in, 3)
        power_value = (pow(wind_speed, 3) - cut_in_3) * rated_power / (pow(rated_speed, 3) - cut_in_3)
        
        return round(power_value, 2)
    elif wind_speed <= cut_out:
        return rated_power
    else:
        return 0



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

    y = L / (1 + np.exp(-k*(x-x0))) + b
    
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
    
    #? p0：函数参数的初始值，从而减少计算机的计算量
    p0 = [data[power_label].max(), data[wind_speed_label].mean(), 1, data[power_label].min()]

    # 基于sigmoid拟合功率曲线
    popt, pcov = curve_fit(sigmoid, data[wind_speed_label], data[power_label], p0, method="dogbox")
    #! sigmoid拟合可能没有到达额定功率：到达额定风速以后，额定功率数值线偏下
    #? sigmoid拟合修正：保证功率曲线到达额定功率数值线
    if sigmoid(20, *popt) > data[power_label].max():
        k = 1 + np.exp(-popt[2]*(20-popt[1]))
        popt[0] = (data[power_label].max() - popt[3]) * k
    
    #
    curve = pd.DataFrame(wind_speed_list)
    curve[power_label] = pd.DataFrame(sigmoid(wind_speed_list, *popt))
    curve.columns = [wind_speed_label, actual_power_label]
    
    return popt, curve


def calc_actual_power_curve(data):
    """
    计算实际功率曲线数值点【计算每个分箱平均值】
    :param data: 输入数据时序集

    :return: 功率曲线数据点集合
    """

    # *** ---------- 1 对风速划分区间 ----------
    data, speed_list = cut_speed(data)

    # *** ---------- 2 根据2个思路绘制实际功率曲线 ----------
    speed_bin_dataset = data.groupby(wind_speed_bin_label)
    actual_power_df = pd.DataFrame()

    for index, bin_data in speed_bin_dataset:
        #? 分箱区间点太少，不操作：功率曲线不考虑该部分数值
        if len(bin_data) > 0.0001 * len(data):
            # 2.1 根据IEC按照风速分箱生成实际功率
            actual_power = bin_data[power_label].mean()
            std_power = bin_data[power_label].std()
            
            actual_power_curve = pd.DataFrame([index, actual_power, std_power]).T
            actual_power_curve.columns = [wind_speed_label, actual_power_label, std_power_label]
            
            # actual_power_df = actual_power_df._append(actual_power_curve)
            actual_power_df = pd.concat([actual_power_df, actual_power_curve])
    
    # 2.2 最终的实际功率曲线数据
    actual_power_df = actual_power_df[actual_power_df[wind_speed_label] != -1]
    actual_power_df = actual_power_df.sort_values(wind_speed_label).reset_index(drop=True)
    
    return actual_power_df


def theory_curve_prep(data, speed_list, avg_air_density = None):
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
        data1[wind_speed_label] = data1[wind_speed_label].apply(lambda x: x/pow((avg_air_density/1.225), 1/3))
    
    # data1[wind_speed_label] = data1[wind_speed_label] + 0.5

    
    #TODO: 理论功率曲线的两种生成方式
    #! 二选一：基于直线拟合和基于sigmoid曲线的两种模式
    # *** ---------- 模式一：2 按照原本的风速采样点提取出功率数据 ----------
    #! 直接对转换的理论功率曲线进行线性拟合（问题点：曲线不够平滑）
    # 取理论功率曲线
    data2[theory_power_label] = np.nan
    # all_data = data1._append(data2).sort_values(wind_speed_label)
    all_data = pd.concat([data1, data2]).sort_values(wind_speed_label)
    
    #! 线性拟合：直线拟合
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
    

    # *** ---------- 模式二：3 按照sigmoid曲线拟合功率数据 ----------
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
    #? hue="label": 标记异常数据与否
    sns.scatterplot(data=data, x=wind_speed_label, y=power_label, hue="label")
    plt.title("speed_power")
    
    plt.show()


def plot_power_var(data, power_bin_data, turbine_code, file_path, hue="label"):
    """
    绘制功率分仓方差
    :param data: 输入数据时序集
    :param power_bin_data: 功率分仓数据
    :param turbine_code: 机组编码
    :param file_path: 图像路径
    :return:
    """

    plt.figure()
    #? hue="label": 标记异常数据与否
    #! 参见wind_base_tool文件power_binning函数
    sns.scatterplot(data=data, x=wind_speed_label, y=power_label, hue=hue, 
                    legend=False, size=5)
    plt.plot(power_bin_data['speed_mean'], power_bin_data['power_mean'], 
             c="blue", label="power_curve")
    
    #? 使用errorbar绘制功率曲线的方差
    # fmt：定义数据折线和数据点的样式。
    # ecolor：定义误差棒的颜色。
    # elinewidth：定义误差棒线的宽度。
    # capsize：定义误差棒帽的大小（长度）。
    # capthick：定义误差棒帽的宽度。
    # alpha：设置透明度（范围：0-1）。
    # marker：设置数据点的样式
    # markersize（简写ms）：定义数据点的大小。
    # markeredgecolor（简写mec）：定义数据点的边的颜色，可使用官方提供的缩写
    # 字母代表的简单颜色，也可以使用RGB颜色和HTML十六进制#aaaaaa格式的颜色（具体可参考matplotlib.colors）。
    # markeredgewidth（ 简写mew ）：定义数据点的边的宽度。
    # markerfacecolor（简写 mfc）：定义数据点的颜色。
    # linestyle：设置折线的样式，设置成none可将折线隐藏。
    # label：添加图例。
    plt.errorbar(power_bin_data['speed_mean'], power_bin_data['power_mean'], xerr=power_bin_data['speed_std'],
                 fmt='o', ecolor='orangered', color='b', elinewidth=2, capsize=4, markersize=3, 
                 mfc='orange', mec='k', mew=0.5)

    plt.legend()
    title = "功率分仓偏差分析" + "   " + turbine_code
    plt.title(title)

    # plt.show()
    var_file_name = "{}_power_var.png".format(turbine_code)
    var_full_path = os.path.join(file_path, var_file_name)
    plt.savefig(var_full_path)
    plt.close()


def scatter_curve(data, curve, title, file_path, hue="label"):
    """
    绘制散点图和曲线
    :param data: 输入数据时序集
    :param curve: 理论和实际功率曲线数据
    :param title: 图像标题
    :param file_path: 图像文件完整路径
    :return:
    """

    plt.figure()
    #? hue="label": 标记异常数据与否
    # palette='vlag' 'deep'【默认】'rainbow'
    sns.scatterplot(data=data, x=wind_speed_label, y=power_label, 
                    hue=hue, palette='deep', legend=False)
    plt.plot(curve[wind_speed_label], curve[actual_power_label], 
             c="blue", label="actual_curve")
    plt.plot(curve[wind_speed_label], curve[theory_power_label], 
             c="black", label="theory_curve")
    
    #? 使用errorbar绘制功率曲线的方差
    # ecolor='r', color='b', crimson deeppink lime
    #? color与mfc冲突，后者覆盖
    plt.errorbar(curve[wind_speed_label], curve[actual_power_label], yerr=curve[std_power_label],
                 fmt='o', ecolor='orangered', color='b', elinewidth=2, capsize=4,
                 markersize=4, mfc='yellow', mec='green', mew=0.5)

    plt.legend()
    plt.title(title)

    # plt.show()
    plt.savefig(file_path)
    plt.close()


def scatter_curve_x(data, curve, title, file_path, hue="label"):
    """
    绘制散点图和曲线
    :param data: 输入数据时序集
    :param curve: 理论和实际功率曲线数据
    :param title: 图像标题
    :param file_path: 图像文件完整路径
    :return:
    """

    plt.figure()
    #? hue="label": 标记异常数据与否
    #TODO: 与scatter_curve不同的地方
    #! "legend=False" 隐藏hue对应的legend显示
    sns.scatterplot(data=data, x=wind_speed_label, y=power_label, hue=hue, 
                    size=hue, alpha=0.8, legend=False) # markers='^', 
    plt.plot(curve[wind_speed_label], curve[actual_power_label], 
             c="blue", label="actual_curve")
    plt.plot(curve[wind_speed_label], curve[theory_power_label], 
             c="black", label="theory_curve")
    
    #? 使用errorbar绘制功率曲线的方差
    plt.errorbar(curve[wind_speed_label], curve[actual_power_label], curve[std_power_label],
                 fmt='o', ecolor='r', color='b', elinewidth=2, capsize=4)

    plt.legend()
    plt.title(title)

    # plt.show()
    plt.savefig(file_path)
    plt.close()


def wind_speed_power_plot(data, turbine_code, file_path, air_density_tag=None):
    """
    绘制风速和功率的曲线
    :param data: 输入数据时序集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    :param air_density_tag: 空气密度标签

    :return:
    """

    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "功率/(kW)"
    title = "风速功率变化分析" + "   " + turbine_code

    file_name = "{}_speed_power.png".format(turbine_code)
    full_path = os.path.join(file_path, file_name)

    plt.figure()
    #? hue="label": 标记异常数据与否
    sns.relplot(data=data, x=wind_speed_label, y=power_label, kind="line", ci="sd",
                #, dashes=False, markers=True
                style=air_density_tag, hue=air_density_tag, size=air_density_tag)
    
    # plt.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    plt.tight_layout()

    # plt.show()
    plt.savefig(full_path)
    plt.close()


def power_curve_pred_plot(wind_speed_list, actual_power_list, pred_power_list, 
                          turbine_code, file_path, bin_curve_df=None):
    """功率实际与预测数据对比展示

    Args:
        wind_speed_list (list): 风速数据
        actual_power_list (list): 实际功率数据
        pred_power_list (list): 预测功率数据
        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
        bin_curve_df (DataFrame): IEC BIN分仓拟合曲线
    """

    plt.figure(figsize = (10, 6))
    plt.scatter(wind_speed_list, actual_power_list, color="blue", label="Ground truth", s=0.1)
    plt.scatter(wind_speed_list, pred_power_list, color="red", label="Prediction", s=0.1)

    if bin_curve_df is not None:
        plt.plot(bin_curve_df[wind_speed_label], bin_curve_df[power_label], '-*', label='IEC BIN')
    
    plt.title("Power Curve model")
    plt.xlabel("Wind speed (m/s)")
    plt.ylabel("Output power")

    plt.legend()
    plt.tight_layout()
    
    # plt.show()
    file_name = "{}_dswe.png".format(turbine_code)
    plot_save(file_path, file_name)


def power_curve_3d_series_plot(power_curve_df, turbine_code, file_path):
    """功率曲线3D展示：实际与预测数据对比展示 【多维度】 【三维功率曲线】

    Args:
        power_curve_df (DataFrame): 功率曲线模型 数据集
        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
    """
    
    #? 风速 + 风向 => 功率 三维功率曲线
    power_curve_direction_3d_plot(power_curve_df, turbine_code, file_path)

    #? 风速 + 空气密度 => 功率 三维功率曲线
    power_curve_airdensity_3d_plot(power_curve_df, turbine_code, file_path)

    #? 风速 + 机舱温度 => 功率 三维功率曲线
    power_curve_nacelletemp_3d_plot(power_curve_df, turbine_code, file_path)


def power_curve_direction_3d_plot(dataset, turbine_code, file_path):
    """功率曲线3D展示：实际与预测数据对比展示 【风向】 【三维功率曲线】
    #? 参考dist_tool.py文件的pcw_direction_3d_plot函数
    #? 差异：pcw_direction_3d_plot函数是基于数据的直接展示，
    #? power_curve_direction_3d_plot函数重点对比实际风机出力
    #? 和功率曲线建模的差异对比

    Args:
        dataset (DataFrame): 功率曲线模型 数据集

        wind_speed_list (list): 风速数据
        wind_direction_list (list): 风向数据
        actual_power_list (list): 实际功率数据
        pred_power_list (list): 预测功率数据

        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
        bin_curve_df (DataFrame): IEC BIN分仓拟合曲线
    """

    vars_list = [wind_speed_label, wind_direction_label, power_label, power_pred_label]

    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "风向/($°$)"
    zlabel = "功率/(kW)"
    title = "风速-风向-功率3D分析"

    file_name = "pc_direction_3d_{}.png".format(turbine_code)
    file_path = get_full_path(file_path, file_name)

    power_curve_vs_pred_3d_plot(dataset, vars_list, file_path, xlabel, ylabel, zlabel, title)


def power_curve_airdensity_3d_plot(dataset, turbine_code, file_path):
    """功率曲线3D展示：实际与预测数据对比展示 【空气密度】 【三维功率曲线】

    Args:
        dataset (DataFrame): 功率曲线模型 数据集

        wind_speed_list (list): 风速数据
        air_density_list (list): 空气密度数据
        actual_power_list (list): 实际功率数据
        pred_power_list (list): 预测功率数据

        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
        bin_curve_df (DataFrame): IEC BIN分仓拟合曲线
    """

    vars_list = [wind_speed_label, air_density_label, power_label, power_pred_label]

    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "空气密度/(Kg/m$^3$)"
    zlabel = "功率/(kW)"
    title = "风速-空气密度-功率3D分析"

    file_name = "pc_airsentiy_3d_{}.png".format(turbine_code)
    file_path = get_full_path(file_path, file_name)

    power_curve_vs_pred_3d_plot(dataset, vars_list, file_path, xlabel, ylabel, zlabel, title)


def power_curve_nacelletemp_3d_plot(dataset, turbine_code, file_path):
    """功率曲线3D展示：实际与预测数据对比展示 【机舱温度】 【三维功率曲线】

    Args:
        dataset (DataFrame): 功率曲线模型 数据集

        wind_speed_list (list): 风速数据
        nacelle_temp_list (list): 机舱温度数据
        actual_power_list (list): 实际功率数据
        pred_power_list (list): 预测功率数据

        turbine_code (str): 机组编码
        file_path (str): 图像文件完整路径
        bin_curve_df (DataFrame): IEC BIN分仓拟合曲线
    """

    vars_list = [wind_speed_label, nacelle_temp_label, power_label, power_pred_label]

    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "机舱温度/($°$)"
    zlabel = "功率/(kW)"
    title = "风速-机舱温度-功率3D分析"

    file_name = "pc_nacelletemp_3d_{}.png".format(turbine_code)
    file_path = get_full_path(file_path, file_name)

    power_curve_vs_pred_3d_plot(dataset, vars_list, file_path, xlabel, ylabel, zlabel, title)


def power_curve_vs_pred_3d_plot(dataset, vars_list, file_path, xlabel=None, ylabel=None, 
                        zlabel=None, title=None):
    """
    绘制功率曲线三维展示 图像 【真实功率与预测值对比】
    
    :param dataset: 时序数据集
    :param vars_list: x、y、z变量名称列表
    :param file_path: 图像文件完整路径

    :param xlabel: x坐标名称
    :param ylabel: y坐标名称
    :param zlabel: z坐标名称
    :param title: 图像标题
    
    :return:
    """
    
    # *** ---------- 3D plot initializing ----------
    #? azim是绕z轴旋转的角度
    #? elev是绕y轴旋转的角度
    #? 默认值：azim=-60, elev=30
    figsize=(12, 8)
    fig = plt.figure(figsize=figsize)
    
    #! 存在两种方式绘制3D图形
    ax = Axes3D(fig, azim=120, elev=10) # azim=-60
    # ax = fig.gca(projection='3d')
    # ax.view_init(elev=10,azim=120)

    # *** ---------- 3D Power Curve with power value of ground truth ----------
    #? vars_list[0] + vars_list[1] => vars_list[2]
    ax.scatter(dataset[vars_list[0]], dataset[vars_list[1]], dataset[vars_list[2]], 
               cmap=cm.coolwarm, alpha=0.5, marker='o')
    
    # *** ---------- 3D Power Curve with power value of prediction ----------
    #? vars_list[0] + vars_list[1] => vars_list[3]
    ax.scatter(dataset[vars_list[0]], dataset[vars_list[1]], dataset[vars_list[3]], 
               cmap=cm.coolwarm, alpha=0.5, marker='+')
    
    # *** ---------- 3D plot setting ----------
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



# --------------------------------------------------------------------
# ***
# Power Curve Modeling
# ***
# --------------------------------------------------------------------

def power_curve_analysis_openoa(dataset, turbine_code, file_path):
    """
    基于openoa包功率曲线拟合方法建模分析【Power Curve Modeling】
    三种方法建模：IEC、Spline、logistic五参数
    
    :param dataset: 输入数据时序集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径

    :return:
    """

    # Fit the power curves
    #? 返回的是函数
    iec_curve = power_curve.IEC(dataset[wind_speed_label], dataset[power_label], bin_width=0.1)
    l5p_curve = logistic_5_parametric(dataset[wind_speed_label], dataset[power_label])
    spline_curve = power_curve.gam(dataset[wind_speed_label], dataset[power_label], n_splines = 20)

    # Plot the results
    x = np.linspace(0, 20, 100)
    plt.figure(figsize = (10, 6))
    plt.scatter(dataset[wind_speed_label], dataset[power_label], alpha=0.5, s=1, c='gray')
    plt.plot(x, iec_curve(x), color="red", label='IEC', linewidth=3)
    plt.plot(x, spline_curve(x), color="C1", label='Spline', linewidth=3)
    plt.plot(x, l5p_curve(x), color="C2", label='L5P', linewidth=3)
    
    plt.xlabel('Wind speed (m/s)')
    plt.ylabel('Power (kW)')
    plt.legend()

    # 绘图和保存文件
    # plt.show()
    curve_file_name = "{}_openoa.png".format(turbine_code)
    curve_full_path = os.path.join(file_path, curve_file_name)
    plt.savefig(curve_full_path)
    plt.close()


