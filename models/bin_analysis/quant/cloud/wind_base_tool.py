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
# import logging

import numpy as np
import pandas as pd

#
import warnings
warnings.filterwarnings("ignore")



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

# 
# ** SCADA基础标签 **
power_label = 'power'
power_bin_label = 'power_bin'

# 功率预测标签 【功率曲线建模】
power_pred_label = 'power_pred'

wind_speed_label = 'wind_speed'
wind_speed_bin_label = 'wind_speed_bin'

wind_direction_label = 'wind_direction'
wind_direction_bin_label = 'wind_direction_bin'

gen_speed_label = 'gen_speed'
gen_speed_bin_label = 'gen_speed_bin'

rotor_speed_label = 'rotor_speed'
rotor_speed_bin_label = 'rotor_speed_bin'

air_density_label = 'air_density'
air_density_bin_label = 'air_density_bin'

# 机舱温度
nacelle_temp_label = 'nacelle_temp'

# wind turbine code or ID
turbine_code_label = 'turbine_code'

cp_label = 'cp'

# 
# ** 数据清洗数据点种类标识 **
#? ['label'] == 0: 清洗过的正常数据
#? ['label'] == 1: 根据“风速-功率”筛选异常数据点
#? ['label'] == 2: 根据“箱线图”去除异常值
#? ['label'] == 3: 根据“3-Delta原则”标注异常数据点
mark_label = 'label'



# --------------------------------------------------------------------
# ***
# 通用处理函数
# ***
# --------------------------------------------------------------------


def plot_save(dir_path, file_name):
    """图片文件保存

    Args:
        dir_path (str): 图像文件存储路径
        file_name (str): 文件名称
    """
    import matplotlib.pyplot as plt
    full_path = os.path.join(dir_path, file_name)
    plt.savefig(full_path)
    plt.close()


# --------------------------------------------------------------------
# ***
# 异常值清洗
# ***
# --------------------------------------------------------------------
def box_drop_abnormal(dataset, field_name):
    """
    通过箱线图和3-Delta方法，对指定字段【数据列】标注异常值
    
    :param dataset: 输入数据时序集
    :param field_name: 目标字段名称

    :return: 返回基于箱线图和3-Delta异常值标注后的数据
    """

    # *** ---------- 1 利用箱线图去除异常值 ----------
    q1 = dataset.loc[dataset[mark_label] == 0, field_name].quantile(q=0.25)
    q3 = dataset.loc[dataset[mark_label] == 0, field_name].quantile(q=0.75)
    
    low_whisker = q1 - 1.5 * (q3 - q1)
    up_whisker = q3 + 1.5 * (q3 - q1)
    
    dataset.loc[(dataset[field_name] < low_whisker) | (dataset[field_name] > up_whisker), mark_label] = 2

    # *** ---------- 2 利用3-Delta原则去除异常值 ----------
    lower_bound = np.mean(dataset[field_name]) - (3 * np.std(dataset[field_name]))
    upper_bound = np.mean(dataset[field_name]) + (3 * np.std(dataset[field_name]))
    
    dataset.loc[(dataset[field_name] < lower_bound) | (dataset[field_name] > upper_bound), mark_label] = 3
    
    return dataset


def rule_removal(dataset, rated_wind_speed, power_cap):
    """
    基于基本规则标注异常值

    :param dataset: 时序数据集
    :param rated_wind_speed: 额定风速
    :param power_cap: 装机额定功率

    :return: 返回基于规则进行异常值标注后的数据
    """

    # *** ---------- 1 当风速超过2.5m/s，功率为0的点为异常值 ----------
    dataset.loc[(dataset[wind_speed_label] > 2.5) & (dataset[power_label] == 0), mark_label] = 1

    # *** ---------- 2 当风速超过额定风速，功率小于额定功率70%的点为异常值 ----------
    dataset.loc[(dataset[wind_speed_label] > rated_wind_speed) & (dataset[power_label] < power_cap * 0.7), mark_label] = 1
    
    # *** ---------- 3 当风速超过20m/s点为异常值 ----------
    dataset.loc[dataset[wind_speed_label] > 20, mark_label] = 1

    # *** ---------- 4 当功率小于0的点为异常值 ----------
    dataset.loc[dataset[power_label] < 0, mark_label] = 1
    
    return dataset


