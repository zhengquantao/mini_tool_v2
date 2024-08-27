import os
import numpy as np
import pandas as pd

from common.common import read_csv_file, ignore_files_func, common_cut
from graph.wind_flow_chart import build_html


def wind_flow_main(file_path, project_path, title):
    wind_flow_dict, str_code = wind_flow(file_path, project_path)
    full_path, file_name = build_html(wind_flow_dict, title, project_path, str_code,)
    return full_path, file_name


def wind_flow_main_export(file_path, project_path):
    wind_flow_list = []
    wind_flow_dict, str_code = wind_flow(file_path, project_path)
    for row in wind_flow_dict.values():
        wind_flow_list.append([row["turbine_code"], row["wind_mean"], row["wind_density"], row["terrain_mean_all"],
                               row["terrain_mean"], row["wind_max"]])
    return wind_flow_list


def wind_flow(file_path, project_path):

    if os.path.isfile(file_path):
        scada_files = [file_path]
        str_code = file_path.split(os.sep)[-1].split(".")[0]

    else:
        scada_files = [os.path.join(file_path, scada_file) for scada_file in os.listdir(file_path)]
        str_code = file_path.split(os.sep)[-1]

    turbine_dict = {}
    for scada_file in scada_files:

        if not scada_file.endswith(".csv"):
            continue

        if ignore_files_func(scada_file):
            continue

        turbine_code = scada_file.split(os.sep)[-1].split(".")[0]
        df = read_csv_file(scada_file)

        if df.empty:
            return turbine_dict, str_code

        df = df[~(df == df.shift()).all(axis=1)]

        wind_data = build_wind_data(df)

        df = df[['wind_speed']]

        wind_speed_bins = list(range(0, 25, 1))
        wind_label = [i + 0.5 for i in wind_speed_bins[:-1]]
        timestamp = int(df.index[1].timestamp()) - int(df.index[0].timestamp())
        if timestamp >= 10 * 60:
            df_resample = df.resample('1h').agg({'wind_speed': [np.mean, cal_complex_terrain]})
        else:
            df_resample = df.resample('10min').agg({'wind_speed': [np.mean, cal_complex_terrain]})
        df_resample.columns = ['wind_speed', 'terrain']

        df_resample['wind_label'] = pd.cut(df_resample['wind_speed'], bins=wind_speed_bins, labels=wind_label)
        terrain_line = df_resample.groupby(by='wind_label')['terrain'].quantile(0.90)
        terrain_line.index = terrain_line.index.astype(float)
        terrain_line = terrain_line.round(2)

        terrain_mean_all = terrain_line.mean().round(2)
        terrain_mean = terrain_line.loc[2.5:15].mean().round(2)

        terrain_line.dropna(inplace=True)
        turbine_dict[turbine_code] = {"wind_speed": terrain_line.index.tolist(), "wind_mean": wind_data["wind_mean"],
                                      "terrain": terrain_line.values.tolist(), "turbine_code": turbine_code,
                                      "terrain_mean": terrain_mean, "terrain_mean_all": terrain_mean_all,
                                      "wind_max": wind_data["wind_max"], "wind_density": wind_data["wind_density"]}

    return turbine_dict, str_code


def cal_complex_terrain(wind_speed_values):
    return wind_speed_values.std()/wind_speed_values.mean()


def build_wind_data(wind_df):

    wind_df["wind_speed2"] = wind_df.apply(lambda row: pow(row["wind_speed"], 3), axis=1)
    wind_df = common_cut(wind_df, "wind_speed", "wind_speed_bin", start=0, step=0.5)
    wind_df["wind_speed_bin"] = wind_df["wind_speed_bin"].astype('float').fillna(0)

    wind_speed_count = len(wind_df["wind_speed2"])
    grouped_mean = wind_df[wind_df["wind_speed_bin"] > 0].groupby("wind_speed_bin").agg(
        {"power": "mean", "wind_speed": "size", "air_density": "mean", "wind_speed2": "sum"})
    grouped_mean = grouped_mean.fillna(0)
    grouped_mean["wind_power_density"] = grouped_mean.apply(
        lambda row: row["air_density"] * row["wind_speed2"] / wind_speed_count / 2, axis=1)

    wind_mean, wind_max = wind_df["wind_speed"].mean().round(2), wind_df["wind_speed"].max().round(2)
    wind_density = grouped_mean["wind_power_density"].mean().round(2)
    ret_dict = {"wind_mean": wind_mean, "wind_max": wind_max, "wind_density": wind_density}
    return ret_dict
