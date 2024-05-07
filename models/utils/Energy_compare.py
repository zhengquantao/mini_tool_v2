'''
coding:utf-8
@Software:PyCharm
@Time:2023/8/25 11:38
@Author: Natsu
'''

from dswe import ComparePCurve, CovMatch
from pandas import DataFrame, concat, read_csv
import os
from utils.data_cleansing import *
import matplotlib.pyplot as plt
from matplotlib import rcParams
from utils.plot_utils import *

rcParams['font.family'] = 'Microsoft YaHei'
import seaborn as sns


def base_data_process(file_path, base_turbine, result_path, flag,
                      feature_columns: list, target_columns: list,
                      wind_col: list, confidence: float = 0.8, logger=None, farm_name=""):
    """
    前序处理数据
    Parameters
    ----------
    file_path 文件存放路径
    base_turbine 标杆风机
    result_path 结果存放路径
    flag 标志位   1为直接获取对比结果，0为获取匹配数据
    feature_columns 特征值列表
    target_columns 目标值列表

    Returns
    -------

    """
    ## 读取标杆风机数据
    filelist = os.listdir(file_path)
    data_result = DataFrame(
        columns=["turbine_code", "Weighted diff", "Weighted stat diff", "Scaled diff", "Scaled stat diff",
                 "Unweighted diff", "Unweighted stat diff"])
    if ".csv" in base_turbine:
        name = base_turbine
    else:
        name = base_turbine + '.csv'

    filelist.remove(name)
    df1 = read_csv(os.path.join(file_path, name)).fillna(1)
    df1 = df1.loc[:, feature_columns + target_columns].astype(float)
    # df1 = Data_cleansing(df1,feature_columns+target_columns, )

    ## 数据清洗
    df1, clean_percentage = confidence_interval(df1, confidence, wind_col, target_columns, name, logger=logger)

    ## 读取其他风机并进行清洗
    ##      这里是两部，一步可以用来获取对比结果， 一步可以用来获取匹配的数据
    try:
        if flag == 1:

            data_result = cycle_compare(df1, filelist, file_path, data_result, feature_columns, target_columns,
                                        logger=logger, flag_cycle=0,
                                        Confidence=confidence, Wind_col=wind_col, result_path=result_path,
                                        farm_name=farm_name)

        elif flag == 0:
            get_math_data(df1, filelist, file_path, result_path, feature_columns, target_columns, base_turbine,
                          logger=logger,
                          Confidence=confidence, Wind_col=wind_col, farm_name=farm_name)

        else:
            data_result = cycle_compare(df1, filelist, file_path, data_result, feature_columns, target_columns,
                                        logger=logger,
                                        flag_cycle=0, Confidence=confidence, Wind_col=wind_col, result_path=result_path,
                                        farm_name=farm_name)
            get_math_data(df1, filelist, file_path, result_path, feature_columns, target_columns, base_turbine,
                          logger=logger,
                          Confidence=confidence, Wind_col=wind_col, farm_name=farm_name)


    except Exception as e:
        logger.error(e)
    return data_result


def cycle_compare(df1: DataFrame, filelist: list, file_path, data_result: DataFrame, feature_columns: list,
                  target_columns: list, flag_cycle=0, logger=None,
                  Confidence=0.9, Wind_col: list = [], result_path='', farm_name=""):
    """
    循环对比
    Parameters
    ----------
    df1 风机1的数据
    df2 风机2的数据
    i 文件名
    data_result 存放结果

    Returns
    -------
    """

    ## 这里就是DSWE算法的步骤，
    colum = []
    logger.info("start")

    for i in filelist:
        if ".csv" in i:
            logger.info(i)
            df2 = read_csv(os.path.join(file_path, i)).fillna(1)
            df2 = df2.loc[:, feature_columns + target_columns].astype(float)
            # df2 = Data_cleansing(df2, feature_columns+target_columns)
            df2, clean_percentage = confidence_interval(df2, Confidence, Wind_col, target_columns, i, logger=logger)

            ### 这里可以循环使用不同的特征计算结果
            if flag_cycle == 1:

                for k in range(df2.shape[1] - 1):
                    colum.append(df2.columns[k])
                    # num = min(df1.shape[0],df2.shape[0])
                    logger.info(colum)
                    # 合并标杆风机和对比风机的数据
                    Xlist = [df1.iloc[:, colum].to_numpy(), df2.iloc[:, colum].to_numpy()]
                    ylist = [df1.loc[:, target_columns].to_numpy(), df2.loc[:, target_columns].to_numpy()]

                    if len(colum) == 1:
                        testcol = [0]
                    else:
                        testcol = [0, 1]

                    ##数据比较
                    cpc = ComparePCurve(Xlist, ylist, testcol)

                    ## 保存结果
                    data_result.loc[len(data_result)] = [i.split(".")[0], cpc.weighted_diff, cpc.weighted_stat_diff,
                                                         cpc.scaled_diff, cpc.scaled_stat_diff, cpc.unweighted_diff,
                                                         cpc.unweighted_stat_diff]

                    logger.info('end')
            else:

                ##这里是使用规定的特征（默认）
                Xlist = [df1.loc[:, feature_columns].to_numpy(), df2.loc[:, feature_columns].to_numpy()]
                ylist = [df1.loc[:, target_columns].to_numpy(), df2.loc[:, target_columns].to_numpy()]
                if len(colum) == 1:
                    testcol = [0]
                else:
                    testcol = [0, 1]

                cpc = ComparePCurve(Xlist, ylist, testcol)
                data_result.loc[len(data_result)] = [i.split(".")[0], cpc.weighted_diff, cpc.weighted_stat_diff,
                                                     cpc.scaled_diff, cpc.scaled_stat_diff, cpc.unweighted_diff,
                                                     cpc.unweighted_stat_diff]

                logger.info('end')
    data_result.index = data_result["turbine_code"].apply(lambda x: int(x[-3:]))
    data_result.to_excel(os.path.join(result_path, farm_name + "_compareCurve.xlsx"))
    return data_result


