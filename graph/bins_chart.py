import os


from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/static/"

from pyecharts import options as opts
from pyecharts.charts import Scatter, Line
from common.common import random_name
from settings.settings import float_size


def build_html(data, col_x, col_y, xlabel, ylabel, title, file_path, bin_df,  hue=None, sizes=None, turbine_code=None,):
    """
    按照指定数据列绘制曲线图 【单台风机分仓曲线】
    包括散点图、曲线和偏差展示

    :param data: 时序数据集
    :param col_x: x数据列名
    :param col_y: y数据列名

    :param xlabel: x坐标名称
    :param ylabel: y坐标名称
    :param title: 图像标题

    :param file_path: 图像文件完整路径
    :param bin_df (dataframe): 分仓数据集

    :return:
    """

    # scatter = (
    #     Scatter()
    #     .add_xaxis(data[col_x].tolist())
    #     .add_yaxis(
    #         "scatter",
    #         data[col_y].tolist(),
    #         label_opts=opts.LabelOpts(is_show=False),
    #     )
    #     .set_global_opts(
    #         title_opts=opts.TitleOpts(title=title),
    #         xaxis_opts=opts.AxisOpts(
    #             name=xlabel,
    #             type_="value",
    #             splitline_opts=opts.SplitLineOpts(is_show=True),),
    #         yaxis_opts=opts.AxisOpts(
    #             name=ylabel,
    #             type_="value",
    #             splitline_opts=opts.SplitLineOpts(is_show=True)),
    #     )
    # )
    #
    # line = (
    #     Line()
    #     .add_xaxis(bin_df[col_x].tolist())
    #     .add_yaxis(
    #         "line",
    #         bin_df[col_y].tolist(),
    #         linestyle_opts=opts.LineStyleOpts(width=2),
    #         label_opts=opts.LabelOpts(is_show=False),
    #         is_symbol_show=False,
    #         z=10, z_level=10,
    #     )
    # )

    scatter = (
        Scatter(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(pos_right="right"),  # 将图例放在右边
            xaxis_opts=opts.AxisOpts(
                name=xlabel,
                type_="value",
                splitline_opts=opts.SplitLineOpts(is_show=True),),
            yaxis_opts=opts.AxisOpts(
                name=ylabel,
                type_="value",
                splitline_opts=opts.SplitLineOpts(is_show=True)),
        )
    )
    for size in sizes:
        size_data = data[data[hue] == size]
        add_scatter(scatter, size_data, size, col_x, col_y, color=None)
    line = (
        Line()
        .add_xaxis(bin_df[col_x].tolist())
        .add_yaxis(
            "line",
            bin_df[col_y].tolist(),
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=False,
            z=10, z_level=10,
        )
    )
    page = scatter.overlap(line)
    file_name = random_name(turbine_code, title)
    html_path = page.render(os.path.join(file_path, file_name))

    return html_path, file_name


def add_scatter(scatter, data, name, col_x, col_y, color=None):
    obj = Scatter().add_xaxis(data[col_x].tolist()).add_yaxis(str(name)[:5], data[col_y].tolist(),
                                                              color=color,
                                                              label_opts=opts.LabelOpts(is_show=False),
                                                              )
    scatter.overlap(obj)
