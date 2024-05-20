import os

from pyecharts.globals import CurrentConfig

from common.common import random_name, create_dir
from settings.settings import float_size

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Scatter


def build_html(factor_path, turbine, plot_power_df, *args, **kwargs):
    tmp_data = {
        "能效一级": [(101.8, 4.11), (102.6, 4.17), (101.8, 4.13), (102.4, 4.16)],
        "能效二级": [(101.9, 4.12), (102.5, 4.18)],
        "能效三级": [(102.1, 4.15)],
        "能效四级": [(101.5, 4.05), (102.3, 4.10)],
        "标杆风机": [(102.0, 4.15)]
    }
    scatter = (
        Scatter(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px"))
        .add_xaxis([tmp_data["标杆风机"][0][0]])
        .add_yaxis(
            series_name="标杆风机",
            y_axis=[tmp_data["标杆风机"][0][1]],
            symbol_size=20,
            label_opts=opts.LabelOpts(is_show=False),
            color="#f30e08"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="能效等级总览"),
            xaxis_opts=opts.AxisOpts(type_="value", min_=101.05, max_=102.95),
            yaxis_opts=opts.AxisOpts(type_="value", min_=4.00, max_=4.20),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                orient="vertical",  # 工具栏 icon 的布局朝向
                pos_left="right"  # 工具栏组件离容器左侧的距离
            ),
            # 区域缩放
            datazoom_opts=opts.DataZoomOpts(
                is_show=True,  # 是否显示 组件。如果设置为 false，不会显示，但是数据过滤的功能还存在
                type_="inside",  # 组件类型，可选 "slider", "inside"
                orient="horizontal",  # 可选值为：'horizontal', 'vertical'
                range_start=0,  # 显示区域开始
                range_end=100,  # 显示区域结束
            ),
            # 提示
            tooltip_opts=opts.TooltipOpts(
                is_show=True,  # 是否显示提示框组件，包括提示框浮层和 axisPointer。
                # 触发类型。可选：
                # 'item': 数据项图形触发，主要在散点图，饼图等无类目轴的图表中使用。
                # 'axis': 坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。
                # 'none': 什么都不触发
                trigger="axis",
                axis_pointer_type="cross",
            )))
    add_scatter(scatter, tmp_data["能效一级"], "能效一级", color="#aab536")
    add_scatter(scatter, tmp_data["能效二级"], "能效二级", color="#39b536")
    add_scatter(scatter, tmp_data["能效三级"], "能效三级", color="#3676b5")
    add_scatter(scatter, tmp_data["能效四级"], "能效四级", color="#00b3f0")

    file_name = random_name(turbine, "能效等级总览")
    factor_path = create_dir(factor_path)
    html_path = scatter.render(os.path.join(factor_path, file_name))

    return html_path, file_name


def add_scatter(scatter, data, name, color="green"):
    obj = Scatter().add_xaxis([item[0] for item in data]).add_yaxis(name, [item[1] for item in data],
                                                                    color=color, symbol_size=20,)
    scatter.overlap(obj)
