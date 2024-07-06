'''
coding:utf-8
@Software:PyCharm
@Time:2023/8/28 14:32
@Author: Natsu
'''

import numpy as np
import pandas as pd
import scipy.stats as stats
from sklearn.neighbors import KernelDensity


def fit_plot_line(x=[], y=[], ci=95):
    import seaborn as sns
    import matplotlib.pyplot as plt
    alpha = 1 - ci / 100
    n = len(x)

    Sxx = np.sum(x ** 2) - np.sum(x) ** 2 / n
    Sxy = np.sum(x * y) - np.sum(x) * np.sum(y) / n
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    # Linefit
    b = Sxy / Sxx
    a = mean_y - b * mean_x

    # Residuals
    def fit(xx):
        return a + b * xx

    residuals = y - fit(x)

    var_res = np.sum(residuals ** 2) / (n - 2)
    sd_res = np.sqrt(var_res)

    # Confidence intervals
    se_b = sd_res / np.sqrt(Sxx)
    se_a = sd_res * np.sqrt(np.sum(x ** 2) / (n * Sxx))

    df = n - 2  # degrees of freedom
    tval = stats.t.isf(alpha / 2., df)  # appropriate t value

    ci_a = a + tval * se_a * np.array([-1, 1])
    ci_b = b + tval * se_b * np.array([-1, 1])

    # create series of new test x-values to predict for
    npts = 100
    px = np.linspace(np.min(x), np.max(x), num=npts)

    def se_fit(x):
        return sd_res * np.sqrt(1. / n + (x - mean_x) ** 2 / Sxx)

    # Plot the data
    plt.figure()

    plt.plot(px, fit(px), 'k', label='Regression line')
    plt.plot(x, y, 'k.')

    x.sort()
    limit = (1 - alpha) * 100
    plt.plot(x, fit(x) + tval * se_fit(x), 'r--', lw=2,
             label='Confidence limit ({0:.1f}%)'.format(limit))
    plt.plot(x, fit(x) - tval * se_fit(x), 'r--', lw=2)

    plt.xlabel('X values')
    plt.ylabel('Y values')
    plt.title('Linear regression and confidence limits')
    plt.legend(loc='best')
    plt.show()


def plot_violinplot(data,label,title,num,index):
    """
    小提琴图
    Parameters
    ----------
    data
    label
    title
    num
    index

    Returns
    -------

    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    # data = data[data[label]<=30]
    data["real_time"] = pd.to_datetime(data["real_time"])
    data["月份"] = data["real_time"].dt.month
    plt.subplot(num, 1, index)
    sns.violinplot(x="月份",y=label,data=data)
    plt.xlabel("月份")
    plt.ylabel(label)
    # plt.yticks(range(0,30,5))
    plt.title(title)


def plot_distplot(x, title_name,num):
    """
    绘制概率密度图
    Parameters
    ----------
    x
    y2
    title_name
    num

    Returns
    -------

    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.histplot(x, bins=40, alpha=0.5, label=title_name, color=sns.color_palette()[num], )
    # plt.title(title_name)


def plot_curve_line(x, y2, title_name, num):
    """
    绘制功率曲线
    Parameters
    ----------
    x
    y2
    title_name
    num

    Returns
    -------

    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    sns.lineplot(x=sorted(x), y=sorted(y2), linewidth=2.0,
                 # ax=ax2,
                 label=title_name, color=sns.color_palette()[num],  ####5
                 )
    plt.xticks(range(0, 21))
    plt.xlabel("风速")
    plt.ylabel("功率")
    plt.title("功率曲线")


def plot_power_distplot(x, y2, title_name, num):
    """
    概率密度图和功率曲线图
    Parameters
    ----------
    x
    y2
    title_name
    num

    Returns
    -------

    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()

    ax2 = ax.twinx()

    sns.histplot(x, bins=40, alpha=0.5, label="概率密度", color=sns.color_palette()[1],
                 ax=ax
                 )



    # sns.distplot(x=x,color=sns.color_palette('dark')[1],
    #              ax=ax,
    #              label="概率密度图"
    #              )

    sns.lineplot(x=sorted(x), y=sorted(y2), linewidth=2.0,
                 ax=ax2,
                 label="功率曲线", color=sns.color_palette()[0],  ####5
                 )

    plt.xticks(range(0, 21))
    plt.title(title_name + '号风机')
    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(handles1 + handles2, labels1 + labels2, loc=7)

    plt.tight_layout()

    plt.savefig("./img/" + title_name + ".png")
    plt.close()
    # plt.show()