def data_clean(dataset, rated_wind_speed, power_cap):
    """
    数据清洗：异常数据标注
    ["label"] == 0: 清洗过的正常数据
    ["label"] == 1: 根据“风速-功率”筛选异常数据点
    ["label"] == 2: 根据“箱线图”去除异常值
    ["label"] == 3: 根据“3-Delta原则”标注异常数据点

    :param dataset: 时序数据集
    :param rated_wind_speed: 额定风速
    :param power_cap: 装机额定功率

    :return: 返回进行异常值标注后的数据
    """

    # ** 1 初始所有数据点标记为 0 **
    dataset[mark_label] = 0

    # ** 2 基于机理去除部分异常值 **
    dataset = rule_removal(dataset, rated_wind_speed, power_cap)

    # ** 3 基于“发电机功率”使用箱线图和3-Delta方法清除异常值 **
    dataset = box_drop_abnormal(dataset, power_label)

    return dataset


# --------------------------------------------------------------------
# ***
# 风速分箱
# ***
# --------------------------------------------------------------------

def cut_speed(dataset):
    """
    对风速按照0.5间隔进行划分和分组：[+-0.25]

    :param dataset: 时序数据集
    
    :return: 返回对数据进行分仓和异常值标注后的数，风速分箱列表
    """

    speed_list = list(np.linspace(2, 25, 47))
    
    for i in range(len(speed_list)):
        speed_item = speed_list[i]
        
        # dataset.loc[(dataset[wind_speed_label] >= speed_item - 0.25) 
        #             & (dataset[wind_speed_label] < speed_item + 0.25), wind_speed_bin_label] = speed_item
        
        index_list = dataset[(dataset[wind_speed_label] >= speed_item - 0.25) 
                    & (dataset[wind_speed_label] < speed_item + 0.25)].index.tolist()
        
        if len(index_list) > 0:
            dataset.loc[index_list, wind_speed_bin_label] = speed_item
        else:
            print("风速分仓数据为空：{}".format(speed_item))
    
    #! 小于2.25特殊处理
    dataset.loc[dataset[wind_speed_label] < 2.25, wind_speed_bin_label] = -1
    
    #! 大于20特殊处理：超过额定风速，统一处理
    #? 20与风速区间25存在冲突
    dataset.loc[dataset[wind_speed_label] > 20, wind_speed_bin_label] = len(speed_list)
    
    return dataset, speed_list


def wind_speed_binning(dataset, field_name=power_label):
    """
    根据风速分箱对数据进行分仓，并根据指定字段【默认功率值】去除异常值
    :param dataset: 时序数据集
    
    :return: 返回对数据进行分仓和异常值标注后的数据集，风速分箱列表
    """
    
    # *** ---------- 1 按照风速区间划分 ----------
    dataset, speed_list = cut_speed(dataset)

    # *** ---------- 2 分区间标注异常值 ----------
    speed_group_data = dataset.groupby(wind_speed_bin_label)

    all_data = pd.DataFrame()
    
    for index, bin_data in speed_group_data:
        # 按风速区间，利用箱线图和3-Delta去除异常值
        #! 0.001选值的意义
        if len(bin_data) > 0.001 * len(dataset):
            bin_data = box_drop_abnormal(bin_data, field_name)
        
        # all_data = all_data._append(bin_data)
        all_data = pd.concat([all_data, bin_data])
    
    return all_data, speed_list


