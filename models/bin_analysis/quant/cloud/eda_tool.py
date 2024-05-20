#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# Exploratory Data Analysis(EDA)
# 功能描述：EDA(Exploratory Data Analysis, 探索性数据分析)在进行正式的
# 统计分析之前,对数据进行初步的探索和分析的过程。
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
import logging

import os
import calendar

import numpy as np
import pandas as pd

from scipy.stats import pearsonr

#
import warnings
warnings.filterwarnings("ignore")


#
from models.bin_analysis.quant.cloud.wind_base_tool import wind_speed_label, power_label, wind_direction_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import plot_save
from models.bin_analysis.quant.cloud.pitch_analysis import pitch1_label, pitch2_label, pitch3_label


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
# EDA分析处理
# ***
# --------------------------------------------------------------------

def plot_EWMA(data, time_label, ewma_label, turbine_code, dir_path):
    """进行EWMA指数加权移动平均分析和展示
    Exponentially weighted moving average (EWMA)

    1. 基于pandas包ewm函数
    2. 进行长短两种时间间隔分析

    Args:
        data (DataFrame): 时序数据集
        time_label (str): 时间字段标签
        ewma_label (str): ewma分析标签
        turbine_code (str): 机组编码
        dir_path (str): 存储路径
    """

    '''
    #
    ewma_long = data[ewma_label].ewm(halflife='180 minutes', times=pd.DatetimeIndex(data[time_label])).mean()
    ewma_short = data[ewma_label].ewm(halflife='20 minutes', times=pd.DatetimeIndex(data[time_label])).mean()
    '''
    ewma_long = data[ewma_label].ewm(halflife='1 days', times=pd.DatetimeIndex(data[time_label])).mean()
    ewma_short = data[ewma_label].ewm(halflife='0.1 days', times=pd.DatetimeIndex(data[time_label])).mean()

    #
    import seaborn as sns
    from windrose import WindroseAxes

    #
    import matplotlib as mpl

    from matplotlib import cm
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    from mpl_toolkits.mplot3d import Axes3D

    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False
    mpl.rcParams['legend.fontsize'] = 10
    
    plt.subplots(figsize = (16,3))
    
    plt.plot(data[time_label], ewma_long, linewidth=1)
    plt.plot(data[time_label], ewma_short, color='indigo')
    # plt.ylim([0, 1])
    plt.axhline(y=ewma_long.mean(), color='gray', linestyle='--')
    plt.axhline(y=ewma_short.median(), color='gray', linestyle='--')
    plt.title('EWMA Analysis of {} - {}'.format(ewma_label, turbine_code))

    # 保存文件
    # plt.show()
    file_name = "EWMA_{}_{}.png".format(ewma_label, turbine_code)
    plot_save(dir_path, file_name)


def plot_windrose(data, turbine_code, dir_path):
    """绘制风能玫瑰图

    1. 基于windrose包
    2. opening: to control the space between each sector

    Args:
        data (DataFrame): 时序数据集
        turbine_code (str): 机组编码
        dir_path (str): 存储路径
    """
    
    fig = plt.figure()
    ax = WindroseAxes.from_ax()
    ax.bar(data[wind_direction_label], data[wind_speed_label], normed=True, 
           opening=0.9, edgecolor='white')
    
    ax.set_legend()
    ax.set_title('Wind Rose representation - {}'.format(turbine_code))

    # 保存文件
    # plt.show()
    file_name = "Windrose_{}.png".format(turbine_code)
    plot_save(dir_path, file_name)


def set_dark_bg(mpl=None, sns=None):
    """设置matplotlib绘图plot颜色风格
    """

    mpl.style.use('dark_background')
    sns.set_palette('bright')


def clear_plots(plt=None):
    """清除matplotlib绘图plot对象
    """

    plt.clf()
    plt.close("all")


