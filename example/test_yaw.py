import os
import warnings
import numpy as np
import pandas as pd
import statistics as stat
import scipy.stats as stats
import seaborn as sns
import configparser
import pymysql
# import psycopg2

import matplotlib.pyplot as plt
import uuid
from sklearn.cluster import DBSCAN

import matplotlib as mpl
mpl.use('Agg')
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()

plt.rcParams['font.sans-serif'] =  ['SimHei']


plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'
plt.rcParams['axes.unicode_minus'] = False


# 标签名
pitch_angel_label_1 = '平均桨叶2角度'
pitch_angel_label_2 = '平均桨叶3角度'
# pitch_angel_label_3 = 'ipitchangle3_avg'

power_label = 'power'
wind_direction_label = 'wind_direction'
nacell_direction_label = 'nacelle_direction'
wind_speed_label = 'wind_speed'
gen_speed_label = 'generator_speed'
# db="scadadb_202401_202406"
#
# use_table= 'my2000_onedata'

model_type= 'MY2.0'

data_time_name ='real_time'

turbine_name = 'turbine_code'

airdensity_name = 'air_density'


# data_conn = conn_1(db)
# #
# sql = f"SELECT {pitch_angel_label_1},{pitch_angel_label_2},{pitch_angel_label_3},{gen_speed_label},{nacell_direction_label},{power_label},{airdensity_name},{wind_direction_label},{wind_speed_label}, {turbine_name},{data_time_name} FROM \"{use_table}\" where  {data_time_name} >='2024-01-01 00:00:00' and {data_time_name} <'2024-04-01 00:00:00'"
#
# data = pd.read_sql(sql=sql, con=data_conn)
# data.to_csv('orig_data.csv')
# df= data

import chardet
data_path = r'C:\Users\EDY\Desktop\30057\30057014.csv'
with open(data_path, 'rb') as f:
    raw_data = f.read(10000)  # 读取部分数据来检测编码
    result = chardet.detect(raw_data)
    encoding = result['encoding']

# 使用检测到的编码读取 CSV
data = pd.read_csv(data_path, encoding=encoding)

# 选择非偏航工况
blade_angles = [pitch_angel_label_1,pitch_angel_label_2]
data['桨叶角度'] = data[blade_angles].mean(axis=1)

data = data.loc[data['桨叶角度'] < 10,:]
data = data.loc[data[power_label] > 100,:].reset_index(drop=True)
# 剔除异常数据
# data = data[data[wind_direction_label].rolling(100).var() > 1]

# plt.figure()
# # plt.plot(data['桨叶角度'],'b*')
# # # plt.show(block=True)
# #
# # plt.figure()
# # plt.plot(data[wind_direction_label],'b*')
# # # plt.show(block=True)
# #
# # plt.figure()
# # plt.plot(data[nacell_direction_label],'b*')
# # # plt.show(block=True)
#
# plt.figure()
# plt.plot(data[nacell_direction_label] - data[wind_direction_label],'b*')
#
# plt.figure()
# plt.plot(data['yaw_angle'],'b*')
#
# plt.figure()
# plt.hist(x=data['yaw_angle'],bins =50,edgecolor ='white',density = True)
# plt.show(block=True)

# plt.figure()
# # plt.plot(data['桨叶角度'],'b*')
# # # plt.show(block=True)
data['yaw_angle'] = data[nacell_direction_label]
# data = data.loc[abs(data['yaw_angle'])<25,:]
data [wind_direction_label] = data['yaw_angle']
power_bins = list(range(100, 2200, 400))
power_labels = [200 + i for i in power_bins][:-1]
data['功率区间'] = pd.cut(data[power_label], bins=power_bins, labels=power_labels)

