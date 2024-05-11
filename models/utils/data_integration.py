'''
coding:utf-8
@Software:PyCharm
@Time:2023/9/6 17:25
@Author: Natsu
'''
import os

import pandas as pd
# import matplotlib.pyplot as plt
from models.utils.data_cleansing import *
from models.utils.wind_base_tool import *
from models.utils.AEP.wind_base_tool import *
from models.utils.constants import *


### 文件格式为分月份，不分机组的
from models.utils.data_cleansing import confidence_interval


def modify_data_type(dir, lable: list):
    for i in os.listdir(dir):
        print(i)
        data = pd.read_csv(os.path.join(dir, i))
        for la in lable:
            data[la] = data[la].apply(lambda x: x.replace(",", "") if type(x) is not float and "," in x else x)
            # data = data.astype(float)
        data.to_csv(i, index=False)


def merge_data_mon(file_path, use_label, result_path):
    """
    这里主要是针对数据只分月份，每个月份包含所有的风机的数据
    Parameters
    ----------
    file_path  文件路径
    use_label  所需要的标签
    result_path  结果存放的路径

    Returns
    -------

    """
    file_list = os.listdir(file_path)
    result = pd.DataFrame()
    ##判断存放结果的文件夹是不是存在
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    ## 将所有月份的数据合并在一起
    for file_name in file_list:
        if ".csv" not in file_name:
            continue
        data = pd.read_csv(os.path.join(file_path, file_name))[use_label]
        result = pd.concat([result, data])
    ##从合并的数据中提取不同风机的数据并保存
    for turbine_code in result["turbid"].unique():
        turbine_scada = result[result["turbid"] == turbine_code]
        turbine_scada.to_csv(os.path.join(result_path, str(turbine_code) + '.csv'), index=False)


def merge_data_dir(file_path, use_label, result_path):
    """
    这里针对的是分风机，但是每个风机文件夹中的数据是分月份的，要合并在一起
    Parameters
    ----------
    file_path
    use_label
    result_path

    Returns
    -------

    """
    ## 首先需要获取存放不同风机数据的文件夹
    file_list = os.listdir(file_path)
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    ## 这里首先获取外面一层文件夹的列表，
    for turbine in file_list:
        if turbine == "处理完成数据":
            continue
        print(turbine)
        data_path = os.path.join(file_path, turbine)
        result = pd.DataFrame()
        # 这里提取文件夹的数据，进行合并
        for Da in os.listdir(data_path):
            print(Da)
            if ".csv" in Da:
                data = pd.read_csv(os.path.join(data_path, Da), skiprows=8)[use_label]
            elif "xls" in Da or "xlsx" in Da:
                data = pd.read_excel(os.path.join(data_path, Da), skiprows=8)[use_label].iloc[1:, :]

            else:
                return "数据格式不对"
            data = data[(data["并网运行"] == 1) & (data["维护"] == 0)]
            data.drop(["并网运行", "维护"], axis=1, inplace=True)
            result = pd.concat([result, data])
        result.to_csv(os.path.join(result_path, f"{turbine}.csv"), index=False)


def curve_line_extra(power_curve_path, factor_name):
    """
    针对一个文件中多个风机型号的功率曲线
    Returns
    -------

    """
    power_curve = pd.read_csv(power_curve_path)
    if factor_name == "myse":
        power_line = power_curve[(power_curve["MODEL_"] == "MySE3.6") &
                                 (power_curve["FARM_CODE"] == 30000) & (power_curve["WINDS_SPEED"] < 20)][
            ["WINDS_SPEED", "WINDS_POWER"]].sort_values(by="WINDS_SPEED")
    elif factor_name == "wsts":

        power_line = power_curve[(power_curve["MODEL_"] == "V126-3.8") &
                                 (power_curve["FARM_CODE"] == 30000) & (power_curve["WINDS_SPEED"] < 20)][
            ["WINDS_SPEED", "WINDS_POWER"]].sort_values(by="WINDS_SPEED")

    elif factor_name == "gms":

        power_line = power_curve[
            (power_curve["MODEL_"] == "SG3.65") & (power_curve["FARM_CODE"] == 30000) & (
                    power_curve["WINDS_SPEED"] < 20)][
            ["WINDS_SPEED", "WINDS_POWER"]].sort_values(by="WINDS_SPEED")

    elif factor_name == "lhdl":

        power_line = power_curve[(power_curve["MODEL_"] == "UP3200") &
                                 (power_curve["FARM_CODE"] == 30000) & (power_curve["WINDS_SPEED"] < 20)][
            ["WINDS_SPEED", "WINDS_POWER"]].sort_values(by="WINDS_SPEED")
    elif factor_name == "dfdq":
        power_line = power_curve[(power_curve["MODEL_"] == "DEW-D4000") & (power_curve["FARM_CODE"] == 30000) & (
                power_curve["WINDS_SPEED"] < 20)][["WINDS_SPEED", "WINDS_POWER"]].sort_values(by="WINDS_SPEED")
    else:
        power_line = power_curve
    return power_line


