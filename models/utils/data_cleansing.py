import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from models.utils.plot_utils import *


def Data_cleansing(data, feature: list = None, logger=None):
    """

    Parameters
    ----------
    feather:选取的特征列表
    data：数据

    Returns
    -------

    """
    if feature != None:
        data = data[feature]

    logger.info(f"清洗前{data.shape[0]}")
    for i in data.columns:
        df = box_outlier(data, i, 1.5)
        df = three_sigma(df, i)

    df = df.drop(df[((df["grWindSpeed"] > 2.5) & (df["grGridActivePower"] == 0)) \
                    | (df["grWindSpeed"] > 11) & (df["grGridActivePower"] < 3600 * 0.9) \
                    | (df["grWindSpeed"] > 20) | (df["grGridActivePower"] < 0)].index)

    logger.info(f"清洗后{df.shape[0]}")
    return df


def box_plot_outliers(data_ser, box_scale):
    """
    利用箱线图去除异常值
    :param data_ser: 接收 pandas.Series 数据格式
    :param box_scale: 箱线图尺度，默认用 box_plot（scale=3）进行清洗
    :return:
    """

    iqr = box_scale * (data_ser.quantile(0.75) - data_ser.quantile(0.25))
    # 下阈值
    val_low = data_ser.quantile(0.25) - iqr * 1.5
    # 上阈值
    val_up = data_ser.quantile(0.75) + iqr * 1.5
    # 异常值
    outlier = data_ser[(data_ser < val_low) | (data_ser > val_up)]
    # 正常值
    normal_value = data_ser[(data_ser > val_low) & (data_ser < val_up)]

    return outlier, normal_value, (val_low, val_up)


# 箱型图判断异常点
def box_outlier(data, col, iqr=1.5):
    df = data.copy(deep=True)
    out_index = []
    Q1 = df[col].quantile(q=0.25)  # 下四分位
    Q3 = df[col].quantile(q=0.75)  # 上四分位
    low_whisker = Q1 - iqr * (Q3 - Q1)  # 下边缘
    up_whisker = Q3 + iqr * (Q3 - Q1)  # 上边缘

    # 寻找异常点,获得异常点索引值，删除索引值所在行数据
    rule = (df[col] > up_whisker) | (df[col] < low_whisker)
    out = df[col].index[rule]
    out_index += out.tolist()
    df.drop(out_index, inplace=True)
    return df


def three_sigma(data, col):
    """
    进行3sigma异常值剔除
    :param data: 原数据——series
    :return: bool数组
    """

    # 上限
    up = data[col].mean() + 3 * data[col].std()
    # 下线
    low = data[col].mean() - 3 * data[col].std()

    # 在上限与下限之间的数据是正常的
    df = data[(data[col] < up) & (data[col] > low)]

    return df


def data_del(x, lower_bound, upper_bound, use_column=None, target_column=None):
    lower = pd.concat([x + 2, lower_bound], axis=1)
    upper = pd.concat([x - 2, upper_bound], axis=1)
    lower.columns = use_column + target_column
    upper.columns = use_column + target_column

    # upper[use_column[0]] = upper[use_column[0]].apply(lambda x : 0 if x<0 else x)

    lower.iloc[-1] = [0, 0]

    return lower, upper


def sigmoid(x, L, x0, k, b):
# def sigmoid(x, L,x0,k, b):
    """
    Parameters
    ----------
    L负责将输出范围从 [0,1] 缩放到 [0,L]
    b向输出添加偏差并将其范围从 [0,L] 更改为 [b,L+b]
    k负责缩放输入，保留在 (-inf,inf)
    x0是 Sigmoid 中间的点，即 Sigmoid 最初应该输出值的点1/2[因为如果 x=x0，我们得到 1/(1+exp(0)) = 1/2]。

    -------

    """
    y = L / (1 + np.exp(-k * (x - x0))) + b
    return (y)


def curve_sigmod(x, y):
    p0 = [np.max(y), np.median(x), 1, np.min(y)]  # this is an mandatory initial guess
    # p0 = [np.max(y),np.median(x), 0,]
    popt, pcov = curve_fit(sigmoid, x, y, p0, method='trf')

    if sigmoid(20, *popt) < y.max():
        k = 1 + np.exp(-popt[2] * (20 - popt[1]))
        popt[0] = (y.max() - popt[3]) * k


    y2 = sigmoid(x, *popt)
    y2.name = "功率"
    y2 = y2.apply(lambda x: y.max() if x > y.max() else x)

    return y2, popt



def confidence_interval(data, confidence_interval=0.8, use_column=None, target_column=None, plot_name=None, logger=None,
                        num=5, plot_flag=0):

    data = data[data[use_column[0]] > 0]
    # 数据清洗
    x = data[use_column[0]]
    y = data[target_column[0]]

    ##拟合三条功率曲线，一条上限 一条下面和本身数据的
    y2, popt = curve_sigmod(x, y)

    lower = confidence_interval
    upper = 1 + (1 - confidence_interval)
    lower_bound, popt_low = curve_sigmod(x + 2, y2 * lower)
    # lower_bound = lower_bound.apply(lambda x: 0 if x<0 else x)

    upper_bound, popt_upper = curve_sigmod(x - 2, y2 * upper)

    # upper_bound = upper_bound.apply(lambda x: y.max() if  x> y.max() else x)

    # lower_bound, upper_bound  = data_del(x,lower_bound,upper_bound, use_column, target_column)

    ## 提取出非异常点位inliers = {DataFrame: (19723, 5)} ['real_time', 'wind_speed', 'wind_direction', 'power', 'groups'] [4     2022-01-24 17:10:00    3.101379       -7.130000    9.378966     3.0] [5     2022-01-24 17:20:00    3.219931        3.794502   13.016151     3.0] [6     2022-01-24 17:30:00    4.115464 ...View as DataFrame

    inliers = data.loc[lambda x: (sigmoid(x[use_column[0]], *popt_low) < x[target_column[0]]) & (
                x[target_column[0]] < sigmoid(x[use_column[0]], *popt_upper))]

    # outliers_indices = np.where((data[[target_column]] < lower_bound) | (data[[target_column]] > upper_bound))[0]

    # # 找到超出置信区间的值的索引
    # outliers_indices = np.where((data[[target_column]] < lower_bound) | (data[[target_column]] > upper_bound))[0]
    #
    # # 删除超出置信区间的值
    # data = np.delete(data[[target_column]], outliers_indices)

    # 绘制函数曲线和置信区间
    # plot_confidence_interval(x, y, y2, inliers, lower_bound, upper_bound, use_column, target_column,plot_name)
    # # 绘制功率曲线和概率密度图
    # if plot_flag == 0:
    #     pass
    # else:
    #     plot_power_distplot(x, y2, plot_name, num)
    # ##绘制功率曲线
    # plot_curve_line(x,y2,plot_name,num)

    clean_value = data.shape[0] - inliers.shape[0]
    # logger.info(f"清洗了{clean_value}条数据，占比为{((clean_value/data.shape[0])*100):.2f}%")

    return inliers, (clean_value / data.shape[0])
