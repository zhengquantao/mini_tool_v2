import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
import os
from scipy.optimize import curve_fit
import math
from models.utils.data_cleansing import *


# ======================================================================================================================
# 异常值清洗
def merge_data(file_path):
    list_dir = os.listdir(file_path)
    result = pd.DataFrame()
    for i in list_dir:
        data = pd.read_csv(os.path.join(file_path, i), encoding="gbk")
        result = pd.concat([result, data], axis=1)

    return result


def box_drop_abnormal(subdata, name):
    """
    通过箱线图去除异常值
    :param subdata:
    :return:
    """
    # 1 利用箱线图去除异常值
    q1 = subdata.loc[subdata["label"] == 0, name].quantile(q=0.25)
    q3 = subdata.loc[subdata["label"] == 0, name].quantile(q=0.75)
    low_whisker = q1 - 1.5 * (q3 - q1)
    up_whisker = q3 + 1.5 * (q3 - q1)
    subdata.loc[(subdata[name] < low_whisker) | (subdata[name] > up_whisker), "label"] = 2

    # 2 利用3delta原则去除异常值
    lower_bound = np.mean(subdata[name]) - (3 * np.std(subdata[name]))
    upper_bound = np.mean(subdata[name]) + (3 * np.std(subdata[name]))
    subdata.loc[(subdata[name] < lower_bound) | (subdata[name] > upper_bound), "label"] = 3
    return subdata


def rule_removal(data, rate_speed, cap):
    """
    基于基本规则去除异常值
    :param data:
    :return:
    """
    # 1 当风速超过2.5m/s，功率为0的点为异常值
    data["label"] = 0

    # 2 根据风速-功率来
    data.loc[(data["speed"] > 2.5) & (data["power"] == 0), "label"] = 1
    data.loc[(data["speed"] > rate_speed) & (data["power"] < cap * 0.7), "label"] = 1
    data.loc[data["speed"] > 20, "label"] = 1
    data.loc[data["power"] < 0, "label"] = 1
    return data


def cut_speed(data):
    """
    对风速进行划分和分组
    :param data:
    :return:
    """
    speed = list(np.linspace(2, 25, 47))
    for i in range(len(speed)):
        subspeed = speed[i]
        data.loc[(data["speed"] >= subspeed - 0.25) & (data["speed"] < subspeed + 0.25), "groups"] = subspeed
    data.loc[data["speed"] < 2.25, "groups"] = -1
    data.loc[data["speed"] > 20, "groups"] = len(speed)
    return data, speed


# ======================================================================================================================
# 曲线拟合
def sigmoid(x, L, x0, k, b):
    """
    sigmoid函数拟合回归
    :param x:
    :param L:
    :param x0:
    :param k:
    :param b:
    :return:
    """
    y = L / (1 + np.exp(-k * (x - x0))) + b
    return y


def curve_fitting(data, speed):
    """
    拟合功率曲线
    :param data:
    :return:
    """
    # try:
    #     data = data[data["label"] == 0].reset_index(drop=True)
    # except Exception as e:
    #     print("无需执行此步骤！")

    p0 = [data["power"].max(), data["speed"].mean(), 1, data["power"].min()]
    popt, pcov = curve_fit(sigmoid, data["speed"], data["power"], p0, method="dogbox")  # p0：函数参数的初始值，从而减少计算机的计算量
    if sigmoid(20, *popt) > data["power"].max():
        k = 1 + np.exp(-popt[2] * (20 - popt[1]))
        popt[0] = (data["power"].max() - popt[3]) * k

    curve = pd.DataFrame(speed)
    curve["power"] = pd.DataFrame(sigmoid(speed, *popt))
    curve.columns = ["speed", "actual_power"]
    return popt, curve


def plot_power_curve(data):
    """
    根据实际情况绘制功率曲线，计算其平均值
    :param data:
    :return:
    """
    # 1 对风速划分区间
    data, speed = cut_speed(data)

    # 2 根据2个思路绘制实际功率曲线
    speed_data = data.groupby("groups")
    all_data = pd.DataFrame()

    for index, subdata in speed_data:
        if len(subdata) > 0.0001 * len(data):
            # 2.1 根据IEC生成实际功率
            actual_power = subdata["power"].mean()
            actual_power_curve = pd.DataFrame([index, actual_power]).T
            actual_power_curve.columns = ["speed", "actual_power"]
            all_data = all_data.append(actual_power_curve)
    all_data = all_data[all_data["speed"] != -1].sort_values("speed").reset_index(drop=True)
    return all_data


