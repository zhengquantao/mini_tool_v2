import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from sklearn.cluster import DBSCAN

from common.common import read_csv_file, ignore_files_func, common_cut
from graph.yaw_chart import build_html


# 标签名
pitch_angle_label = 'pitch_angle'

power_label = 'power'
power_bin_label = 'power_bin'
wind_direction_label = 'wind_direction'
wind_direction_bin_label = 'wind_direction_bin'
nacell_direction_label = 'nacelle_direction'
wind_speed_label = 'wind_speed'
gen_speed_label = 'generator_speed'

START_POWER = 100
MAX_POWER = 2200
STEP_POWER = 400


def yaw_main(file_path, project_path, title):
    yaw_turbine_lists, results_all, str_code = yaw(file_path, project_path)
    full_path, file_name = build_html(yaw_turbine_lists, title, project_path, str_code, yaw_list=results_all)
    return full_path, file_name


def yaw_main_export(file_path, project_path, title):
    ret_yaw_dict = {}
    yaw_turbine_lists, results_all, str_code = yaw(file_path, project_path)
    for yaw_turbine in yaw_turbine_lists:
        full_path, file_name = build_html([yaw_turbine], title, project_path, yaw_turbine["turbine_code"])
        ret_yaw_dict[yaw_turbine["turbine_code"]] = full_path

    return results_all, ret_yaw_dict


def yaw(file_path, project_path):
    if os.path.isfile(file_path):
        scada_files = [file_path]
        str_code = file_path.split(os.sep)[-1].split(".")[0]

    else:
        scada_files = [os.path.join(file_path, scada_file) for scada_file in os.listdir(file_path)]
        str_code = file_path.split(os.sep)[-1]

    yaw_turbine_lists = []
    results_all = []
    scaler = MinMaxScaler()

    for scada_file in scada_files:

        if not scada_file.endswith(".csv"):
            continue

        if ignore_files_func(scada_file):
            continue

        turbine_code = scada_file.split(os.sep)[-1].split(".")[0]
        df = read_csv_file(scada_file)

        # 选择非偏航工况
        df = df.loc[df[pitch_angle_label] < 10, :]
        df = df.loc[df[power_label] > 100, :].reset_index(drop=True)

        if df[nacell_direction_label].min() > 0 and df[wind_direction_label].min() > 0:
            df[wind_direction_label] = df[wind_direction_label] - df[nacell_direction_label]

        elif df[nacell_direction_label].min() < 0 and df[wind_direction_label].min() > 0:
            df[wind_direction_label] = df[nacell_direction_label]

        power_bins = list(range(START_POWER, MAX_POWER, STEP_POWER))
        power_labels = [200 + i for i in power_bins][:-1]
        df[power_bin_label] = pd.cut(df[power_label], bins=power_bins, labels=power_labels)

        yaw_turbine_dict = {"yaw_turbine_list": [], "turbine_code": turbine_code}

        yaw_err_dic = {}
        eps_id = 0.05
        sample_id = 20

        for power_i in power_labels:

            item_dict = {"power": power_i}
            df_p = df[df[power_bin_label] == power_i]

            if len(df_p) < 400:
                print(f'功率{power_i}单个功率区间数据量太少！')
                continue
            df_p = df_p[df_p[wind_speed_label] < df_p[wind_speed_label].mode()[0]]  # 为什么这么处理
            df_c = df_p[[wind_direction_label, wind_speed_label, power_label]]

            df_c.dropna(inplace=True)
            if len(df_p) < 50:
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
                df_c0 = df_c[df_c['cluster'] != -1]

            df_c0 = df_c0[df_c0[wind_direction_label].abs() < 40]
            if len(df_c0) < 20:
                continue

            dir_bins = np.arange(min(df_c0[wind_direction_label])-1, max(df_c0[wind_direction_label])+1, 1)
            dirs = [i + 0.5 for i in dir_bins][:-1]
            df_c0[wind_direction_bin_label] = pd.cut(df_c0[wind_direction_label], bins=dir_bins, labels=dirs)
            dir_power_i = df_c0.groupby(by=wind_direction_bin_label)[wind_speed_label].min()

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

            # 散点
            item_dict["scatter_x"] = df_c0[wind_direction_label]
            item_dict["scatter_y"] = df_c0[wind_speed_label]
            # 虚线
            item_dict["split_line"] = (0, 0)

            if valid_flag:
                # 曲线
                item_dict["line_y"] = y_pre
                item_dict["line_x"] = y_pre.index
                # 最低点
                item_dict["min_point"] = [yaw_err_i, min_wind_i]
                yaw_err_dic[power_i] = yaw_err_i

            yaw_turbine_dict["yaw_turbine_list"].append(item_dict)

        build_yam_mean(yaw_err_dic, yaw_turbine_dict, turbine_code, results_all)

        yaw_turbine_lists.append(yaw_turbine_dict)

    return yaw_turbine_lists, results_all, str_code


def build_yam_mean(yaw_err_dic, yaw_turbine_dict, turbine_code, results_all):
    yaw_err_s = pd.Series(yaw_err_dic)
    yaw_err_mean = np.round(yaw_err_s.mean(), 1)
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
        comment = '对风偏差异常!留意风向仪对0偏差'
        description = f'对风偏差角度{yaw_err_mean}'
    else:
        comment = ''
        description = ''
    yaw_turbine_dict["yaw_err_mean"] = yaw_err_mean
    yaw_turbine_dict["yaw_err_status"] = status
    yaw_turbine_dict["yaw_err_comment"] = comment
    results_all.append([turbine_code, yaw_err_mean, status, comment])