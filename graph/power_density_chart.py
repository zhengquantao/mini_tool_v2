import os

import numpy as np
from pyecharts.globals import CurrentConfig

from common.common import random_name
from settings.settings import float_size

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/static/"

from pyecharts import options as opts
from pyecharts.charts import Bar, Line


def build_html(factor_path, turbine, plot_power_df, xticks, name, *args, **kwargs):
    page = build_page(plot_power_df, name)
    file_name = random_name(turbine, "风资源对比图")
    html_path = page.render(os.path.join(factor_path, file_name))

    return html_path, file_name


def build_page(plot_power_df, name):
    # 计算概率密度
    # hist, bin_edges = np.histogram(plot_power_df["wind_speed"], bins=xticks)
    plot_power_df["wind_speed2"] = plot_power_df.apply(lambda row: pow(row["wind_speed"], 3), axis=1)
    grouped_mean = plot_power_df[plot_power_df["groups"] > 0].groupby("groups").agg(
        {"power": "mean", "wind_speed": "size", "air_density": "mean", "wind_speed2": "mean"})
    bar = (
        Bar(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px"))
        .add_xaxis(grouped_mean.index.tolist())
        .add_yaxis("概率密度", grouped_mean["wind_speed"].tolist(), yaxis_index=1, color="#ffc084")
        .extend_axis(
            yaxis=opts.AxisOpts(
                type_="value",
                name="数量",
                min_=0,
                position="left",
                # axislabel_opts=opts.LabelOpts(formatter="{value} °C"),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True
                ),),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=name),
            xaxis_opts=opts.AxisOpts(
                name="风速(m/s)",
                # type_="value",
                # splitline_opts=opts.SplitLineOpts(is_show=True),
                # min_=0,
                # max_=max(xticks),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="功率(kw)",
                position="right",
                # splitline_opts=opts.SplitLineOpts(is_show=True),
                min_=0,
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                orient="vertical",  # 工具栏 icon 的布局朝向
                pos_left="right"  # 工具栏组件离容器左侧的距离
            ),
            # 区域缩放
            datazoom_opts=opts.DataZoomOpts(
                is_show=True,  # 是否显示 组件。如果设置为 false，不会显示，但是数据过滤的功能还存在
                type_="slider",  # 组件类型，可选 "slider", "inside"
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
            ))
    )

    # 创建Line图
    line1 = (
        Line()
        .add_xaxis(grouped_mean.index.tolist())
        .add_yaxis("功率曲线", grouped_mean["power"].tolist(),
                   label_opts=opts.LabelOpts(is_show=False),
                   is_symbol_show=False, color="#1f77b4", is_smooth=True,
                   z=1, z_level=1, yaxis_index=0)
    )
    grouped_mean = grouped_mean.fillna(0)
    grouped_mean["wind_power_density"] = grouped_mean.apply(
        lambda row: row["air_density"] * row["wind_speed"] * pow(row["wind_speed2"], 3) / 2, axis=1)
    line2 = (
        Line()
        .add_xaxis(grouped_mean.index.tolist())
        .add_yaxis("风功率密度", grouped_mean["wind_power_density"].tolist(),
                   label_opts=opts.LabelOpts(is_show=False),
                   is_symbol_show=False, color="#bf8232", is_smooth=True,
                   z=1, z_level=1, yaxis_index=0)
    )

    page = bar.overlap(line1).overlap(line2)
    return page