fig_m, axs_m = plt.subplots(figsize=(10, 8))
cmap = mpl.cm.get_cmap("tab20")
color_list = cmap(range(1, len(power_labels) * 2, 2))
yaw_err_dic = {}
sub_figs = []
turbine_codes = data[turbine_name].unique()
results_all = []
idex = 0
for turbine_id in turbine_codes:
    print(turbine_id)
    idex = idex + 1
    print(idex)
    df = data.loc[data[turbine_name]==turbine_id,:].reset_index(drop=True)
    df = df.sort_values(by=data_time_name).reset_index(drop=True)

    # df['is_same'] = df[wind_speed_label] == df[wind_speed_label].shift(1)
    # diff_val =df[~df['is_same'].ne(df['is_same'].shift(1))]
    # df['is_same'].iloc[0] = False  # 将第一行的'is_same'设为False，因为没有前一个值可以比较
    # # 使用cumsum对连续相同的值进行分组
    # df['group'] = df['is_same'].ne(df['is_same'].shift(1)).cumsum()
    # # 计算每个组的长度
    # group_lengths = df.groupby('group')['group'].transform('size')
    # # 查找长度大于或等于10的组
    # long_groups = group_lengths[group_lengths >= 10]

    # plt.figure()
    # plt.plot(df.loc[0:1000,'rectime'],df.loc[0:1000,wind_direction_label], 'b*-')
    # plt.figure()
    # plt.plot(df.loc[0:1000,'rectime'],df.loc[0:1000,wind_speed_label], 'b*-')
    # plt.show(block=True)

    fig_m, axs_m = plt.subplots(figsize=(10, 8))
    cmap = mpl.cm.get_cmap("tab20")
    color_list = cmap(range(1, len(power_labels) * 2, 2))
    yaw_err_dic = {}
    sub_figs = []
    eps_id = 0.05
    sample_id = 20
    for i, power_i in enumerate(power_labels):
        c_i = color_list[i]
        df_p = df[df['功率区间'] == power_i]
        if len(df_p) < 400:
            print(f'功率{power_i}单个功率区间数据量太少！')
            # continue
        df_p = df_p[df_p[wind_speed_label] < df_p[wind_speed_label].mode()[0]]  # 为什么这么处理
        df_c = df_p[[wind_direction_label, wind_speed_label, power_label]]

        # plt.figure()
        # sns.scatterplot( x=df_c[wind_speed_label],y= df_c[wind_direction_label], marker='*', color='b', label='风速-偏航散点图')
        # plt.show()

        df_c.dropna(inplace=True)
        if len(df_p)<50:
            df_c0 = df_c
        else:
            db = DBSCAN(eps=eps_id, min_samples=sample_id)
            df_c['norm_wind_speed'] = scaler.fit_transform(df_c[[wind_speed_label]]).ravel()
            df_c['norm_wind_direct'] = scaler.fit_transform(df_c[[wind_direction_label]]).ravel()
            db.fit(df_c[['norm_wind_speed', 'norm_wind_direct']])
            # db.fit(df_c[[wind_speed_label, wind_direction_label]])
            df_c['cluster'] = db.labels_
            # 计算每个类别的数量
            counts = df_c['cluster'].value_counts()
            # 展示聚类效果图
            # plt.figure()
            # sns.scatterplot(data= df_c, y=df_c[wind_speed_label], x=df_c[wind_direction_label], hue='cluster', marker='*',
            #                 label='风速-偏航散点图')
            # plt.title(f'eps={eps_id}-sample={sample_id}-{turbine_id}功率段{power_i}kW-DBSCAN聚类')
            # local_fig_path = 'eps={}-sample={}-{}功率段{}DBSCAN聚类.jpg'.format(eps_id,sample_id,turbine_id, power_i)
            # plt.savefig(local_fig_path)
            # plt.show(block=True)
            df_c0 = df_c[df_c['cluster'] != -1]

        df_c0 = df_c0[df_c0[wind_direction_label].abs() < 40]
        if len(df_c0)<20:
            print("---------------------")
            continue
        # print(len(df_c0))
        # dir_bins = np.arange(-40, 40, 1)
        dir_bins = np.arange(min(df_c0[wind_direction_label])-1, max(df_c0[wind_direction_label])+1, 1)
        dirs = [i + 0.5 for i in dir_bins][:-1]
        df_c0['风向区间'] = pd.cut(df_c0[wind_direction_label], bins=dir_bins, labels=dirs)
        dir_power_i = df_c0.groupby(by='风向区间')[wind_speed_label].min()

        # dir_power_i = dir_power_i.rolling(3, min_periods=1).mean()
        dir_power_i.dropna(inplace=True)
        x = np.array(dir_power_i.index)
        X = np.c_[x ** 2, x, np.ones_like(x)]
        coe = np.linalg.pinv(X) @ dir_power_i.values
        y_pre = X @ coe
        y_pre = pd.Series(y_pre, index=x)
        yaw_err_i = -coe[1] / (2 * coe[0])
        min_wind_i = coe[0] * yaw_err_i * yaw_err_i + coe[1] * yaw_err_i + coe[2]
        # 判断拟合是否有效，拟合曲线需开口朝上，便差异不能太大
        valid_flag = coe[0] > 0 and np.abs(yaw_err_i) <= 15
        # valid_flag = 1
        # if abs(yaw_err_i)>max(df_c0[wind_direction_label].abs()):
        #     yaw_err_i = np.mean(df_c0[wind_direction_label])
        #     min_wind_i = min(df_c0[wind_speed_label])
        axs = df_c0.plot(kind='scatter', x=wind_direction_label, y=wind_speed_label, color=c_i, figsize=(10, 8), s=0.2)
        # axs.plot(y_pre, color=c_i)
        # axs.plot(yaw_err_i, min_wind_i, '*r', markersize=8)
        axs.axvline(x=0, ymin=0, ymax=0.8, linestyle="--", color='red')
        plt.title(f'{turbine_id}功率段{power_i}kW-偏航对风误差：{np.round(yaw_err_i, 1)}')
        if valid_flag:
            axs.plot(y_pre, color=c_i)
            axs.plot(yaw_err_i, min_wind_i, '*r', markersize=8)

        local_fig_path = '{}功率段{}偏航对风_{}.jpg'.format(turbine_id, power_i,uuid.uuid1())
        plt.savefig(local_fig_path)
        plt.close()
        sub_figs.append(local_fig_path)

        # 主图中画图
        df_c0.plot(ax=axs_m, kind='scatter',  x=wind_direction_label, y=wind_speed_label, color=c_i, s=0.2, alpha=0.3)
        if valid_flag:
            axs_m.plot(y_pre, color=c_i)
            axs_m.plot(yaw_err_i, min_wind_i, '*r', markersize=8)

            yaw_err_dic[power_i] = yaw_err_i

    yaw_err_s = pd.Series(yaw_err_dic)
    yaw_err_mean = np.round(yaw_err_s.mean(), 1)
    axs_m.axvline(x=0, ymin=0, ymax=0.8, linestyle="--", color='red')
    axs_m.set_title(f'{turbine_id}_偏航对风误差：{yaw_err_mean}  偏航状态：正常')
    # 添加color_bar
    cmap = mpl.colors.ListedColormap(color_list)
    norm = mpl.colors.BoundaryNorm(power_bins, cmap.N)
    fig_m.colorbar(
        mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
        ax=axs_m,
        ticks=power_bins,
        spacing='proportional',  # 刻度成比例
        label='有功功率（kW）',
    )

    main_fig = '{}偏航对风整体图_{}.jpg'.format( turbine_id, uuid.uuid1())
    fig_m.savefig(main_fig, bbox_inches='tight')

    result = yaw_err_mean
    print('result:', result)

    weight_mean_abs = np.abs(yaw_err_mean)

    if weight_mean_abs >= 8:
        status = '故障'
    elif weight_mean_abs >= 6:
        status = '告警'
    elif weight_mean_abs >= 4:
        status = '注意'
    else:
        status = '正常'

    if status != '正常':
        comment = '对风偏差异常！'
        description = f'对风偏差角度{yaw_err_mean}'
    else:
        comment = ''
        description = ''

    # print('status', status)
    # print('comment', comment)
    # print('description', description)
    main_fig = '{}偏航对风整体图_{}-{}{}.jpg'.format(turbine_id,status,comment, uuid.uuid1())
    fig_m.savefig(main_fig, bbox_inches='tight')
    result = [turbine_id,yaw_err_mean,status, comment]
    results_all.append(result)

all_results = pd.DataFrame(results_all)
all_results.to_csv('2024_yaw_results.csv')
test = 1
#
# all_results.to_csv('yaw_results.csv')