import numpy as np
import os
import pandas as pd
# from models.dswe import ComparePCurve, CovMatch
# import pymysql
# import matplotlib.pyplot as plt
# import seaborn as sns
from sklearn.preprocessing import MinMaxScaler


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


# filelist1 = os.listdir(r"H:\scy\文档\能效评估\data")

# sql1_6 = \"SELECT rece_time,grWindSpeed,grWindDirction,grAirPressure,grOutdoorTemperature,grAirDensity,grGridActivePower,mvir_turb_status,grPitchAngle1A,grPitchAngle1B,grPitchAngle2A,grPitchAngle2B,gr  PitchAngle3A,grPitchAngle3B,grRotorSpeed1,grRotorSpeed2 FROM t3000000{}_all WHERE rece_time between '2022-01-01 00:00:00' and '2023-06-30 00:00:00'\".format(i)\n",
# sql7_12 = "SELECT rece_time,VelViento,Direccion,Temp,DensidadAireEst,Potencia,Estado,RotorAnguloPitchPala1,RotorAnguloPitchPala2,RotorAnguloPitchPala3 FROM t3000000{}_all WHERE rece_time between '2022-01-01 00:00:00' and '2023-06-30 00:00:00'".format(i)
# sql13_17 = \"SELECT rece_time,WindSpeed,WindDirection,Temperature,ActivePower,OperationStateInt,BladesPitchAngle FROM t300000{}_all WHERE rece_time between '2022-01-01 00:00:00' and '2023-06-30 00:00: 00'\".format(i)\n",
# sql18_24 = \"SELECT rece_time,CI_WindSpeed1,CI_WindSpeed2,CI_YawError1,CI_YawError2,CI_AirPressureModbusCom,CI_AirTemperatureModbusCom,CI_AirDensityModbusCom,CI_AbsoluteAirHumidityModbusCom,CI_PcsActivePower,WTB_STATUS,CI_RotorSpeed,CI_RotorSpeed2,D_CurrentMeasuredPitchAngle123 FROM t300000{}_all WHERE rece_time between '2022-01-01 00:00:00' and '2023-06-30 00:00:00'\".format(i)\n",
# sql25_29 = \"SELECT rece_time,T_INTWTCState,T_Windspeed10m,T_Windspeed1s,T_Windspeed30s,T_SensorWindDirection10s,T_SensorWindDirection1s,T_SensorWindDirection30s,T_RotorRpm,T_ENG_P, FROM t300000{}_all WHERE rece_time between '2022-01-01 00:00:00' and '2023-06-30 00:00:00'\".format(i)\n",
# sql_lider = \"select real_time,grHWShub0,grHWShub1,grHWShub2,grHWShub3,grHWShub4,grHWShub5,grHWShub6,grHWShub7,grHWShub8,grHWShub9,gbHWShubstatus0,gbHWShubstatus1,gbHWShubstatus2,gbHWShubstatus3,gbHWShubstatus4,gbHWShubstatus5,gbHWShubstatus6,gbHWShubstatus7,gbHWShubstatus8,gbHWShubstatus9,gbLidarStatus FROM t30000{}_all WHERE rece_time between '2022-01-01 00:00:00' and '2023-06-30 00:00:00'\".format(i)\n",
# sql_lider = \"select real_time,T_RadarWind_50m,T_RadarWindDirect_50m,T_RadarWind_100m,T_RadarWindDirect_100m FROM t30000{}_all WHERE rece_time between '2022-01-01 00:00:00' and '2023-06-30 00:00:00'\".format(i)\n",

