import os
import math
import numpy as np
import pandas as pd

from scipy.optimize import minimize


from common import loggers
from common.common import read_csv_file, detect_encoding, simple_data_cleaning
from settings.settings import power_theoretical, geolocation

# *** ---------- custom package ----------

from models.bin_analysis.quant.cloud.wind_base_tool import rule_removal, wind_speed_binning, windspeed_binning_proc
from models.bin_analysis.quant.cloud.wind_base_tool import wind_speed_label, power_label, gen_speed_label, \
    air_density_label

from models.bin_analysis.quant.cloud.pitch_analysis import pitch_label
from models.bin_analysis.quant.cloud.tsr_tool import tsr_calc, tsr_label

from models.bin_analysis.quant.cloud.bin_analysis_tool import dict_df_merge, dict_curve_plot
from models.bin_analysis.quant.cloud.bin_analysis_tool import bin_curve_analysis, month_bin_curve_analysis, \
    power_curve_bin


def bin_main(file_path, project_path, img_mode=False, run_func_list=None):
    """
    主程序执行
    :return:
    """
    factor_name = project_path.split(os.sep)[-1]
    turbine_code = file_path.split(os.sep)[-1].split(".")[0]

    # *** ---------- 1 基础设置和参数初始化 ----------
    if os.path.isfile(file_path):
        scada_files = [file_path]
    else:
        scada_files = [os.path.join(file_path, scada_file) for scada_file in os.listdir(file_path)]

    # 叶轮直径
    rotor_diameter = 104

    # 风轮半径：rotor radius
    rotor_radius = rotor_diameter / 2

    # 机组装机容量
    power_cap = None

    # 额定风速
    rated_wind_speed = None

    # 切入风速
    cut_in_wind_speed = 3

    # 切出风速
    cut_out_wind_speed = 20

    # 最小发电机转速：【并网转速】
    min_generator_speed = 1000

    # 传动比：gear ratio，transmission ratio，drive ratio
    gear_ratio = 131.58

    # *** ---------- 2 按SCADA文件进行分析处理 ----------
    # ? 曲线分仓分析数据词典
    res = []
    for scada_file in scada_files:

        if not scada_file.endswith(".csv"):
            continue

        if scada_file in [power_theoretical, geolocation]:
            continue

        # *** ---------- 3 数据提取 ----------
        # ** 3.1 CSV数据读取 **
        # SCADA数据文件夹
        # data = pd.read_csv(scada_file)  # , encoding="GB2312"
        data = read_csv_file(scada_file)
        # 初始化额定功率
        if not all([power_cap, rated_wind_speed]):

            power_theoretical_path = os.path.join(project_path, power_theoretical)
            power_theoretical_df = pd.read_csv(power_theoretical_path, encoding=detect_encoding(power_theoretical_path))
            max_row = power_theoretical_df["WINDS_POWER"].idxmax()
            row_data = power_theoretical_df.loc[max_row]
            power_cap, rated_wind_speed = row_data["WINDS_POWER"], row_data["WINDS_SPEED"]

        # data = simple_data_cleaning(data, power_cap)
        # 当前SCADA数据机组编号
        # turbine_code = data.loc[0, "风机"]

        # ** 3.2 运行模式数据提取 **
        # 提取正常运行的数据，并只提取相关标签，并限制风速、功率的标签为speed和power
        # ! "运行模式" == 20: 并网模式的数据
        # ? 没有运行模式数据
        # data = data[data["平均机组运行模式"] == 20].reset_index(drop=True)

        # ** 3.3 字段名称转换 **
        # data = data[["时间", "风机", "平均风速(m/s)", "平均发电机转速",
        #              "平均桨叶1角度", "平均桨叶2角度", "平均桨叶3角度",
        #              "平均风向（机舱）", "平均风角度（对北）", "平均空气密度", "平均机舱温度", "平均功率"]]
        # "power",
        # data.columns = ["real_time", "turbine_code", wind_speed_label, gen_speed_label,
        #                 pitch1_label, pitch2_label, pitch3_label,
        #                 "nacelle_direction", "wind_direction", air_density_label, "nacelle_temp", power_label]
        data.columns = ["turbine_code", wind_speed_label, gen_speed_label,
                        pitch_label, "nacelle_direction", "wind_direction", air_density_label, "nacelle_temp",
                        power_label]

        # # ** 3.4 数值类型转换 **
        # data.loc[:, "wind_speed"] = data.loc[:, "wind_speed"].astype("float")
        # data.loc[:, "wind_direction"] = data.loc[:, "wind_direction"].astype("float")
        #
        # data.loc[:, "air_density"] = data.loc[:, "air_density"].astype("float")
        # data.loc[:, pitch_label] = data.loc[:, pitch_label].astype("float")
        #
        # data.loc[:, "nacelle_temp"] = data.loc[:, "nacelle_temp"].apply(lambda x: locale.atof(str(x)))
        # # data.loc[:, "nacelle_temp"] = data.loc[:, "nacelle_temp"].astype("float")
        #
        # # data.loc[:, "power"] = data.loc[:, "power"].apply(lambda x: x.replace('"', ''))
        # # data.loc[:, "power"] = data.loc[:, "power"].apply(lambda x: x.replace('\'', ''))
        # # data.loc[:, "power"] = data.loc[:, "power"].apply(lambda x: locale.atof(x))
        # data.loc[:, "power"] = data.loc[:, "power"].apply(lambda x: x.replace(',', ''))
        # data.loc[:, "power"] = data.loc[:, "power"].astype("float")
        #
        # # data.loc[:, gen_speed_label] = data.loc[:, gen_speed_label].astype("float")
        # # data.loc[:, gen_speed_label] = data.loc[:, gen_speed_label].apply(lambda x: x.replace('"', ''))
        # # data.loc[:, gen_speed_label] = data.loc[:, gen_speed_label].apply(lambda x: x.replace('\'', ''))
        # # data.loc[:, gen_speed_label] = data.loc[:, gen_speed_label].apply(lambda x: locale.atof(x))
        #
        # data.loc[:, gen_speed_label] = data.loc[:, gen_speed_label].apply(lambda x: x.replace(',', ''))
        # data.loc[:, gen_speed_label] = data.loc[:, gen_speed_label].astype("float")
        #
        # #
        # data[power_label] = pd.to_numeric(data[power_label])
        # data[gen_speed_label] = pd.to_numeric(data[gen_speed_label])
        # data["nacelle_temp"] = pd.to_numeric(data["nacelle_temp"])

        # ** 3.5 空气密度分类：用于叶尖速比和空气密度关系分析 **
        air_density_list = data.loc[:, "air_density"].apply(lambda x: round(x, 4))
        data.insert(len(data.columns), "air_density_x", air_density_list)

        #
        loggers.logger.info("-------------------------------------------------------")
        loggers.logger.info("开始处理机组{}的数据".format(turbine_code))

        # *** ---------- 4 基于功率的数据清洗 ----------

        # ** 4.1 对数据进行分仓和异常值标注后的数据 **
        bin_norm_data, speed_list = windspeed_binning_proc(data, rated_wind_speed, power_cap)

        # ** 4.2 正常数据和异常数据标识 **
        # ! ["label"] == 0: 清洗过的正常数据
        # ! ["label"] == 1: 根据“风速-功率”筛选异常数据点
        # ! ["label"] == 2: 根据“箱线图”去除异常值
        # ! ["label"] == 3: 根据“3-Delta原则”标注异常数据点
        norm_data = bin_norm_data[bin_norm_data["label"] == 0]

        norm_data = norm_data[norm_data[gen_speed_label] > min_generator_speed]
        norm_data = norm_data[norm_data[wind_speed_label] > cut_in_wind_speed - 1.0]
        norm_data = norm_data[norm_data[wind_speed_label] <= cut_out_wind_speed]

        norm_data = norm_data[norm_data[wind_speed_label] <= cut_out_wind_speed]

        norm_data = norm_data[norm_data["nacelle_temp"] <= 100]
        norm_data = norm_data[norm_data["nacelle_temp"] >= -30]

        # *** ---------- 5 Violinplot变量分析 ----------
        '''
        month_label = 'month'
        norm_data['real_time'] = pd.to_datetime(norm_data['real_time'])
        norm_data[month_label] = norm_data.loc[:, "real_time"].apply(lambda x: "{}-{}".format(x.year, x.month))

        #
        turbine_desc = norm_data.describe()
        logger.info(turbine_desc)

        month_list = norm_data[month_label].unique().tolist()


        power_curve_bin(norm_data, turbine_code, bin_img_path)

        #
        vars_label = [power_label, wind_speed_label, air_density_label, pitch1_label, 
                      gen_speed_label, "nacelle_temp"]
        vars_legend = ['Power, kW', 'Wind speed, m/s', '空气密度/(Kg/m$^3$)', '变桨角度/(°)',
                       'Generator Speed/(r·min$^{-1}$)"', 'Nacelle temperature, °C']

        plot_heatmap(norm_data, vars_label, turbine_code, bin_img_path)

        draw_time_violinplot(norm_data, vars_label, vars_legend, time_label=month_label, 
                             time_tick_labels=month_list, turbine_code=turbine_code, 
                             file_path=bin_img_path, times_order=month_list, fig_size=(15, 10), orient="v")
        '''

        # *** ---------- 6 BIN曲线分仓绘图 ----------
        # ? 计算叶尖速比TSR
        if tsr_label not in norm_data.columns.to_list():
            tsr_calc(norm_data, gear_ratio, rotor_radius, True)

        # TODO: 不同的分仓绘图
        cp_factor = 0.5 * math.pi * pow(0.5 * float(rotor_diameter), 2) / 1000

        # ? 是否采用清洗的数据：norm_data
        # TODO: 根据不同的场景的进行选择
        # 是否清洗数据，对于诊断问题、曲线绘制、能效评估具有不同的意义
        # TODO: plot_flag=True 是否针对每个风机分仓曲线绘图 【单个风机】【分仓曲线】
        html_path, file_name = bin_curve_analysis(norm_data, turbine_code, air_density_tag=air_density_label,
                                                  dir_path=project_path, cp_factor=cp_factor,
                                                  plot_flag=img_mode, run_func_list=run_func_list)
        res.append((html_path, file_name))
        # ? 合并分仓分析数据词典
        # bin_dict = dict_df_merge(bin_dict, new_bin_dict, turbine_code)

        ''''''

        # *** ---------- 7 BIN曲线分仓趋势分析 ----------
        '''
        # ['2022-7' '2022-8' '2022-9' '2022-10' '2022-11' '2022-12' '2023-2'
        # '2023-3' '2023-4' '2023-5' '2022-6' '2023-1']
        # logger.info(norm_data[month_label].unique())

        target_data = norm_data[(norm_data[month_label] == '2022-7') | (norm_data[month_label] == '2023-2')]
        # target_data = norm_data[(norm_data[month_label] in ['2022-7', '2023-2'])]
        target_data = target_data.reset_index(drop=True)


        cp_factor = 0.5 * math.pi * pow(0.5 * float(rotor_diameter), 2) / 1000
        month_bin_curve_analysis(target_data, turbine_code, air_density_tag=air_density_label, 
                                 dir_path=bin_img_path, cp_factor= cp_factor)
        '''

        # *** ---------- 8 风速-功率密度分析 ----------
        '''
        # 提取月度数据
        m7_data = norm_data[norm_data[month_label] == '2022-7']
        m2_data = norm_data[norm_data[month_label] == '2023-2']

        h = sns.jointplot(data=m2_data, x=wind_speed_label, y=power_label, kind="hex")
        _ = h.set_axis_labels(wind_speed_label, power_label, fontsize=16)
        plt.show()

        sns.displot(data=m2_data, x=wind_speed_label, y=power_label, kind="kde",
                binwidth=(0.25, 50), cbar=True)
        plt.show()
        '''

        # *** ---------- 9 空气密度分析 ----------
        '''
        air_density_desc = m7_data[wind_speed_label].describe()
        logger.info(air_density_desc)

        #? 使用distfit寻找最佳的概率分布函数以及参数
        dfit = distfit() # distr='norm'
        dfit.fit_transform(m7_data[wind_speed_label].values)
        print(dfit.model)

        print(dfit.summary)
        dfit.plot_summary()
        plt.show()

        dfit.plot(chart='pdf')
        plt.show()


        #? 空气密度概率分布直方图展示
        #? https://medium.com/@raffaelwidmer/introduction-to-copula-using-python-8adec4d0cd76
        plt.figure()

        sns.histplot(m7_data[air_density_label].values)
        sns.histplot(m2_data[air_density_label].values)
        plt.show()


        fig, (ax1, ax2) = plt.subplots(1, 2)

        sns.histplot(m7_data[air_density_label].values, ax=ax1)
        sns.histplot(m2_data[air_density_label].values, ax=ax2)

        ax1.set_title("Histogram of 2022-7 Dataset")
        ax2.set_title("Histogram of 2023-2 Dataset")
        plt.show()
        '''

    # 曲线分仓binning分析结果展示【绘图】
    # ? 是否采用中文标注 【否则采用英文】 cn_label_flag
    # dict_curve_plot(bin_dict, bin_img_path, cn_label_flag=False)
    return res[0]