def detect_missing_data(data, turbine_code, dir_path):
    """检查数据缺失情况

    1. Check out how much missing data there is in the .csv. No one.
    2. To determine the number of missing data.

    Args:
        data (DataFrame): 时序数据集
        turbine_code (str): 机组编码
        dir_path (str): 存储路径
    """
    #
    import seaborn as sns
    from windrose import WindroseAxes

    #
    import matplotlib as mpl

    from matplotlib import cm
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    from mpl_toolkits.mplot3d import Axes3D

    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False
    mpl.rcParams['legend.fontsize'] = 10

    # create a new DataFrame with the expected periods
    expected_periods = pd.date_range(start=data.index.min(), end=data.index.max(), freq='10T')

    # find the missing periods
    missing_periods = expected_periods.difference(data.index)

   # count the number of missing periods for each month
    missing_counts = pd.Series(missing_periods.month).value_counts().sort_index()

    # create a list of missing counts for each month, converted to hours
    # counts = [0] * len(month_names)
    # for i, month in enumerate(month_names):
    #     if month in missing_counts.index:
    #         counts[i] = missing_counts[month] * 0.1667
    counts = [missing_counts[i] * 0.1667 if i in missing_counts.index else 0 for i in range(1, 13)]

    # create a dictionary of month names and their corresponding number
    month_names = [calendar.month_name[i][:3] for i in range(1, 13)]

    # create a bar plot of the missing counts by month
    plt.bar(month_names, counts)
    plt.xlabel('Month')
    plt.ylabel('Missing Data (Hours)')
    plt.title('Missing Data by Month - {}'.format(turbine_code))

    # 保存文件
    # plt.show()
    file_name = "Missing_Data_{}.png".format(turbine_code)
    plot_save(dir_path, file_name)