def hlh_pro():
    filedir = os.listdir("E:\scy\能效评估数据\hlh\原始数据")
    filedir = [i for i in filedir if
               i not in ["process", "zxl_data", "t30000602_all.csv", "t30000606_all.csv", "t30000628_all.csv",
                         "turbine02end.csv"]]
    #
    # #处理数据
    k = 1
    for i in filedir:
        if i == "process":
            pass
        else:
            data = pd.read_csv(os.path.join("E:\scy\能效评估数据\hlh\原始数据", i))
            if k < 7:
                data = data.loc[:, ["rece_time", "grWindSpeed", "grWindDirction", "grGridActivePower"]]
                # data["grGridActivePower"] = data["grGridActivePower"]/3600

            elif 7 <= k <= 12:
                data = data.loc[:, ["rece_time", "VelViento", "Direccion", "Potencia"]]
                # data["Potencia"] = data["Potencia"] / 3650
                # data["Potencia"] = data["Potencia"] / data["Potencia"].max()
                # data = data.drop(data[(data["VelViento"] > 5) & (data["Potencia"] == 0)].index)
                # data = box_outlier(data, "Potencia", 1.5)
                # data = three_sigma(data, "Potencia")
            elif 13 <= k <= 17:
                data = data.loc[:, ["rece_time", "WindSpeed", "WindDirection", "ActivePower"]]
                # data["ActivePower"] = data["ActivePower"] / 3800
                # data["ActivePower"] = data["ActivePower"] / data["ActivePower"].max()
                # data = data.drop(data[(data["WindSpeed"] > 5) & (data["ActivePower"] == 0)].index)
                data["WindDirection"] = data["WindDirection"] - 180
                # data = box_outlier(data, "ActivePower", 1.5)
                # data = three_sigma(data, "ActivePower")
            elif 18 <= k <= 24:
                data = data.loc[:, ["rece_time", "CI_WindSpeed1", "CI_YawError1", "CI_PcsActivePower"]]
                # data["CI_PcsActivePower"] = data["CI_PcsActivePower"] / 3200
                # data["CI_PcsActivePower"] = data["CI_PcsActivePower"] / data["CI_PcsActivePower"].max()
                # data = data.drop(data[(data["CI_WindSpeed1"] > 5) & (data["CI_PcsActivePower"] == 0)].index)
                # data = box_outlier(data, "CI_PcsActivePower", 1.5)
                # data = three_sigma(data, "CI_PcsActivePower")
            elif 25 <= k <= 29:
                data = data.loc[:, ["rece_time", "T_Windspeed1s", "T_SensorWindDirection1s", "T_ENG_P"]]
                # data["T_ENG_P"] = data["T_ENG_P"] /4000
                # data["T_ENG_P"] = data["T_ENG_P"] / data["T_ENG_P"].max()
                # data = data.drop(data[(data["T_Windspeed1s"] > 5) & (data["T_ENG_P"] == 0)].index)
                # data = box_outlier(data, "T_ENG_P", 1.5)
                # data = three_sigma(data, "T_ENG_P")

            data.columns = ["real_time", "wind_speed", "Direction", "power"]
            data.index = pd.to_datetime(data["real_time"])
            data = data.drop(["real_time"], axis=1)
            data = data.resample('10T').mean()
            data.to_csv(r"E:\scy\能效评估数据\hlh\old_data\turbine-采样平均值\{}".format(i))
            k += 1


hlh_pro()

# # 风机能效对比循环版本
# filelist=["t30000001.csv","t30000002.csv","t30000003.csv","t30000005.csv","t30000006.csv"]
#
# data  = pd.DataFrame(columns=["num","feather_num","Weighted diff","Weighted stat diff","Scaled diff","Scaled stat diff","Unweighted diff","Unweighted stat diff"])
# L=[]
# df1 = pd.read_csv(os.path.join(r"H:\scy\文档\能效评估\data",'t30000004.csv')).iloc[:,1:].fillna(1)
# df1 = df1.drop(df1[((df1["grWindSpeed"] > 2.5) & (df1["grGridActivePower"] == 0)) \
#                     | (df1["grWindSpeed"] > 11) & (df1["grGridActivePower"] < 3600 * 0.9) \
#                     | (df1["grWindSpeed"] > 20) | (df1["grGridActivePower"] < 0)].index)
#
# num = 1
# for i in filelist:
#     df2 = pd.read_csv(os.path.join(r"H:\scy\文档\能效评估\data", i)).iloc[:,1:].fillna(1)
#     df2 = df2.drop(df2[((df2["grWindSpeed"] > 2.5) & (df2["grGridActivePower"] == 0)) \
#                        | (df2["grWindSpeed"] > 11) & (df2["grGridActivePower"] < 3600 * 0.9) \
#                        | (df2["grWindSpeed"] > 20) | (df2["grGridActivePower"] < 0)].index)
#     for j in df2.columns:
#         df2 = box_outlier(df2, j)
#         df2 = three_sigma(df2, j)
#         df1 = box_outlier(df1, j)
#         df1 = three_sigma(df1, j)
#
#     colum = []
#     print("start")
#     for k in range(df2.shape[1]-1):
#         colum.append(k)
#         # num = min(df1.shape[0],df2.shape[0])
#         print(colum)
#         Xlist = [df1.iloc[:, colum].to_numpy(), df2.iloc[:, colum].to_numpy()]
#         ylist = [df1.iloc[:, 4].to_numpy(), df2.iloc[:, 4].to_numpy()]
#
#         if len(colum)==1:
#             testcol=[0]
#         else:
#             testcol = [0,1]
#         cpc = ComparePCurve(Xlist, ylist, testcol)
#         data.loc[len(data)] = [i[-6:-4],len(colum),cpc.weighted_diff,cpc.weighted_stat_diff,cpc.scaled_diff,cpc.scaled_stat_diff,cpc.unweighted_diff,cpc.unweighted_stat_diff]
#
#         print('end')
#     num += 1
#
# data.to_csv("compareCurve_speed_dir_update.csv", index=False)