def power_binning(dataset, bin_size=50):
    """
    根据功率对数据进行分仓
    :param dataset: 时序数据集
    :param bin_size: 分仓功率间隔大小
    
    :return: 返回对数据进行分仓和异常值标注后的数据集，功率分箱列表
    """

    power_bins = np.arange(0, np.ceil(dataset[power_label].max()/100.0)*100, bin_size)
    power_labels = [x for x in power_bins[1:]]
    
    dataset[power_bin_label] = pd.cut(dataset[power_label], bins=power_bins, labels=power_labels)

    power_bin_groups = dataset.groupby(power_bin_label)

    power_bin_data = pd.DataFrame()
    # power_bin_data.columns = [power_label, 'power_mean', 'speed_mean', 'speed_std']

    for index, bin_data in power_bin_groups:
        power_mean = bin_data[power_label].mean()
        speed_mean = bin_data[wind_speed_label].mean()
        speed_std = bin_data[wind_speed_label].std()

        power_bin_item = pd.DataFrame({power_bin_label:[index],
                                    'power_mean': [power_mean], 
                                    'speed_mean': [speed_mean], 
                                    'speed_std': [speed_std]})
        power_bin_data = pd.concat([power_bin_data, power_bin_item])
    
    power_bin_data = power_bin_data.sort_values(power_bin_label).reset_index(drop=True)

    return power_bin_data, power_labels


def windspeed_binning_proc(dataset, rated_wind_speed, power_cap):
    """
    数据规则清洗、根据风速分箱对数据进行分仓，并去除异常值

    :param dataset: 时序数据集
    :param rated_wind_speed: 额定风速
    :param power_cap: 装机额定功率
    
    :return: 返回对数据进行分仓和异常值标注后的数据
    """
        
    # ** 1 初始所有数据点标记为 0 **
    dataset[mark_label] = 0

    # ** 2 基于机理去除部分异常值 **
    norm_data_1 = rule_removal(dataset, rated_wind_speed, power_cap)

    # ** 3 通过箱线图和3-Delta原则去除异常值 **
    #! 按照风速区间[0.5]范围+-0.25分组，并基于箱线图和3-Delta原则去除异常值
    norm_data_2, speed_list = wind_speed_binning(norm_data_1)

    return norm_data_2, speed_list


def binning_proc(dataset, all_bin_values, bin_label, target_label, 
                 split_value=None, interpolate_method=None, fill_value=np.nan):
    """对数据进行分仓处理，拟合并返回分仓的均值和方差列表
    #! 如果split_value不为空，小于的fill_value填充，大于分割值的插值
    #! 部分分仓由于没有数据，对于的结果数值为np.nan，需要填充或者插值处理
    #! "interpolate_method" 和 "fill_value" 参数二选一，优先按照"interpolate_method"处理

    #? 如果这里的插值和填充处理逻辑不适合具体的分仓分析，可以另写专门处理函数
    #? 示例参见："models.bin_analysis.quant.cloud.bin_analysis_tool"包 wind_speed_power_bin_fix方法

    Args:
        dataset (dataframe): 时序数据集
        all_bin_values (list): 所有的分仓数据
        bin_label (str): 数据集分仓列名称（标签名称）
        target_label (str): 目标分仓数据列名称
        split_value (numeric): 如果split_value不为空，小于的fill_value填充，大于分割值的插值
        interpolate_method (str): interpolate method插值方法, 比如"linear"
        fill_value (numeric): nan默认填充值
    Returns:
        (list, list): 拟合后均值和标准差数据列表
    """

    #! 与方法'windspeed_binning_proc'有区别，'windspeed_binning_proc'主要
    #! 用于风速的功率数据分仓处理，拟合功率曲线
    #! 'binning_proc'方法主要适用于通用版本的分仓处理过程
    mean_list = np.ones(len(all_bin_values)) * np.nan
    std_list = np.ones(len(all_bin_values)) * np.nan
    for index, bin_item in enumerate(all_bin_values):
        bin_data = dataset[dataset[bin_label] == bin_item]

        # 计算均值和标准差
        count = bin_data[target_label].count()
        if count==0 and split_value is not None and bin_item <= split_value:
            mean_list[index] = fill_value
            std_list[index] = 0
        else:
            mean_list[index] = bin_data[target_label].mean()
            std_list[index] = bin_data[target_label].std()

    #! 插值: NAN数据填充办法
    # TODO:
    if interpolate_method is not None:
        mean_list = pd.Series(data=mean_list).interpolate(method=interpolate_method).bfill().values
        std_list = pd.Series(data=std_list).interpolate(method=interpolate_method).bfill().values
    elif not np.isnan(fill_value):
        mean_list = pd.Series(mean_list).fillna(fill_value)
        std_list = pd.Series(std_list).fillna(fill_value)
    
    return mean_list, std_list


