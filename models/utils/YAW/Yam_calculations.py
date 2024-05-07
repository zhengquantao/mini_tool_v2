import os
import math
import pandas as pd
import numpy as np


def data_pro(data, speed_lable, dir_lable1, dir_lable2, num=1):
    if num == 1:
        data["YawDirction"] = data[dir_lable1] - data[dir_lable2]
    else:
        data["YawDirction"] = data[dir_lable1]
    data = data[((data["YawDirction"] >= -10) & (data["YawDirction"] <= 10))]
    data = data[(data[speed_lable] > 3) & (data[speed_lable] < 11)]

    carbine = np.arange(0.0, 11.5, 0.5)
    speedLabels = ["0-0.5", "0.5-1", "1-1.5", "1.5-2", "2-2.5", "2.5-3", "3-3.5", "3.5-4", "4-4.5", "4.5-5", "5-5.5",
                   "5.5-6", "6-6.5", "6.5-7", "7-7.5", "7.5-8", "8-8.5", "8.5-9", "9-9.5", "9.5-10",
                   "10-10.5", "10.5-11", ]
    # "11-11.5", "11.5-12", "12-12.5", "12.5-13", "13-13.5", "13.5-14", "14-14.5", "14.5-15", "15-15.5", "15.5-16","16-16.5", "16.5-17", "17-17.5", "17.5-18"]
    data['grWindSpeed_lable'] = pd.cut(data[speed_lable], bins=carbine, labels=speedLabels, include_lowest=True)
    carbine = np.arange(-10, 11, 1)
    dirLabels = ["-10°_-9°", "-9°_-8°", "-8°_-7°", "-7°_-6°", "-6°_-5°", "-5°_-4°", "-4°_-3°", "-3°_-2°", "-2°_-1°",
                 "-1°_0°", "0°_1°", "1°_2°",
                 "2°_3°", "3°_4°", "4°_5°", "5°_6°", "6°_7°", "7°_8°", "8°_9°", "9°_10°"]
    data['Dirction_lable'] = pd.cut(data['YawDirction'], bins=carbine, labels=dirLabels, include_lowest=True)
    return data


def power_d(data, speed_label, power_label):
    end = pd.DataFrame()
    st = pd.DataFrame()
    R = 140.68
    colums = data["grWindSpeed_lable"].unique().tolist()
    Index = data["Dirction_lable"].unique().tolist()
    for i in colums:
        L = []
        K = []
        for j in Index:
            data_end = data[(data["grWindSpeed_lable"] == i) & (data["Dirction_lable"] == j)]
            p = 1.2
            V = data_end[speed_label]
            A = math.pi * (R / 2) ** 2
            Cp = 2 * data_end[power_label] / (p * A * V ** 3)
            P = 0.5 * p * A * Cp
            L.append(P.mean())
            K.append(data_end.shape[0])
            print(data_end.shape[0])
        end[i] = L
        st[i] = K
        print("-----------------------------------------------------")
    end.index = Index
    st.index = Index
    return end, st


rootpath = "H:\scy\文档\能效评估\偏航\data"
filepath = os.listdir(rootpath)
for i in filepath:
    data = pd.read_csv(os.path.join(rootpath, i))
    if 0 < int(i[-6:-4]) < 7:
        data = data_pro(data, "grWindSpeed", "grWindDirctionToNorth", "grNacellePositionToNorth")
        end, st = power_d(data, "grWindSpeed", "grGridActivePower")
    elif 7 <= int(i[-6:-4]) <= 12:
        continue
    elif 13 <= int(i[-6:-4]) <= 17:
        data = data_pro(data, "WindSpeed", "NacelleDirection", "WindDirection")
        end, st = power_d(data, "WindSpeed", "ActivePower")
    elif 18 <= int(i[-6:-4]) <= 24:
        data = data_pro(data, "CI_WindSpeed1", "CI_YawError1", "", 0)
        end, st = power_d(data, "CI_WindSpeed1", "CI_PcsActivePower")
    elif 25 <= int(i[-6:-4]) <= 29:
        continue
        # data = data_pro(data, "grWindSpeed", "grNacellePositionToNorth", "grWindDirctionToNorth", 0)
        # end = power_d(data, "grWindSpeed", "grGridActivePower")
    else:
        continue

    end.columns = data["grWindSpeed_lable"].unique().tolist()

    end.to_excel(r"H:\scy\文档\能效评估\偏航\turbine{}出力.xlsx".format(i[-6:-4]), encoding="gbk")
    st.to_excel(r"H:\scy\文档\能效评估\偏航\turbine{}容量.xlsx".format(i[-6:-4]), encoding="gbk")
