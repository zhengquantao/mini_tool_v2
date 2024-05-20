#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 风电机组偏航分析
# 功能描述：为实现发电量提升目标，对机组叶偏航控制性能进行分析、诊断
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
import numpy as np

import pandas as pd

import logging

#
import warnings

warnings.filterwarnings("ignore")

#
import re

# 正则表达式匹配开头数字
digit_pattern = re.compile(r'(-?\d+)(\.\d+)?')

#
from models.utils.file_dir_tool import create_proj_dir, create_dir
from models.utils.wind_base_tool import rule_removal, wind_speed_binning, binning_proc, box_drop_abnormal
from models.utils.wind_base_tool import mark_label

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

# yaw misalignment field name
yaw_deviation_label = "yaw_deviation"
wind_speed_bin_label = "wind_speed_bin"
yaw_deviation_bin_label = "yaw_deviation_bin"

# 分仓功率偏差角度对应功率拟合标签名称
yaw_bin_fitted_label = "bin_fitted_power"
yaw_bin_cap_label = "bin_cap"


# --------------------------------------------------------------------
# ***
# 异常值清洗
# ***
# --------------------------------------------------------------------
def box_outlier(dataset, field_name, iqr=1.5):
    """
    采用四分位法完成异常点的清洗
    
    :param dataset: 输入数据时序集
    :param field_name: 目标字段名称

    :return: 完成异常点清洗的数据集
    """

    df = dataset.copy(deep=True)
    out_index = []
    Q1 = df[field_name].quantile(q=0.25)  # 下四分位
    Q3 = df[field_name].quantile(q=0.75)  # 上四分位
    low_whisker = Q1 - iqr * (Q3 - Q1)  # 下边缘
    up_whisker = Q3 + iqr * (Q3 - Q1)  # 上边缘

    # 寻找异常点,获得异常点索引值，删除索引值所在行数据
    rule = (df[field_name] > up_whisker) | (df[field_name] < low_whisker)
    out = df[field_name].index[rule]
    out_index += out.tolist()
    df.drop(out_index, inplace=True)

    return df


def three_sigma(dataset, field_name):
    """
    进行3-sigma异常值剔除
    :param dataset: 原数据——series

    :return: bool数组
    """

    # 上限
    up = dataset[field_name].mean() + 3 * dataset[field_name].std()
    # 下线
    low = dataset[field_name].mean() - 3 * dataset[field_name].std()

    # 在上限与下限之间的数据是正常的
    df = dataset[(dataset[field_name] < up) & (dataset[field_name] > low)]

    return df


# --------------------------------------------------------------------
# ***
# 偏航数据分析
# ***
# --------------------------------------------------------------------

def yaw_deviation_calc(data, wind_direction_lable, nacelle_direction_lable):
    """
    根据'风向对北角度'和'机舱对北角度'进行偏航对风偏差进行计算

    :param data: 输入数据时序集
    :param wind_direction_lable: 自然风向标签
    :param nacelle_direction_lable: 主机机舱方向

    :return: 计算了偏航的对风偏差
    """

    yaw_deviation_list = data[wind_direction_lable] - data[nacelle_direction_lable]
    data.insert(len(data.columns), yaw_deviation_label, yaw_deviation_list)

    return data


