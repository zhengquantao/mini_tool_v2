import pandas as pd
import random
from sklearn.preprocessing import MinMaxScaler
from models.utils.data_cleansing import *
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, make_scorer, mean_absolute_error, precision_score, recall_score, \
    f1_score, accuracy_score, roc_curve, auc
from math import sqrt
from models.utils.data_cleansing import *


def base_data_pro(filepath, feature_columns, target_columns):
    df = pd.read_csv(filepath)
    df = Data_cleansing(df, feature_columns + target_columns)
    X = df[feature_columns]
    y = df[target_columns]
    x_train, x_test, y_train, y_test = train_test_split(X, y)

    model = DecisionTreeRegressor()
    included = bidirectional_selection(model, x_train, y_train, cross_vi=5, )

    return included


def model_metrics(model, x, y, pos_label=1, flag=1):
    """
    评价函数
    Parameters
    ----------
    model 模型
    x 特征值
    y 目标值
    pos_label 标签
    flag 判断是分类还是回归

    Returns
    -------

    """
    yhat = model.predict(x)
    if flag == 1:
        yprob = model.predict_proba(x)[:, 1]
        fpr, tpr, _ = roc_curve(y, yprob, pos_label=pos_label)
        result = {'accuracy_score': accuracy_score(y, yhat),
                  'f1_score_macro': f1_score(y, yhat, average="macro"),
                  'precision': precision_score(y, yhat, average="macro"),
                  'recall': recall_score(y, yhat, average="macro"),
                  'auc': auc(fpr, tpr),
                  'ks': max(abs(tpr - fpr))
                  }
    elif flag == 0:
        result = {'mean_squared_error': mean_squared_error(y, yhat),
                  'mean_absolute_error': mean_absolute_error(y, yhat),
                  "root_mean_squared_error": sqrt(mean_squared_error(y, yhat))
                  }
    return result


def bidirectional_selection(model, x_train, y_train, cross_vi=10, flag=1, logger=None):
    """
    协变量筛选
    Parameters
    ----------
    model
    x_train
    y_train
    cross_vi 交叉验证次数

    Returns
    -------

    """

    # Dict = dict(zip(range(x_train.shape[1]), x_train.columns))

    DICT_col = []
    DICT_result = []

    min_max = MinMaxScaler()
    x_train = pd.DataFrame(min_max.fit_transform(x_train), columns=x_train.columns)
    # x_test = pd.DataFrame(min_max.fit_transform(x_test),columns=x_train.columns)

    excluded = list(set(x_train.columns))
    # random.shuffle(excluded)

    l = []

    for i in range(len(excluded)):
        res = []
        for col in excluded:
            if col not in l:
                model.fit(x_train[l + [col]], y_train)
                latest_metrics = sqrt(cross_val_score(model, x_train, y_train, scoring=make_scorer(mean_squared_error),
                                                      cv=cross_vi).mean())
                # latest_metrics = model_metrics(model, x_test[included+ l + [col]], y_test,flag=0)[metrics]
                res.append(latest_metrics)
                logger.info(f'{l + [col]} with metrics RMSE {latest_metrics:.3f}%')
                DICT_col.append(l + [col])
                DICT_result.append(latest_metrics)
        l.append(excluded[res.index(min(res))])
        excluded.remove(excluded[res.index(min(res))])

    logger.info(f"best columns combination {DICT_col[DICT_result.index(min(DICT_result))]}")

    return DICT_col[DICT_result.index(min(DICT_result))]


# def bidirectional_selection_classify(model, x_train, y_train, x_test, y_test, annealing=True, anneal_rate=0.2, iters=10,
#                             best_metrics=0,
#                             metrics='mean_squared_error', threshold_in=0.0001, threshold_out=0.0001, early_stop=True,
#                             verbose=True):
#     """
#     model  选择的模型
#     annealing     模拟退火算法
#     anneal_rate   退火概率，随迭代采纳概率衰减
#     threshold_in  特征入模的>阈值
#     threshold_out 特征剔除的<=阈值
#     """
#
#     included = []
#     best_metrics = best_metrics
#
#     for i in range(iters):
#         # forward step
#         print("iters", i)
#         changed = False
#         excluded = list(set(x_train.columns) - set(included))
#         random.shuffle(excluded)
#         for new_column in excluded:
#             model.fit(x_train[included + [new_column]], y_train)
#             latest_metrics = model_metrics(model, x_test[included + [new_column]], y_test)[metrics]
#             if latest_metrics - best_metrics > threshold_in:
#                 included.append(new_column)
#                 change = True
#                 if verbose:
#                     print('Add {} with metrics gain {:.6}'.format(new_column, latest_metrics - best_metrics))
#                 best_metrics = latest_metrics
#             elif annealing:
#                 if random.randint(0, i) / iters <= anneal_rate:
#                     included.append(new_column)
#                     if verbose:
#                         print('Annealing Add   {} with metrics gain {:.6}'.format(new_column,
#                                                                                   latest_metrics - best_metrics))
#
#         # backward step
#         random.shuffle(included)
#         for new_column in included:
#             included.remove(new_column)
#             model.fit(x_train[included], y_train)
#             latest_metrics = model_metrics(model, x_test[included], y_test)[metrics]
#             if latest_metrics - best_metrics <= threshold_out:
#                 included.append(new_column)
#             else:
#                 changed = True
#                 best_metrics = latest_metrics
#                 if verbose:
#                     print('Drop{} with metrics gain {:.6}'.format(new_column, latest_metrics - best_metrics))
#         if not changed and early_stop:
#             break
#     return included


if __name__ == "__main__":
    pass
    # data1 = pd.read_csv(r"H:\scy\文档\能效评估\data\t30000001.csv")
    # data1_ = data1[["grWindSpeed", "grWindDirction", "grOutdoorTemperature", "grAirDensity", "grGridActivePower"]]
    # data1_.fillna(1)
    # print(data1_.shape[0])
    # for i in data1_.columns:
    #     df = box_outlier(data1_, i, 1.5)
    #     df = three_sigma(data1_, i)
    #
    # df = df.drop(df[((df["grWindSpeed"] > 2.5) & (df["grGridActivePower"] == 0)) \
    #                 | (df["grWindSpeed"] > 11) & (df["grGridActivePower"] < 3600 * 0.9) \
    #                 | (df["grWindSpeed"] > 20) | (df["grGridActivePower"] < 0)].index)
    #
    # X = df[["grWindSpeed","grWindDirction","grOutdoorTemperature","grAirDensity"]]
    # y = df[["grGridActivePower"]]
    # x_train, x_test, y_train, y_test = train_test_split(X,y)
    #
    # model = DecisionTreeRegressor()
    # included = bidirectional_selection(model, x_train, y_train, cross_vi=5,)