def theory_curve_preprocess(data, ratio, speed):
    """
    理论功率曲线处理
    :param data:
    :return:
    """
    data1, data2 = data.copy(), data.copy()
    # 空气密度转换
    data1["speed"] = data1["speed"].apply(lambda x: x / pow((ratio / 1.225), 1 / 3))
    # data1["speed"] = data1["speed"] + 0.5

    # 直接对转换的理论功率曲线进行线性拟合（问题点：曲线不够平滑）
    data2["theory_power"] = np.nan
    all_data = data1.append(data2).sort_values("speed")
    all_data = all_data.interpolate()
    all_data = all_data.fillna(method="bfill")
    all_data.columns = ["speed", "theory_power1"]
    theory_curve = pd.merge(all_data, data, left_on="speed", right_on="speed", how="inner")
    theory_curve = theory_curve[["speed", "theory_power1"]]
    theory_curve.columns = ["speed", "theory_power"]
    theory_curve["theory_power"] = theory_curve["theory_power"].astype("int32")

    # 可用sigmoid曲线拟合回归
    data1 = data1.rename(columns={"theory_power": "power"})
    popt, theory_curve = curve_fitting(data1, speed)
    theory_curve = theory_curve.rename(columns={"actual_power": "theory_power"})

    # 理论功率效果过好，进行部分微调，主要是性能过好，将其调低
    # theory_curve["speed"] = theory_curve["speed"] + 0.5
    # theory_curve["theory_power"] = theory_curve["theory_power"] - 8
    theory_curve.loc[theory_curve["theory_power"] < 0, "theory_power"] = 0
    theory_curve = theory_curve.reset_index(drop=True)
    return theory_curve


# ======================================================================================================================
# 数据可视化
def scatter_two(data):
    """
    对数据进行可视化
    :param data:
    :return:
    """
    plt.figure()
    sns.scatterplot(data=data, x=data["speed"], y=data["power"], hue="label")
    plt.title("speed_power")
    plt.show()


def scatter_curve(data, curve, subturbine):
    """
    绘制散点图和曲线
    :param data:
    :param speed:
    :param popt:
    :return:
    """
    plt.figure()
    # sns.scatterplot(data=data, x=data["speed"], y=data["power"])
    plt.plot(curve["speed"], curve["actual_power"], c="blue", label="actual_curve")
    plt.plot(curve["speed"], curve["theory_power"], c="black", label="theory_curve")
    plt.legend()
    plt.title(subturbine)
    # plt.show()
    plt.savefig("./img/{}.png".format(subturbine))


# ======================================================================================================================
# 计算电量
def speed_cdf(speed, speed_avg):
    """
    计算风速的瑞丽累积概率分布函数
    :param speed:
    :return:
    """
    cdf = 1 - math.exp(-math.pi / 4 * (speed / speed_avg) ** 2)
    return cdf


def count_speed(data, speedi, speedi_1):
    """
    统计实际的风频概率
    :param data:
    :param speedi:
    :param speedi_1:
    :return:
    """
    # 计算风速区间的概率
    speed_prob = len(data[(data["speed"] < speedi) & (data["speed"] >= speedi_1)]) / len(data)
    return speed_prob


def aep_calculate(data, power_curve, subturbine):
    """
    电量计算
    :param data:
    :param curve:
    :return:
    """
    # 1 取正常运行的数据，并对数据进行降采样，降为1h，然后统计其风速的平均值
    # normal_data = data[data["label"] == 0].set_index("real_time")
    data.index = pd.to_datetime(data.index)
    normal_data = data[["speed", "power"]]
    # normal_data = normal_data.resample("1H").mean()

    # 2 提取基本信息和计算对应的数据缺失量
    # turbine_code = data.loc[0, "turbine_code"]
    all_length = len(normal_data)
    normal_data = normal_data.dropna().sort_index()
    miss_length = all_length - len(normal_data)
    power_hours = len(normal_data)
    # start_time = normal_data.index[0]
    # end_time = normal_data.index[-1]
    min_speed, mean_speed, max_speed = normal_data["speed"].min(), normal_data["speed"].mean(), normal_data[
        "speed"].max()
    min_power, mean_power, max_power = normal_data["power"].min(), normal_data["power"].mean(), normal_data[
        "power"].max()

    # 3 计算发电量
    iec_power, pdf_power = 0, 0
    for i in range(1, len(power_curve)):
        speedi, speedi_1 = power_curve.loc[i, "speed"], power_curve.loc[i - 1, "speed"]
        speed_prob = count_speed(normal_data, speedi, speedi_1)
        iecpoweri, iecpoweri_1 = power_curve.loc[i, "actual_power"], power_curve.loc[i - 1, "actual_power"]
        pdfpoweri, pdfpoweri_1 = power_curve.loc[i, "theory_power"], power_curve.loc[i - 1, "theory_power"]
        # 根据风速的分布计算对应的发电量
        iec_power = iec_power + (speed_cdf(speedi, mean_speed) - speed_cdf(speedi_1, mean_speed)) * (
                    iecpoweri + iecpoweri_1) / 2
        pdf_power = pdf_power + (speed_cdf(speedi, mean_speed) - speed_cdf(speedi_1, mean_speed)) * (
                    pdfpoweri + pdfpoweri_1) / 2
        # # 根据实际的风速分布计算对应的发电量
        # iec_power = iec_power + speed_prob * (iecpoweri + iecpoweri_1) / 2
        # pdf_power = pdf_power + speed_prob * (pdfpoweri + pdfpoweri_1) / 2
    iec_power = int(iec_power * power_hours) / 1000
    pdf_power = int(pdf_power * power_hours) / 1000
    # 计算机组的性能比
    performance_ratio = (iec_power - pdf_power) / pdf_power * 100
    # print("IEC_aep为{}，pdf_aep为{}，性能比为{}".format(iec_power, pdf_power, performance_ratio))

    # 4 将统计信息和相关的数据组合起来
    statistics = pd.DataFrame(
        [subturbine, miss_length, power_hours, round(min_speed, 2), round(mean_speed, 2), round(max_speed, 2),
         round(min_power, 2), round(mean_power, 2), round(max_power, 2), round(iec_power, 2), round(pdf_power, 2),
         round(performance_ratio, 2)]).T
    statistics.columns = ["turbine", "miss_length", "power_hours", "min_speed", "mean_speed", "max_speed", "min_power",
                          "mean_power", "max_power", "iec_power(mWh)", "pdf_power(mWh)", "performance_ratio"]
    return statistics