def data_cut_proc(data, wind_speed_label):
    """
    对数据进行风速和偏航对风偏差分箱标记处理

    :param data: 输入数据时序集
    :param wind_speed_label: 风速标签名称

    :return: 进行了风速和偏航对风偏差分箱标记的数据
    """

    # *** ---------- 1 偏航的对风偏差数据清洗 ----------
    data = data[((data[yaw_deviation_label] >= -10) & (data[yaw_deviation_label] <= 10))]
    data = data[(data[wind_speed_label] > 3) & (data[wind_speed_label] < 11)]

    # *** ---------- 2 自然风速分箱 ----------
    cut_bins = np.arange(3.0, 11.5, 0.5)
    # wind speed bin labels
    wind_speed_bin_labels = ["3-3.5", "3.5-4", "4-4.5", "4.5-5", "5-5.5", "5.5-6",
                             "6-6.5", "6.5-7", "7-7.5", "7.5-8", "8-8.5", "8.5-9",
                             "9-9.5", "9.5-10", "10-10.5", "10.5-11", ]
    # "11-11.5", "11.5-12", "12-12.5", "12.5-13", "13-13.5", "13.5-14", 
    # "14-14.5", "14.5-15", "15-15.5", "15.5-16", "16-16.5", "16.5-17",
    # "17-17.5", "17.5-18"]

    data[wind_speed_bin_label] = pd.cut(data[wind_speed_label], bins=cut_bins,
                                        labels=wind_speed_bin_labels, include_lowest=True)

    # *** ---------- 3 偏航对风偏差分箱 ----------
    cut_bins = np.arange(-10, 11, 1)
    yaw_deviation_bin_labels = ["-10°_-9°", "-9°_-8°", "-8°_-7°", "-7°_-6°", "-6°_-5°",
                                "-5°_-4°", "-4°_-3°", "-3°_-2°", "-2°_-1°", "-1°_0°",
                                "0°_1°", "1°_2°", "2°_3°", "3°_4°", "4°_5°",
                                "5°_6°", "6°_7°", "7°_8°", "8°_9°", "9°_10°"]
    data[yaw_deviation_bin_label] = pd.cut(data[yaw_deviation_label], bins=cut_bins,
                                           labels=yaw_deviation_bin_labels, include_lowest=True)

    return data


def yaw_bin_analysis(data, wind_speed_label, power_label):
    """
    根据风速分箱区间、偏航对风偏差分箱区间组合进行偏航性能分析
    参考论文: 2019_基于风机运行数据的偏航误差分析与校正

    :param data: 输入数据时序集
    :param wind_speed_label: 风速标签名称
    :param power_label: 功率标签名称

    :return: 返回分箱单元格的容量和出现频次数据
    """

    # 各风速分箱、偏航对风偏差分箱区间内的P与v**3 的比值的平均值数据集
    cap_data = pd.DataFrame()

    # 各风速分箱、偏航对风偏差分箱区间内: 出现的次数计数【最终的频次、出现概率研究】
    count_data = pd.DataFrame()

    wind_speed_bin_colums = sorted(data[wind_speed_bin_label].unique().tolist(),
                                   key=lambda bin: float(digit_pattern.match(bin).group(0)))
    yaw_dev_bin_rows = sorted(data[yaw_deviation_bin_label].unique().tolist(),
                              key=lambda bin: float(digit_pattern.match(bin).group(0)))

    for col in wind_speed_bin_colums:
        cap_list = []
        count_list = []

        for row in yaw_dev_bin_rows:
            # 特定的风速分箱区间、偏航对风偏差分箱区间组合的单元格数据
            cell_data = data[(data[wind_speed_bin_label] == col) & (data[yaw_deviation_bin_label] == row)]

            # ! 参考论文: 2019_基于风机运行数据的偏航误差分析与校正
            # 求得各角度区间内的P与v**3 的比值的平均值，即0.5ρACp的平均值，记为R
            R = cell_data[power_label] / (cell_data[wind_speed_label] ** 3)

            cap_list.append(R.mean())
            count_list.append(cell_data.shape[0])

            # logger.info(cell_data.shape[0])
        cap_data[col] = cap_list
        count_data[col] = count_list

    cap_data.index = yaw_dev_bin_rows
    count_data.index = yaw_dev_bin_rows

    # 列名称设置
    # cap_data.columns = wind_speed_bin_colums

    return cap_data, count_data


