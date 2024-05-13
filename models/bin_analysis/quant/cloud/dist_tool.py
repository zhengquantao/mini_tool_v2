#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------->
# 数据分布分析
# 功能描述：对SCADA数据进行变量概率密度分布分析
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
import os
import logging

import numpy as np
import pandas as pd

#
import warnings
warnings.filterwarnings("ignore")

#
import seaborn as sns

import matplotlib as mpl

from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from mpl_toolkits.mplot3d import Axes3D

#? 中文乱码问题
font = fm.FontProperties(fname='微软雅黑.ttf')
#? 字体设置：SimHei
plt.rcParams["font.sans-serif"]=["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"]=False
mpl.rcParams['legend.fontsize'] = 10

plt.rcParams.update(
    {
        # 'text.usetex': False,
        'mathtext.fontset': 'stix',
        'font.family': 'serif',
        "font.serif": ['Microsoft YaHei'],
    }
)

#
from models.bin_analysis.quant.cloud.file_dir_tool import get_full_path
from models.bin_analysis.quant.cloud.plot_tool import scatter_3d_plot

from models.bin_analysis.quant.cloud.wind_base_tool import wind_speed_label, power_label, gen_speed_label
from models.bin_analysis.quant.cloud.wind_base_tool import wind_direction_label, plot_save
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
# 分析处理
# ***
# --------------------------------------------------------------------

def joint_dist(dataset, turbine_code, power_cap, dir_path, plot_kind="kde"):
    """
    绘制风速与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param power_cap: 机组装机容量
    :param file_path: 图像文件完整路径
    
    :return:
    """

    '''
    # *** ---------- 1 distplot绘制概率密度分布 ----------
    #? 基于distplot绘制distribution图形
    sns.displot(data=norm_data, x=wind_speed_label, y=power_label, kind="kde",
                binwidth=(0.2, 10), cbar=True)
    plt.show()

    # *** ---------- 2 PairGrid绘制多图 ----------
    #? 基于PairGrid绘制变量之间的联合概率密度分析
    g = sns.PairGrid(norm_data, vars=[wind_speed_label, generator_speed_label, pitch1_label, power_label])
    g.map_upper(sns.histplot)
    g.map_lower(sns.kdeplot, fill=True)
    g.map_diag(sns.histplot, kde=True)
    plt.show()
    '''
    
    # *** ---------- 3 jointplot绘制bivariate distribution ----------
    #? 基于jointplot绘制双变量概率密度分布图形
    #! kind：{"scatter"| "reg"| "resid"| "kde"| "hex"
    #? 作用：指定要绘制的类型
    # ** 3.1 数据jointplot绘图 **
    # sns.set_style("darkgrid")
    h = sns.jointplot(x=wind_speed_label, y=power_label, data=dataset,
                      kind=plot_kind, xlim=(2, 20), ylim=(-200, power_cap*1.1),
                      stat_func=None, space=0,
                      joint_kws=dict(shade=True, alpha=0.5, color='r'),
                      marginal_kws=dict(shade=True, color='g'))
    # hue='air_density',
    h.set_axis_labels('风速/(m·s$^{-1}$)', '功率/(kW)', fontsize=12)
    plt.title("2-dimensional speed-power distribution")
    
    # ** 3.2 图形设置以及文件保存 **
    ''''''
    # plt.show()
    # 保存图片到文件
    file_name = "{}_joint_PDF.png".format(turbine_code)
    plot_save(dir_path, file_name)


def pcw_3d_dist(dataset, turbine_code, dir_path):
    """
    绘制风速与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """

    #? azim是绕z轴旋转的角度
    #? elev是绕y轴旋转的角度
    #? 默认值：azim=-60, elev=30
    figsize=(7, 5)
    fig = plt.figure(figsize=figsize)
    
    #! 存在两种方式绘制3D图形
    ax = Axes3D(fig, azim=120, elev=10) # azim=-60
    # ax = fig.gca(projection='3d')
    # ax.view_init(elev=10,azim=120)
    ax.scatter(dataset[wind_speed_label], dataset[pitch1_label], dataset[power_label], 
               c=dataset[power_label], cmap=cm.coolwarm)
    
    title = "3D Weed speed, pitch angle and power of %s" % (turbine_code)
    ax.set_title(title)
    ax.set_xlabel("风速/(m·s$^{-1}$)")
    ax.set_ylabel("桨距角$°$")
    ax.set_zlabel("功率/(kW)")
    # ax.legend() # loc="upper right"
    fig.add_axes(ax)
    
    # fig.legend(loc="upper right")
    plt.title(title)
    plt.tight_layout()

    # plt.show()
    file_name = "{}_3d.png".format(turbine_code)
    plot_save(dir_path, file_name)


