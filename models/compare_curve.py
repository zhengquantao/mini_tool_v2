import os

import numpy as np
import pandas as pd

from graph import compare_curve_chart, power_density_chart, power_density_all_chart
from models.utils.data_cleansing import curve_sigmod, sigmoid
from models.utils.data_integration import curve_line_extra
from models.utils.wind_base_tool import cut_speed
from settings.settings import opening_dict, power_theoretical, geolocation


def compare_curve(file_path, num=1, select=False):
    factor_path = opening_dict[os.getpid()]["path"]
    factor_name = factor_path.split(os.sep)[-1]
    turbine_code = file_path.split(os.sep)[-1].split(".")[0]

    plna = str(turbine_code) + "号风机"

    # data = pd.read_csv(file_path).dropna(axis=0)
    data = pd.read_csv(file_path)

    df1, speed_list = cut_speed(data)

    # 功率曲线, 概率密度图和功率曲线图, 异常点, 拟合功率曲线, 清洗后的点
    curve_line, plot_power_distplot, abnormal_scatter, fitting_line, normal_scatter = plot_confidence_interval(
        df1, 0.8, ["wind_speed"], ["power"], plot_name=plna, num=num)

    xticks = np.arange(0, 20.5, 0.5)

    if select:
        plot_power_df, _ = cut_speed(pd.DataFrame({"wind_speed": plot_power_distplot[0],
                                                   "power": plot_power_distplot[1],
                                                   "air_density": df1["air_density"]}))
        file_paths, file_name = power_density_chart.build_html(factor_path, turbine_code, plot_power_df, xticks,
                                                               plot_power_distplot[2])
        return file_paths, file_name

    # 理论功率曲线
    power_line = curve_line_extra(os.path.join(factor_path, power_theoretical), factor_name)
    power_line = (power_line.iloc[:, 0], power_line.iloc[:, 1], "理论功率曲线")

    file_paths, file_name = compare_curve_chart.build_html(factor_path, turbine_code, abnormal_scatter, fitting_line,
                                                           normal_scatter, power_line, xticks)

    return file_paths, file_name


def compare_curve_all(file_path, num=1, select=False):
    factor_path = opening_dict[os.getpid()]["path"]
    factor_name = factor_path.split(os.sep)[-1]

    res_list = []
    for file in os.listdir(file_path):
        if not file.endswith(".csv"):
            continue

        if file in [power_theoretical, geolocation]:
            continue

        turbine_code = file_path.split(os.sep)[-1].split(".")[0]

        plna = str(turbine_code) + "号风机"

        # data = pd.read_csv(file_path).dropna(axis=0)
        data = pd.read_csv(os.path.join(file_path, file))

        df1, speed_list = cut_speed(data)

        # 功率曲线, 概率密度图和功率曲线图, 异常点, 拟合功率曲线, 清洗后的点
        curve_line, plot_power_distplot, abnormal_scatter, fitting_line, normal_scatter = plot_confidence_interval(
            df1, 0.8, ["wind_speed"], ["power"], plot_name=plna, num=num)
        xticks = np.arange(0, 20.5, 0.5)

        plot_power_df, _ = cut_speed(pd.DataFrame({"wind_speed": plot_power_distplot[0],
                                                   "power": plot_power_distplot[1],
                                                   "air_density": df1["air_density"]}))
        plot_power_distplot = (plot_power_df, plot_power_distplot[2])

        res_list.append(
            (curve_line, plot_power_distplot, abnormal_scatter, fitting_line, normal_scatter, xticks, turbine_code)
        )

    if select:

        file_paths, file_name = power_density_all_chart.build_html(factor_path, res_list, factor_name)
        return file_paths, file_name

    # # 理论功率曲线
    # power_line = curve_line_extra(os.path.join(factor_path, power_theoretical), factor_name)
    # power_line = (power_line.iloc[:, 0], power_line.iloc[:, 1], "理论功率曲线")
    #
    # file_paths, file_name = compare_curve_chart.build_html(factor_path, turbine_code, abnormal_scatter, fitting_line,
    #                                                        normal_scatter, power_line, xticks)
    #
    # return file_paths, file_name


def plot_confidence_interval(data, confidence_interval=0.8, use_column=None, target_column=None, plot_name=None,
                             num=None):

    x = data[use_column[0]]
    y = data[target_column[0]]

    y2, popt = curve_sigmod(x, y)
    lower = confidence_interval
    upper = 2-confidence_interval
    lower_bound, popt_low = curve_sigmod(x+2, y2 * lower)
    # lower_bound = lower_bound.apply(lambda x: 0 if x<0 else x)
    upper_bound, popt_upper = curve_sigmod(x-2, y2 * upper)
    # upper_bound = upper_bound.apply(lambda x: y.max() if  x> y.max() else x)

    outliers = data.loc[lambda x: (sigmoid(x[use_column[0]], *popt_low) <= x[target_column[0]]) &
                                  (x[target_column[0]] <= sigmoid(x[use_column[0]], *popt_upper))]
    y3, popt = curve_sigmod(outliers[use_column[0]], outliers[target_column[0]])
    # ##绘制功率曲线
    curve_line = (x, y2, plot_name)

    # # 找到超出置信区间的值的索引
    # outliers_indices = np.where((data[[target_column]] < lower_bound) | (data[[target_column]] > upper_bound))[0]

    # # 删除超出置信区间的值
    # data = np.delete(data[[target_column]], outliers_indices)
    # X_test.sort(axis=0)
    # predictions_amk.sort(axis=0)
    # predictions_temgp.sort(axis=0)

    # ## 概率密度图和功率曲线图
    plot_power_distplot = (x, y2, plot_name)

    # 绘制函数曲线和置信区间c
    # plt.scatter(x, y, label='异常点', color="#FFB48D", alpha=0.5,)
    abnormal_scatter = (x, y, "异常点")

    # plt.plot(sorted(outliers[use_column[0]]), sorted(y3), label="拟合功率曲线", color="red", linewidth=2.0)
    fitting_line = (sorted(outliers[use_column[0]]), sorted(y3), "拟合功率曲线")

    # plt.scatter(outliers[use_column], outliers[target_column], label='清洗后的点', color="#7FBEC2",alpha=0.5)
    normal_scatter = (outliers[use_column[0]], outliers[target_column[0]], '清洗后的点')

    return (curve_line, plot_power_distplot, abnormal_scatter, fitting_line, normal_scatter)


def cut_speeds(data, lable):
    """
    对风速进行划分和分组
    :param data:
    :return:
    """
    data = data[(data[lable] < 18) & (data[lable] >= 0)]
    speed = list(np.linspace(2, 20, 37))
    for i in range(len(speed)):
        subspeed = speed[i]
        data.loc[(data[lable] >= subspeed - 0.25) & (data[lable] < subspeed + 0.25), "groups"] = subspeed
    data.loc[data[lable] < 2.25, "groups"] = -1
    data.loc[data[lable] > 20, "groups"] = len(speed)
    return data, speed