def yaw_quant_reg(data, wind_speed_label, power_label, turbine_code, dir_path):
    """
    为找到风速仓内最大功率对应的对风角度，需对风速仓内的数据进行回归
    根据分位数回归[中位数回归]，选用抛物线为模型结构[二次函数]，进行偏航性能分析
    参考论文: 2020_风力发电机组对风偏差检测算法研究与应用_李闯

    :param data: 输入数据时序集
    :param wind_speed_label: 风速标签名称
    :param power_label: 功率标签名称

    :param turbine_code: 机组编码
    :param dir_path: 存储路径

    :return: 返回风速分箱-偏航对风偏差结果
    """

    # 风速分箱标签
    wind_speed_bins = sorted(data[wind_speed_bin_label].unique().tolist(),
                             key=lambda bin: float(digit_pattern.match(bin).group(0)))

    # 风速分箱-偏航对风偏差 列表
    dev_list = []

    # 创建分仓偏航对风偏差分析图片保存目录
    file_path = create_dir("bin_yaw_img", dir_path)
    bin_yaw_img_title = "偏航对风偏差识别：\n   机组{}   风速仓：{} 偏差角：{}°"

    for speed_bin in wind_speed_bins:
        # 特定的风速分箱区间的偏航数据
        bin_data = data[data[wind_speed_bin_label] == speed_bin]

        # ! 参考论文: 2020_风力发电机组对风偏差检测算法研究与应用_李闯
        # ? 基于中位数回归，使用二次函数拟合[偏航对风偏差] 和[P与v**3 的比值] 曲线
        # ? => 判断对风偏差角
        # *** ---------- 1 数据准备 ----------
        '''
        #? 数据清洗
        if len(bin_data) > 200:
            bin_data = box_drop_abnormal(bin_data, power_label)
        '''

        x = bin_data[yaw_deviation_label]
        y = bin_data[power_label] / (bin_data[wind_speed_label] ** 3)

        bin_data[yaw_bin_cap_label] = y
        bin_data[mark_label] = 0

        if len(bin_data) > 200:
            bin_data = box_drop_abnormal(bin_data, yaw_bin_cap_label)

        bin_data = bin_data[bin_data[mark_label] == 0]

        training_data = {'dev': bin_data[yaw_deviation_label],
                         'cap': bin_data[yaw_bin_cap_label]}
        df = pd.DataFrame(data=training_data)

        # *** ---------- 2 二次分位数回归拟合 ----------
        import statsmodels.formula.api as smf
        mod = smf.quantreg('cap ~ dev + I(dev ** 2.0)', df)
        res = mod.fit(q=.5)
        # logger.info(res.summary())
        # res.predict({'dev': x_dev})

        # *** ---------- 3 拟合参数提取 ----------
        # 截距
        intercept = res.params["Intercept"]
        # 一次项系数
        linear_coef = res.params["dev"]
        # 二次项系数
        quadratic_coef = res.params["I(dev ** 2.0)"]

        #
        bin_data[yaw_bin_fitted_label] = res.fittedvalues

        # *** ---------- 3 偏差结果统计 ----------
        bin_dev = - linear_coef / (2 * quadratic_coef)
        # 保留四位小数
        bin_dev = round(bin_dev, 2)
        dev_list.append(bin_dev)

        # *** ---------- 4 绘制分仓图形 ----------
        # TODO:
        xlabel = "偏航对风偏差角度"
        ylabel = "功率指数"
        title = bin_yaw_img_title.format(turbine_code, speed_bin, str(bin_dev))

        file_name = "{}-{}.png".format(turbine_code, speed_bin)
        full_path = os.path.join(file_path, file_name)

        bin_yaw_plot(bin_data, yaw_deviation_label, yaw_bin_cap_label, yaw_bin_fitted_label, xlabel, ylabel,
                     title, full_path)

    # 
    logger.info("分箱偏航性能诊断对风偏差：\n {}".format(wind_speed_bins))
    logger.info(dev_list)

    return dev_list, wind_speed_bins