def compare_curve(factor_name, file_path, power_curve_path):
    path = os.path.join(file_path, factor_name)
    num = 0
    plt.figure(figsize=(8, 6))
    for i in os.listdir(path):
        data = pd.read_csv(os.path.join(path, i)).dropna(axis=0)
        df1, speed_list = cut_speed(data, "wind_speed")
        df, c = confidence_interval(df1, 0.9, ["wind_speed"], ["power"],
                                    title_name=str(int(i.split("t3")[1].split(".csv")[0])) + "号风机", num=num)
        num += 1

    power_line = curve_line_extra(power_curve_path, factor_name)
    plt.plot(power_line["WINDS_SPEED"], power_line["WINDS_POWER"], "k.", linewidth=2.0, label="理论功率曲线")

    plt.legend(loc="best", ncol=2,
               # bbox_to_anchor=(1.05, 0)
               )
    plt.tight_layout()
    plt.show()
    plt.savefig("%s功率曲线.png".format(factor_name))


def extra_data(scada_file, theory_curve, factor_name):
    if factor_name == "hlh":
        ##霍林河处理  t30000001
        if int(scada_file.split(".csv")[0][-3:]) < 7:
            theory_curve = theory_curve[theory_curve["MODEL_DATAIL"] == "MySE3.6-135"][["WINDS_SPEED", "WINDS_POWER"]]

        elif 7 <= int(scada_file.split(".csv")[0][-3:]) < 13:
            theory_curve = theory_curve[theory_curve["MODEL_DATAIL"] == "SG3.65-132"][["WINDS_SPEED", "WINDS_POWER"]]

        elif 13 <= int(scada_file.split(".csv")[0][-3:]) < 18:
            theory_curve = theory_curve[theory_curve["MODEL_DATAIL"] == "V3.8-126"][["WINDS_SPEED", "WINDS_POWER"]]

        elif 18 <= int(scada_file.split(".csv")[0][-3:]) < 25:
            theory_curve = theory_curve[theory_curve["MODEL_DATAIL"] == "UP3.2-141"][["WINDS_SPEED", "WINDS_POWER"]]

        elif 25 <= int(scada_file.split(".csv")[0][-3:]) < 30:
            theory_curve = theory_curve[theory_curve["MODEL_DATAIL"] == "DEW-D4.0-148"][["WINDS_SPEED", "WINDS_POWER"]]
        theory_curve.sort_values(by="WINDS_SPEED", inplace=True)
    else:
        return theory_curve
    return theory_curve


def get_mount_power_mean(file_path):
    file_list = os.listdir(file_path)
    result = pd.DataFrame(columns=list(np.linspace(2, 25, 47)))
    num = pd.DataFrame(columns=list(np.linspace(2, 25, 47)))

    for i in file_list:
        print(i)
        data = pd.read_csv(os.path.join(file_path, i))
        data.columns = ["wind_speed", "Direction", "Tem", "density", "power"]
        data, speed_list = cut_speed(data)
        l = []
        k = []
        for i in speed_list:
            print(f"在{i}风速段有{data[data['groups'] == i].shape[0]}条数据")
            print(f"在{i}风速段的平均功率为{data[data['groups'] == i]['power'].mean()}MW")
            l.append(data[data['groups'] == i]['power'].mean())
            k.append(data[data['groups'] == i].shape[0])

        result.loc[len(result)] = l
        num.loc[len(num)] = k

    result.to_csv("风速段平均功率.csv")
    num.to_csv("风速段数据量.csv")