def pcw_direction_3d_plot(dataset, turbine_code, dir_path):
    """
    绘制考虑风向的功率曲线
    #? 参考power_curve_tool.py文件的power_curve_direction_3d_plot函数
    #? 差异：本函数是基于数据的直接展示，power_curve_direction_3d_plot函数
    #? 重点对比实际风机出力和功率曲线建模的差异对比
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """
    
    vars_list = [wind_speed_label, wind_direction_label, power_label]

    xlabel = "风速/(m·s$^{-1}$)"
    ylabel = "风向/($°$)"
    zlabel = "功率/(kW)"
    title = "风速-风向-功率3D分析"

    file_name = "dir_3d_{}.png".format(turbine_code)
    file_path = get_full_path(dir_path, file_name)

    # 基于通用3D绘制函数，描述风速-风向-功率的三维关系【vars_list】
    scatter_3d_plot(dataset, vars_list, file_path, xlabel, ylabel, zlabel, title, 
                    color_label=wind_direction_label)



def binning_dist(dataset, turbine_code, dir_path):
    """
    绘制风速与桨距角关系 图像
    
    :param dataset: 时序数据集
    :param turbine_code: 机组编码
    :param file_path: 图像文件完整路径
    
    :return:
    """

    bin_data = pd.DataFrame(dataset[[wind_speed_label, power_label]]).reset_index(drop=True)

    # *** ---------- 1 wind speed分仓 ----------
    wind_speed_bins = np.arange(0, np.ceil(bin_data[wind_speed_label].max()), 0.125)
    # wind_speed_labels = ['-'.join(map(str,(x,y))) for x, y in zip(wind_speed_bins[:-1], wind_speed_bins[1:])]
    wind_speed_labels = [x for x in wind_speed_bins[1:]]

    bin_data['speed_bins'] = pd.cut(bin_data[wind_speed_label], bins=wind_speed_bins, 
                                          labels=wind_speed_labels)

    # *** ---------- 2 power分仓 ----------
    power_bins = np.arange(0, np.ceil(bin_data[power_label].max()/100.0)*100, 20)
    power_labels = [x for x in power_bins[1:]]

    bin_data['power_bins'] = pd.cut(bin_data[power_label], bins=power_bins, labels=power_labels)

    # *** ---------- 3 分仓统计频次 ----------
    bin_data.dropna(inplace=True)
    bin_data.insert(0, 'count', 1)
    dist_data = bin_data.groupby(['speed_bins','power_bins'])[['count']].count().reset_index()
    # dist_data.to_csv(os.path.join(dir_path, "{}_dist.csv".format(turbine_code)))


    #! 存在大部分数值为零，分仓采样数据频次集中，分割不明显的情况
    # point_num = bin_data['count'].sum()
    # dist_data['count'] = dist_data['count'] * 100 / point_num 
    # dist_data['count'] = dist_data['count'] + 2
    # dist_data['count'] = dist_data['count'].apply(np.log) 

    # turbine_desc = dist_data.describe()
    # logger.info(turbine_desc)

    # *** ---------- 4 3D图形展示 ----------
    fig = plt.figure()
    
    #! 存在两种方式绘制3D图形
    ax = Axes3D(fig, azim=-50, elev=40)
    # ax = fig.gca(projection='3d')
    # ax.view_init(elev=10,azim=120)
    # ax.scatter(dist_data['speed_bins'], dist_data['power_bins'], dist_data['count'], 
    #           cmap=cm.coolwarm)


    # ** 4.1 数据plot_surface绘图 **
    x_list, y_list = np.meshgrid(wind_speed_bins[1:], power_bins[1:])
    count_index = list(dist_data.columns).index('count')

    def fun_dist(x, y):
        xy = [[d1, d2] for d1, d2 in zip(x.ravel(), y.ravel())]
        z_2d_list = np.array([0] * len(xy))
        
        x_len = len(x[0])
        y_len = len(y[:, 0])
        for y_index in range(y_len):
            for x_index in range(x_len):
                j = y[y_index, 0]
                i = x[0, x_index]

                target_point = dist_data[(dist_data['speed_bins']==i) & (dist_data['power_bins']==j)]
                
                if target_point is not None:
                    z_2d_list[x_index + y_index* x_len] = target_point.iloc[0, count_index]
                else:
                    z_2d_list[x_index + y_index* x_len] = 0
        
        return z_2d_list.reshape(y_len, x_len)
    
    ax.plot_surface(x_list, y_list, fun_dist(x_list, y_list), 
                    cmap=cm.coolwarm, linewidth=2, alpha=0.5, antialiased=False)
    
    # ** 4.2 数据bar3d绘图 **
    '''
    width = 0.125
    height = 20
    bottom = np.zeros_like(x_list.ravel())
    z_2d_list = fun_dist(x_list, y_list)
    ax.bar3d(x_list.ravel(), y_list.ravel(), bottom, width, height, z_2d_list.ravel(), 
             shade=True, cmap=cm.coolwarm, alpha=0.2)
    
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 2000*1.1)
    # ax.set_zlim(0.0, 0.0030)
    '''


    # ** 4.3 图形设置以及文件保存 **
    title = "3D Weed speed, pitch angle and power of %s" % (turbine_code)
    ax.set_title(title)
    ax.set_xlabel("风速/(m·s$^{-1}$)")
    ax.set_ylabel("功率/(kW)")
    ax.set_zlabel("PDF")

    # ax.legend() # loc="upper right"
    # fig.legend(loc="upper right")
    fig.add_axes(ax)
    
    plt.title(title)
    plt.tight_layout()
    
    # plt.show()
    file_name = "dist_{}_bin.png".format(turbine_code)
    plot_save(dir_path, file_name)