def bin_yaw_plot(data, col_x, col_y, fitted_label, xlabel, ylabel, title, file_path, hue=None, size=None):
    """
    按照指定数据列绘制散点图
    
    :param data: 时序数据集
    :param col_x: x数据列名
    :param col_y: y数据列名
    :param fitted_label: 分仓功率偏差角度对应功率拟合标签名称

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

    band_data = data[(data[col_y] < data[fitted_label] * 1.2) & (data[col_y] > data[fitted_label] * 0.9)]

    # 
    fig, ax = plt.subplots()
    # ? hue="label": 标记异常数据与否
    g = sns.scatterplot(data=band_data, x=col_x, y=col_y, hue=hue, size=size, ax=ax)

    # ? 下标$_x$ 上标$^x$
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # 绘制线性拟合曲线 
    # 'r--'
    # ax.plot(data[col_x], data[fitted_label], '-', lw=2, color='blue')
    data = data.sort_values(col_x)
    ax.plot(data[col_x].tolist(), data[fitted_label].tolist(), 'r--')

    # plt.show()
    plt.savefig(file_path)
    plt.close()


def yaw_dev_bin_clean(dev_list, wind_speed_bins):
    """
    【偏航对风偏差 数值清洗】
    对风速分箱后的每个分箱的偏航对风偏差进行筛选，如果数值偏离正常范围，给予舍弃

    :param dev_list: 风速分箱-偏航对风偏差 列表
    :param wind_speed_bins: 风速分箱标签 列表

    :return: 清洗过后的偏航对风偏差和风速分箱标签列表
    """

    dev_array = np.array(dev_list)
    indexs = np.where(np.abs(dev_array) <= 10)[0].tolist()

    dev_list_x = [dev_list[x] for x in indexs]
    wind_speed_bins_x = [wind_speed_bins[x] for x in indexs]

    return dev_list_x, wind_speed_bins_x


def yaw_misalignment_calc1(data, wind_speed_label, dev_list, wind_speed_bins):
    """
    通过分仓和拟合，根据每个风速分箱对风偏差的集合，使用加权平均法计算机组的综合偏差

    参考论文: 2020_风力发电机组对风偏差检测算法研究与应用_李闯

    :param data: 输入数据时序集
    :param wind_speed_label: 风速标签名称
    :param dev_list: 风速分箱-偏航对风偏差 列表
    :param wind_speed_bins: 风速分箱标签 列表

    :return: 返回基于权重计算的 风机 偏航对风偏差角度数值
    """

    # 偏航对风偏差 数值清洗
    dev_list_x, wind_speed_bins_x = yaw_dev_bin_clean(dev_list, wind_speed_bins)

    wind_speed_avg_list = []
    for speed_bin in wind_speed_bins_x:
        # 特定的风速分箱区间的偏航数据
        bin_data = data[data[wind_speed_bin_label] == speed_bin]

        # wind_speed_min = bin_data[wind_speed_label].min()
        # wind_speed_max = bin_data[wind_speed_label].max()

        wind_speed_avg = bin_data[wind_speed_label].mean()
        wind_speed_avg_list.append(wind_speed_avg)

    # 使用加权平均法计算机组的综合偏差
    speed_3_sum = sum([item ** 3 for item in wind_speed_avg_list])
    weight_list = [round(item ** 3 / speed_3_sum, 3) for item in wind_speed_avg_list]
    logger.info("分仓加权计算的综合偏差【模式一】：权重 {}".format(weight_list))
    # ! 参考论文: 2020_风力发电机组对风偏差检测算法研究与应用_李闯
    dev_angle = sum([x * y for x, y in zip(dev_list_x, weight_list)])
    dev_angle = round(dev_angle, 2)
    logger.info(dev_angle)

    return dev_angle


def yaw_misalignment_calc2(data, wind_speed_label, dev_list, wind_speed_bins, air_density_label=None):
    """
    通过分仓和拟合，根据每个风速分箱对风偏差的集合，使用加权平均法计算机组的综合偏差

    基于Wind power density: WPD=1/2*AD*WS**3
    WS: Wind Speed
    AD: Air Density

    :param data: 输入数据时序集
    :param wind_speed_label: 风速标签名称
    :param air_density_label: 空气密度标签名称
    :param dev_list: 风速分箱-偏航对风偏差 列表
    :param wind_speed_bins: 风速分箱标签 列表

    :return: 返回基于权重计算的 风机 偏航对风偏差角度数值
    """

    # 偏航对风偏差 数值清洗
    dev_list_x, wind_speed_bins_x = yaw_dev_bin_clean(dev_list, wind_speed_bins)

    bin_wpd_sum_list = []
    for speed_bin in wind_speed_bins_x:
        # 特定的风速分箱区间的偏航数据
        bin_data = data[data[wind_speed_bin_label] == speed_bin]

        # ! 是否有空气密度数据，如果没有则不考虑空气密度系数
        bin_wpd_sum = 0
        if air_density_label is not None:
            bin_wpd_sum = bin_data.apply(lambda row: 0.5 * row[air_density_label]
                                                     * pow(row[wind_speed_label], 3), axis=1).sum()
        else:
            bin_wpd_sum = bin_data[wind_speed_label].apply(lambda x: 0.5 * pow(x, 3)).sum()

        bin_wpd_sum_list.append(bin_wpd_sum)

    # 使用加权平均法计算机组的综合偏差
    wpd_sum = sum(bin_wpd_sum_list)
    weight_list = [round(item / wpd_sum, 3) for item in bin_wpd_sum_list]

    logger.info("分仓加权计算的综合偏差【模式二】：权重 {}".format(weight_list))
    # ! 基于[Wind power density]计算权重，进行综合偏差分析
    dev_angle = sum([x * y for x, y in zip(dev_list_x, weight_list)])
    dev_angle = round(dev_angle, 2)
    logger.info(dev_angle)

    return dev_angle


def yaw_misalignment_proc(data, wind_speed_label, power_label, turbine_code,
                          dir_path, air_density_label=None):
    """
    通过分仓和拟合，根据每个风速分箱对风偏差的集合，使用加权平均法计算机组的综合偏差
    分为两步：
    Step 1: 分箱进行偏航性能诊断分析
    Step 2: 分箱对风偏差加权计算整体偏差

    :param data: 输入数据时序集
    :param wind_speed_label: 风速标签名称
    :param power_label: 功率标签名称

    :param turbine_code: 机组编码
    :param dir_path: 存储路径

    :param air_density_label: 空气密度标签名称

    :return: 返回 偏航对风偏差角度
    """

    # *** ---------- 1 分箱进行偏航性能诊断分析 ----------
    # dev_list: 风速分箱-偏航对风偏差 列表
    # wind_speed_bins: 风速分箱标签 列表
    dev_list, wind_speed_bins = yaw_quant_reg(data, wind_speed_label, power_label, turbine_code, dir_path)

    # *** ---------- 2 分箱对风偏差加权计算整体偏差 ----------
    # 该机组最终 偏航对风偏差角度数值
    # ! [二选一]两种模式计算选择一种即可
    # ? 通过风速分仓和拟合，对每个分箱对风偏差的集合加权平均
    # 【模式一】根据风速三次方加权拟合
    dev_angle = yaw_misalignment_calc1(data, wind_speed_label, dev_list, wind_speed_bins)

    # 【模式二】根据风能密度（Wind power density, WPD）加权拟合
    dev_angle = yaw_misalignment_calc2(data, wind_speed_label, dev_list, wind_speed_bins, air_density_label)

    return dev_angle


def energy_loss_calc(yaw_misalignment_angle):
    """
    偏航对风偏差造成的发电量损失计算

    :param yaw_misalignment_angle: 偏航对风偏差角度

    :return: 返回 偏航对风偏差角度
    """

    loss = 1 - pow(math.cos(yaw_misalignment_angle * math.pi / 180), 3)
    loss_percent = round(loss * 100, 3)

    return loss_percent
