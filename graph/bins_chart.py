import os


from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Scatter, Line
from common.common import random_name, create_dir
from settings.settings import float_size


def build_html(data, col_x, col_y, xlabel, ylabel, title, file_path, bin_df,  hue=None, sizes=None, turbine_code=None,
               beside_title="", line_name=""):
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
    :param turbine_code: 风机编号
    :param beside_title: 侧边标题
    :param line_name: 线名字

    :return:
    """
    colors = ["#EBDEF0", "#D7BDE2", "#C39BD3", "#AF7AC5", "#9B59B6", "#884EA0", "#76448A"]
    colors_size = len(colors)
    scatter = (
        Scatter(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(pos_right="right", pos_top="50%", border_width=0),  # 将图例放在右边
            xaxis_opts=opts.AxisOpts(
                name=xlabel,
                # type_="value",
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            yaxis_opts=opts.AxisOpts(
                name=ylabel,
                type_="value",
                splitline_opts=opts.SplitLineOpts(is_show=True)),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                orient="vertical",  # 工具栏 icon 的布局朝向
                pos_left="right"  # 工具栏组件离容器左侧的距离
            ),
            # # 区域缩放
            # datazoom_opts=opts.DataZoomOpts(
            #     is_show=True,  # 是否显示 组件。如果设置为 false，不会显示，但是数据过滤的功能还存在
            #     type_="slider",  # 组件类型，可选 "slider", "inside"
            #     orient="horizontal",  # 可选值为：'horizontal', 'vertical'
            #     range_start=0,  # 显示区域开始
            #     range_end=100,  # 显示区域结束
            # ),


            # 自定义文本框
            # https://github.com/reed-hong/pyecharts/blob/5f01f2fb43d1602a46d77234721450008cbff7eb/example/graphic_example.py#L10
            graphic_opts=[
                opts.GraphicGroup(
                    graphic_item=opts.GraphicItem(right="right", top="48%"),
                    children=[
                        opts.GraphicText(
                            graphic_textstyle_opts=opts.GraphicTextStyleOpts(
                                text=beside_title,
                            ),
                        ),
                    ],
                )
            ],
        )
    )
    for idx, size in enumerate(sizes):
        size_data = data[data[hue] == size]
        add_scatter(scatter, size_data, size, col_x, col_y, color=colors[idx % colors_size])
    line = (
        Line()
        .add_xaxis(bin_df[col_x].tolist())
        .add_yaxis(
            line_name,
            bin_df[col_y].tolist(),
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
            is_smooth=True,
            is_symbol_show=False,
            z=10, z_level=10,
        )
    )
    page = scatter.overlap(line)
    file_name = random_name(turbine_code, title)
    file_path = create_dir(file_path)
    html_path = page.render(os.path.join(file_path, file_name))

    return html_path, file_name


def add_scatter(scatter, data, name, col_x, col_y, color=None):
    obj = Scatter().add_xaxis(data[col_x].tolist()).add_yaxis(
        str(name)[:5], data[col_y].tolist(),
        color=color,
        label_opts=opts.LabelOpts(is_show=False),
    ).set_series_opts(
        large=True,  # 大数据优化 数据>largeThreshold就优化
        largeThreshold=2000,
    )
    scatter.overlap(obj)