def plot_confidence_interval(x, y, y2, data, lower_bound, upper_bound, use_column, target_column, plot_name):
    import seaborn as sns
    import matplotlib.pyplot as plt
    # 绘制函数曲线和置信区间
    if plot_name is not None:
        plt.title(plot_name)

    plt.scatter(x, y, label='异常点', color = "#FFB48D",alpha=0.5)
    plt.plot(sorted(x), sorted(y2), label='功率曲线', color="r",linewidth=3.0)
    # plt.plot(sorted(x + 2), sorted(lower_bound), label='lower_bound', color="red", linestyle="--")
    # plt.plot(sorted(x - 2), sorted(upper_bound), label='upper_bound', color="green", linestyle="--")
    plt.scatter(data[use_column[0]], data[target_column], label='清洗后的点',  color="#7FBEC2",alpha=0.5)
    # plt.legend()
    # plt.show()







def nrd0(x):
    return 0.9 * min(np.std(x, ddof=1), (np.percentile(x, 75) - np.percentile(x, 25)) / 1.349) * len(x) ** (-0.2)


def approx_kde(X):
    var_range = np.linspace(min(X), max(X), 512).reshape(-1, 1)
    kde = KernelDensity(kernel='gaussian', bandwidth=nrd0(X)
                        ).fit(X.reshape(-1, 1))
    var_density = np.exp(kde.score_samples(var_range))

    return var_range, var_density


def Covmath_plot(matched, data1, data2, name, base_turbine):
    """

    Parameters
    ----------
    matched
    data1
    data2

    Returns
    -------

    """
    import seaborn as sns
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(14, 14))
    fig.subplots_adjust(hspace=0.3, wspace=0.3)
    ax = fig.add_subplot(3, 2, 1)
    ax.set_title('Before Matching', fontsize=16)
    X, y = approx_kde(data1[:, 0])
    ax.plot(X, y, color='black')
    X, y = approx_kde(data2[:, 0])
    ax.plot(X, y, color='red', linestyle='--')
    ax.set_xlim([0, 18])
    ax.set_ylim([0, 0.23])
    ax.set_xlabel('Wind Speed (m/s)', fontsize=14)
    ax = fig.add_subplot(3, 2, 2)
    ax.set_title('After Matching', fontsize=16)
    X, y = approx_kde(matched.matched_data_X[0][:, 0])
    ax.plot(X, y, color='black')
    X, y = approx_kde(matched.matched_data_X[1][:, 0])
    ax.plot(X, y, color='red', linestyle='--')
    ax.set_xlim([0, 18])
    ax.set_ylim([0, 0.23])
    ax.set_xlabel('Wind Speed (m/s)', fontsize=14)

    ax = fig.add_subplot(3, 2, 3)
    ax.set_title('Before Matching', fontsize=16)
    X, y = approx_kde(data1[:, 1])
    ax.plot(X, y, color='black')
    X, y = approx_kde(data2[:, 1])
    ax.plot(X, y, color='red', linestyle='--')
    ax.set_xlim([-30, 30])
    ax.set_ylim([0, 0.2])
    ax.set_xlabel('WindDirction ({}C)'.format(
        u'\N{DEGREE SIGN}'), fontsize=14)
    ax = fig.add_subplot(3, 2, 4)
    ax.set_title('After Matching', fontsize=16)
    X, y = approx_kde(matched.matched_data_X[0][:, 1])
    ax.plot(X, y, color='black')
    X, y = approx_kde(matched.matched_data_X[1][:, 1])
    ax.plot(X, y, color='red', linestyle='--')
    ax.set_xlim([-30, 30])
    ax.set_ylim([0, 0.2])
    ax.set_xlabel('WindDirction ({}C)'.format(
        u'\N{DEGREE SIGN}'), fontsize=14)

    # ax = fig.add_subplot(3, 2, 5)
    # ax.set_title('Before Matching', fontsize=16)
    # X, y = approx_kde(data1[:, 2])
    # ax.plot(X, y, color='black')
    # X, y = approx_kde(data2[:, 2])
    # ax.plot(X, y, color='red', linestyle='--')
    # ax.set_xlim([-30, 40])
    # ax.set_ylim([0, 0.1])
    # ax.set_xlabel('Temperature', fontsize=14)
    # ax = fig.add_subplot(3, 2, 6)
    # ax.set_title('After Matching', fontsize=16)
    # X, y = approx_kde(matched.matched_data_X[0][:, 2])
    # ax.plot(X, y, color='black')
    # X, y = approx_kde(matched.matched_data_X[1][:, 2])
    # ax.plot(X, y, color='red', linestyle='--')
    # ax.set_xlim([-30, 40])
    # ax.set_ylim([0, 0.1])
    # ax.set_xlabel('Temperature', fontsize=14)
    l = []
    l.append(f"turbine {str(int(base_turbine))}")
    l.append(f"turbine {str(int(name))}")
    fig.legend(l, ncol=2, fontsize=14)
    plt.show()
    # fig.savefig('figure24_22.pdf')


if __name__ == "__main__":
    # # generate data
    # mean, cov = [4, 6], [(1.5, .7), (.7, 1)]
    # x, y = np.random.multivariate_normal(mean, cov, 80).T
    #
    # # fit line and plot figure
    # fit_plot_line(x=x, y=y, ci=95)
    pass