# ======================================================================================================================
# 其他辅助函数
def basic_information(subturbine, turbine_code, turbine_type, rate_speed):
    """
    配对每台机组的机型、额定风速
    :param subturbine:
    :param turbine_code:
    :param turbine_type:
    :param rate_speed:
    :return:
    """
    if subturbine in turbine_code:
        cap = 1500
        turbine_type = turbine_type[0]
        rate_speed = rate_speed[0]
    else:
        cap = 1500
        turbine_type = turbine_type[1]
        rate_speed = rate_speed[1]
    return cap, turbine_type, rate_speed


def drop_abnormal(data):
    """
    去除异常值主函数
    :param data:
    :return:
    """
    # 1 按照风速区间划分
    data, speed = cut_speed(data)

    # 2 分区间标注异常值
    speed_data = data.groupby("groups")
    all_data = pd.DataFrame()
    for index, subdata in speed_data:
        if len(subdata) > 0.001 * len(data):
            subdata = box_drop_abnormal(subdata, "power")
        all_data = all_data.append(subdata)
    return all_data, speed


# ======================================================================================================================
# 主函数
def iec_main_pro(data_path, wind_col, target_columns):
    """
    主程序执行
    :return:
    """

    list_dir = os.listdir(data_path)
    # 2 筛选正常运行的数据和部分异常值清洗
    all_statistics = pd.DataFrame()
    for subturbine in list_dir:
        data = pd.read_csv(os.path.join(data_path, subturbine))
        ratio = 1.0496

        # 1 提取正常运行的数据，并只提取相关标签，并限制风速、功率的标签为speed和power
        # data = data[data["平均机组运行模式"] == 20].reset_index(drop=True)
        data = data[wind_col + target_columns]
        # data.columns = ["speed", "power"]
        # subturbine = "3C-30"
        print("开始处理{}机组的数据".format(subturbine))

        # 2 基于功率曲线去除部分异常值
        subdata_2, clean_percentage = confidence_interval(data, 0.8, wind_col, target_columns)

        # 2.1 拟合实际功率曲线，并生成对应的实际功率曲线到表中（此为功率曲线拟合和求实际的平均值）
        # popt, actual_curve = curve_fitting(subdata_2, speed)
        subdata_2.columns = ["speed", "power"]
        actual_curve = plot_power_curve(subdata_2)

        # 2.2 结合理论功率进行计算对比
        theory_curve = pd.read_excel(r"./config/power_curve.xlsx")
        theory_curve.columns = ["speed", "theory_power"]
        theory_curve = theory_curve_preprocess(theory_curve, ratio, subdata_2["speed"])
        curve = pd.merge(theory_curve, actual_curve, left_on="speed", right_on="speed", how="inner")
        scatter_curve(subdata_2, curve, subturbine)  # 功率曲线绘制，并保存图片到对应的路径下

        # 2.3 电量计算
        statistics = aep_calculate(subdata_2, curve, subturbine.split(".csv")[0])
        all_statistics = all_statistics.append(statistics).reset_index(drop=True)
    all_statistics.to_csv(r"./result/result.csv")

# if __name__ == "__main__":
#     main()