# ## 风机能效对比-获取匹配数据
# df1 = pd.read_csv('turbine-额定功率+采样最大值/t30000001.csv').dropna()
# df1["CI_WindSpeed1"] = round(df1["CI_WindSpeed1"], 1)
# # df1 = df1[(df1.iloc[:,3].values<1)&(df1.iloc[:,3].values>0.1)]
# for i in range(2,6):
#     # data = pd.read_csv("../data/turbine02end.csv")
#
#     df2 = pd.read_csv("turbine-额定功率+采样最大值/t300000{}.csv".format(str(i).rjust(2, "0"))).dropna()
#     # df2 = df2[(df2.iloc[:, 3].values < 1) & (df2.iloc[:, 3].values > 0.1)]
#     # df2 = df2.drop(df2[(df2["CI_WindSpeed1"]<5) &(df2["CI_PcsActivePower"]==0)].index)
#     #data  = pd.DataFrame(columns=["num","Weighted diff","Weighted stat diff","Scaled diff","Scaled stat diff","Unweighted diff","Unweighted stat diff"])
#
# Xlist = [df1.iloc[:, [0,1,2,3]].to_numpy(), df2.iloc[:, [0,1,2,3]].to_numpy()]
# ylist = [df1.iloc[:, 4].to_numpy(), df2.iloc[:, 4].to_numpy()]
# testcol = [0]
# # cpc1 = ComparePCurve(Xlist, ylist, testcol)
# cpc = CovMatch(Xlist,ylist)
# # print("Weighted diff        : {}".format(cpc1.weighted_diff))
# # print("Weighted stat diff   : {}".format(cpc1.weighted_stat_diff))
# # print("Scaled diff          : {}".format(cpc1.scaled_diff))
# # print("Scaled stat diff     : {}".format(cpc1.scaled_stat_diff))
# # print("Unweighted diff      : {}".format(cpc1.unweighted_diff))
# # print("Unweighted stat diff : {}".format(cpc1.unweighted_stat_diff))
#
# data1x = pd.DataFrame(cpc.matched_data_X[0])
# # data1x_0 = pd.DataFrame(cpc1.matched_data_X[0])
# data1x.columns = ["grWindSpeed", "grWindDirction", "grOutdoorTemperature", "grAirDensity", ]
# data2x = pd.DataFrame(cpc.matched_data_X[1])
# data2x.columns = ["grWindSpeed", "grWindDirction", "grOutdoorTemperature", "grAirDensity", ]
# data1y = pd.DataFrame(cpc.matched_data_y[0])
# data1y.columns = ["grGridActivePower"]
# data2y = pd.DataFrame(cpc.matched_data_y[1])
# data2y.columns = ["grGridActivePower"]
#
# datae1x = pd.concat([data1x, data1y], axis=1)
# datae1x.to_csv("turbine2match{}-2.csv".format(str(i[-6:-4])), index=False)
# datae2x = pd.concat([data2x, data2y], axis=1)
# datae2x.to_csv("turbine2match{}-2.csv".format(str(i)), index=False)
#
# # 可视化
# plt.figure()
# plt.scatter(datae1x[datae1x.columns[0]], datae1x[datae1x.columns[-1]], label="datae1x", c="r")
# plt.scatter(datae2x[datae2x.columns[0]], datae2x[datae2x.columns[-1]], label="datae2x", c="b")
# plt.legend()
# plt.title("data24_drop1")
# plt.show()
# # 查看数据中功率的最大值、数据量
# print(datae1x[datae1x.columns[-1]].max())
# print(datae2x[datae2x.columns[-1]].max())
# print(len(datae1x))
# print(len(datae2x))