def get_math_data(df1: DataFrame, filelist: list, file_path, result_path,
                  feature_columns: list, target_columns: list, base_turbine,
                  logger, Confidence, Wind_col, farm_name):
    """
    ## 风机能效对比-获取匹配数据
    Parameters
    ----------
    df1 风机1的数据
    df2 风机2的数据
    i 文件名
    result_path 结果存放路径
    feature_columns 特征值列表
    target_columns 目标值列表
    Returns
    -------

    """

    for i in filelist:
        if ".csv" in i:
            logger.info(i)
            df2 = read_csv(os.path.join(file_path, i)).fillna(1)
            df2 = df2.loc[:, feature_columns + target_columns].astype(float)
            # df2 = Data_cleansing(df2, feature_columns+target_columns)
            df2, clean_percentage = confidence_interval(df2, Confidence, Wind_col, target_columns, i, logger=logger)

            ## 获取匹配的文件
            Xlist = [df1.loc[:, feature_columns].to_numpy(), df2.loc[:, feature_columns].to_numpy()]
            ylist = [df1.loc[:, target_columns].to_numpy(), df2.loc[:, target_columns].to_numpy()]

            ## 进行匹配
            cpc = CovMatch(Xlist, ylist)

            ## 提取匹配的数据
            data1x = DataFrame(cpc.matched_data_X[0])
            data1x.columns = feature_columns
            data2x = DataFrame(cpc.matched_data_X[1])
            data2x.columns = feature_columns
            data1y = DataFrame(cpc.matched_data_y[0])
            data1y.columns = target_columns
            data2y = DataFrame(cpc.matched_data_y[1])
            data2y.columns = target_columns

            datae1x = concat([data1x, data1y], axis=1)
            if os.path.exists(os.path.join(result_path, farm_name)):
                result_path = os.path.join(result_path, farm_name)
            else:
                os.mkdir(os.path.join(result_path, farm_name))
            datae1x.to_csv(os.path.join(result_path,
                                        "turbine{}match{}-{}.csv".format(base_turbine[-7:-4], str(i[-7:-4]),
                                                                         base_turbine[-7:-4])), index=False)

            datae2x = concat([data2x, data2y], axis=1)
            datae2x.to_csv(os.path.join(result_path,
                                        "turbine{}match{}-{}.csv".format(base_turbine[-7:-4], str(i[-7:-4]),
                                                                         str(i[-7:-4]))), index=False)

            # 匹配数据对比可视化
            Covmath_plot(cpc, df1.to_numpy(), df2.to_numpy(), i.split(".csv")[0][-3:], base_turbine[-7:-4])

            ## matplotlib版本
            # fig, axes = plt.subplots(len(feature_columns)+len(target_columns), 2, figsize=(10, 10), dpi=100)
            #
            # for i, row in enumerate(axes):
            #     axes[i, 0].scatter(datae1x[datae1x.columns[i]], datae1x[datae1x.columns[-1]], c="r")
            #     axes[i, 1].scatter(datae2x[datae2x.columns[i]], datae2x[datae2x.columns[-1]], c="b")
            #     axes[i, 0].set_title(f"1x{datae1x.columns[i]} and power scatter", fontsize=10)
            #     axes[i, 1].set_title(f"2x{datae1x.columns[i]} and power scatter", fontsize=10)
            #
            # plt.tight_layout()
            # plt.show()

            ##seaborn

            # 查看数据中功率的最大值、数据量
            logger.info(datae1x[datae1x.columns[-1]].max())
            logger.info(datae2x[datae2x.columns[-1]].max())
            logger.info(len(datae1x))
            logger.info(len(datae2x))