def most_productive_periods(data, turbine_code, dir_path, period='month'):
    """风机发电效率分析

    Is there any difference between the periods for average power production?
    This plot show to us many information. Avg. wind speed, Avg. production and the best ratio. 
    - So, the most productive periods(,above the avg.) are: 1.-3. and the 8.-11. months, and 15:00-06:00.
    - The best ratio: 17:00-23:00 [If we had more data (such as temperature, humidity, etc.) 
    we could draw more conclusions about efficiency.]
    - If we want to carry out pre-planned maintenance, the best time is: I Jun., around 10 oclock

    Args:
        data (DataFrame): 时序数据集
        turbine_code (str): 机组编码
        dir_path (str): 存储路径
        period (str, optional): ['hour', 'month']. Defaults to 'month'.
    """

    #? 针对时刻点【24小时或者12个月】基于发电功率均值【productive发电效率】进行排序

    #
    import seaborn as sns
    from windrose import WindroseAxes

    #
    import matplotlib as mpl

    from matplotlib import cm
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    from mpl_toolkits.mplot3d import Axes3D

    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False
    mpl.rcParams['legend.fontsize'] = 10

    fig, ax1 = plt.subplots()

    file_name = ""
    if period == 'hour':
        file_name = "Production_by_Hour_Periods_{}.png".format(turbine_code)

        avg_Kw = data.groupby(data.index.hour)[power_label].mean()
        avg_Wind_speed = data.groupby(data.index.hour)[wind_speed_label].mean()
        x_label = 'Hour of the day'
        
        # calculate ratio of Power to Wind Speed
        hour_group_data = data.groupby(data.index.hour)
        ratio = pd.to_numeric(hour_group_data[power_label].mean() / hour_group_data[wind_speed_label].mean())

        plt.xticks(data.index.hour.unique().values)
    else:
        file_name = "Production_by_Month_Periods_{}.png".format(turbine_code)

        avg_Kw = data.groupby(data.index.month)[power_label].mean()
        avg_Wind_speed = data.groupby(data.index.month)[wind_speed_label].mean()
        x_label = 'Months of the year'
        
        month_group_data = data.groupby(data.index.month)
        ratio = pd.to_numeric(month_group_data[power_label].mean() / month_group_data[wind_speed_label].mean())

        plt.xticks(data.index.month.unique().values)
    
    #
    color = 'yellow'
    ax1.set_xlabel(x_label)
    ax1.set_ylabel('Average Power (kW)', color=color)
    ax1.plot(avg_Kw.index, avg_Kw.values, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # instantiate a second axes that shares the same x-axis
    ax2 = ax1.twinx()

    color = 'lightblue'
    # we already handled the x-label with ax1
    ax2.set_ylabel('Average Wind Speed (m/s)', color=color)
    
    ax2.plot(avg_Wind_speed.index, avg_Wind_speed.values, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Add horizontal lines at the average wind speed and average Power
    ax2.axhline(y=avg_Wind_speed.values.mean(), color='blue', linestyle='--')
    ax1.axhline(y=avg_Kw.values.mean(), color='orange', linestyle='--')
    
    # find the highest ratio
    best = ratio.idxmax()
    pd.set_option("display.max_rows", None, "display.max_columns", None)

    '''
    logger.info(ratio)
    logger.info(best)
    logger.info(avg_Kw)
    logger.info(avg_Wind_speed)
    '''
    
    # Add a vertical line at the highest product value
    ax1.axvline(x=best, color='red', linestyle='--')
    ax1.text(best, avg_Kw.max(), 'Best ratio', rotation=20, va='bottom', color='red')

    fig.tight_layout()  # otherwise the right y-label is clipped. :/

    # 保存文件
    # plt.show()
    plot_save(dir_path, file_name)


def corr_windspeed_power_winddirection(data, turbine_code, dir_path):
    """相关性系数分析：风速、功率、风向
    Is there any correlation between the wind speed, wind direction and power production?
    - After we print the correlations
        wind speed-power: 0.9127742911275556
        wind direction-power: -0.0627017262406927
        wind speed-wind direction-0.0771877325070333
    As expected, there is a strong correlation between the wind speed and the pruduction
    (if higher the wind strength, then higher the energy produced too), in the other two
    comparisons, a negative correlation is visible, but not significant.
    - When we take a look on the next plot, we can detect, that most productive direction
    is between 30°-90° (more than the half of the productivity).

    Args:
        data (DataFrame): 时序数据集
        turbine_code (str): 机组编码
        dir_path (str): 存储路径
    """
    #
    import seaborn as sns
    from windrose import WindroseAxes

    #
    import matplotlib as mpl

    from matplotlib import cm
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    from mpl_toolkits.mplot3d import Axes3D

    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False
    mpl.rcParams['legend.fontsize'] = 10
    # *** ---------- 1 Correlation coefficient analysis ----------
    # corr_windspeed_power = data[wind_speed_label].corr(data[power_label])
    corr_windspeed_power = pearsonr(data[wind_speed_label], data[power_label])
    logger.info(corr_windspeed_power)
    
    # corr_winddirection_power = data[wind_direction_label].corr(data[power_label])
    corr_winddirection_power = pearsonr(data[wind_direction_label], data[power_label])
    logger.info(corr_winddirection_power)
    
    # corr_windspeed_winddirection = data[wind_speed_label].corr(data[wind_direction_label])
    corr_windspeed_winddirection = pearsonr(data[wind_speed_label], data[wind_direction_label])
    logger.info(corr_windspeed_winddirection)

    
    # *** ---------- 2 Total Active Power by Wind Direction ----------
    #? 针对风向【30度分仓】基于发电功率总量【对应可以理解为发电量】进行排序
    wind_direction_group_label = "Wind Direction (°) Rounded"
    
    # Round wind direction values to nearest 30 degrees
    data[wind_direction_group_label] = (data[wind_direction_label] // 30) * 30
    
    # Group data by wind direction and calculate total power
    grouped_data = data.groupby(wind_direction_group_label)[power_label].sum()
    fig, ax = plt.subplots()

    explode = [0.04] * len(grouped_data.index)
    labels = grouped_data.index.astype(str)

    # Define a custom color palette
    custom_palette = sns.color_palette("Paired", len(grouped_data.index))
    ax.pie(grouped_data.values, startangle = 90, counterclock = False, 
           explode = explode, colors=custom_palette)
    
    plt.title("Total Active Power by Wind Direction (°) - {}".format(turbine_code))
    centre_circle = plt.Circle((0, 0), 0.4, fc='black')
    ax.add_artist(centre_circle)
    plt.legend(labels = labels, fancybox = True, loc = 'center left', 
               bbox_to_anchor = (0.93, 0.81), framealpha = 0.5, 
               fontsize = 10, shadow = True, borderpad = 0.8)
    
    # 保存文件
    file_name = "Total_Active_Power_by_Wind_Direction_{}.png".format(turbine_code)
    full_path = os.path.join(dir_path, file_name)
    plt.savefig(full_path)
    # plt.show()
    plt.close()


    # *** ---------- 3 Efficiency by Wind Directionn ----------
    #? 针对风向【30度分仓】基于发电功率均值【Efficiency发电效率】进行排序
    #
    clear_plots()

    fig, ax = plt.subplots()
    # Group data by wind direction and calculate mean power and wind
    grouped_data = data.groupby(wind_direction_group_label)[[power_label, wind_speed_label]].mean()
    
    # Calculate efficiency for each direction
    efficiency = grouped_data[power_label] / grouped_data[wind_speed_label]
    
    results = pd.DataFrame({"Efficiency": efficiency})
    logger.info(results.sort_values(by="Efficiency", ascending=False))
    
    explode = [0.1] * len(grouped_data.index)
    for i in range(len(grouped_data.index)):
        if efficiency.values[i] == efficiency.values.min():
            explode[i] = 0.3

    logger.info(results.sort_values(by="Efficiency", ascending=False))

    ax.pie(results["Efficiency"], labels=results.index, startangle=90, 
           counterclock=False, explode=explode)
    
    centre_circle = plt.Circle((0, 0), 0.4, fc='black')
    ax.add_artist(centre_circle)

    plt.title("Efficiency by Wind Direction (°) - {}".format(turbine_code))
    
    # 保存文件
    file_name = "Efficiency_by_Wind_Direction_{}.png".format(turbine_code)
    full_path = os.path.join(dir_path, file_name)
    plt.savefig(full_path)
    # plt.show()
    plt.close()


def avg_power_by_windspeed(data, turbine_code, dir_path):
    """风速平均发电功率分析
    What is the average power production level for different wind speeds?

    Args:
        data (DataFrame): 时序数据集
        turbine_code (str): 机组编码
        dir_path (str): 存储路径
    """
    #
    import seaborn as sns
    from windrose import WindroseAxes

    #
    import matplotlib as mpl

    from matplotlib import cm
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    from mpl_toolkits.mplot3d import Axes3D

    # ? 中文乱码问题
    font = fm.FontProperties(fname='微软雅黑.ttf')
    # ? 字体设置：SimHei
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    plt.rcParams["axes.unicode_minus"] = False
    mpl.rcParams['legend.fontsize'] = 10

    # Group data by wind speed and calculate average active power
    # uses the cut function to bin the wind speed values into 3 m/s intervals,
    # and calculates the mean active power for each bin. 
    #? 针对风速【3分仓】基于发电功率均值【Efficiency发电效率】进行排序
    grouped_data = data.groupby(pd.cut(data[wind_speed_label], bins=range(0, 26, 1)))[power_label].mean()
    
    #? 分组数据存在NA情况
    grouped_data = grouped_data.dropna()

    fig = plt.figure(figsize=(12,4))
    # Plot bar chart
    def gradientbars(bars,ydata,cmap):
            ax = bars[0].axes
            lim = ax.get_xlim() + ax.get_ylim()
            ax.axis(lim)
                
            for i, bar in enumerate(bars):
                x, y = bar.get_xy()
                h, w = bar.get_height(), bar.get_width()
                grad = np.atleast_2d(np.linspace(0, 1*h/max(ydata), 256)).T

                #zorder of 2 to get gradients above the facecolor, but below the bar outlines
                ax.imshow(grad, extent=[x,x+w,y,y+h], origin='lower', aspect="auto",
                          zorder=2, norm=cm.colors.NoNorm(vmin=0,vmax=1), cmap=cmap)
    
    my_bar = plt.bar(grouped_data.index.astype(str), grouped_data.values)
    cmap = plt.get_cmap('cool')
    gradientbars(my_bar, grouped_data.values, cmap)
    #plt.bar(grouped_data.index.astype(str), grouped_data.values)
    
    plt.xlabel(wind_speed_label)
    plt.ylabel("Average Power Production (kW)")
    plt.title("Average Power Production by Wind Speed - {}".format(turbine_code))
    
    plt.grid(color='darkgray')

    # Set x-axis tick labels to display better format
    x_ticks = [f'{bin.left}-{bin.right}' for bin in grouped_data.index]
    plt.xticks(grouped_data.index.astype(str), x_ticks)
    
    # 保存文件
    file_name = "Average_Power_Production_by_Wind_Speed_{}.png".format(turbine_code)
    full_path = os.path.join(dir_path, file_name)
    plt.savefig(full_path)
    # plt.show()
    plt.close()


