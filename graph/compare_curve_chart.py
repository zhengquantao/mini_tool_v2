import os

from pyecharts.globals import CurrentConfig

from common.common import random_name, create_dir
from settings.settings import float_size, main_title

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Scatter, Line


def build_html(factor_path, turbine, abnormal_scatter, fitting_line, normal_scatter,
               power_line, *args, **kwargs):

    scatter1 = (
        Scatter(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px", page_title=main_title,
                                        bg_color="white"))
        .add_xaxis(abnormal_scatter[0].tolist())
        .add_yaxis(abnormal_scatter[2], abnormal_scatter[1].tolist(), label_opts=opts.LabelOpts(is_show=False),
                   color="#ffb48d")
        .set_series_opts(
            large=True,  # 大数据优化 数据>largeThreshold就优化
            largeThreshold=2000,)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="理论与实际功率对比分析"),
            xaxis_opts=opts.AxisOpts(
                type_="value",
                name="风速(m/s)",
                splitline_opts=opts.SplitLineOpts(is_show=True),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="功率(kW)",
                splitline_opts=opts.SplitLineOpts(is_show=True),
                min_=0,
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                orient="vertical",  # 工具栏 icon 的布局朝向
                pos_left="",
                pos_right="5",  # 工具栏组件离容器左侧的距离
                feature={
                    "saveAsImage": opts.ToolBoxFeatureSaveAsImageOpts(background_color="#ffffff", title="保存图片"),
                    "restore": opts.ToolBoxFeatureRestoreOpts(),
                    "dataView": opts.ToolBoxFeatureDataViewOpts(),
                    "dataZoom": opts.ToolBoxFeatureDataZoomOpts(back_title="缩放还原"),
                    "magicType": opts.ToolBoxFeatureMagicTypeOpts(line_title="切换折线", bar_title="切换柱状",
                                                                  stack_title="切换堆叠", tiled_title="切换平铺", ),
                    "brush": None,
                }
            ),
            # # 区域缩放
            # datazoom_opts=opts.DataZoomOpts(
            #     is_show=True,  # 是否显示 组件。如果设置为 false，不会显示，但是数据过滤的功能还存在
            #     type_="slider",  # 组件类型，可选 "slider", "inside"
            #     orient="horizontal",  # 可选值为：'horizontal', 'vertical'
            #     range_start=0,  # 显示区域开始
            #     range_end=100,  # 显示区域结束
            # ),
            # # 提示
            # tooltip_opts=opts.TooltipOpts(
            #     is_show=True,  # 是否显示提示框组件，包括提示框浮层和 axisPointer。
            #     # 触发类型。可选：
            #     # 'item': 数据项图形触发，主要在散点图，饼图等无类目轴的图表中使用。
            #     # 'axis': 坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。
            #     # 'none': 什么都不触发
            #     trigger="axis",
            # )
        ))
    scatter2 = (
        Scatter(init_opts=opts.InitOpts())
        .add_xaxis(normal_scatter[0].tolist())
        .add_yaxis(normal_scatter[2], normal_scatter[1].tolist(), label_opts=opts.LabelOpts(is_show=False),
                   color="#81bac4")
        .set_series_opts(
            large=True,  # 大数据优化 数据>largeThreshold就优化
            largeThreshold=2000, )
        .set_global_opts(title_opts=opts.TitleOpts(title=normal_scatter[2]),))

    # 创建Line图
    line1 = (
        Line(init_opts=opts.InitOpts())
        .add_xaxis(fitting_line[0])
        .add_yaxis(fitting_line[2], fitting_line[1],
                   label_opts=opts.LabelOpts(is_show=False),
                   is_symbol_show=False, linestyle_opts=opts.LineStyleOpts(width=4),
                   z=10, z_level=10, color="#ff0000")
        .set_global_opts(title_opts=opts.TitleOpts(title=fitting_line[2]))
    )
    line2 = (
        Line(init_opts=opts.InitOpts())
        .add_xaxis(power_line[0].tolist())
        .add_yaxis(power_line[2], power_line[1].tolist(),
                   label_opts=opts.LabelOpts(is_show=False),
                   # 隐藏标签点
                   is_symbol_show=False, linestyle_opts=opts.LineStyleOpts(width=4),
                   # 控制页面层级
                   z=10, z_level=10, color="#2078bc")
        .set_global_opts(title_opts=opts.TitleOpts(title=power_line[2]),)
    )

    page = scatter1.overlap(scatter2).overlap(line1).overlap(line2)
    file_name = random_name(turbine, "理论与实际功率对比分析")
    factor_path = create_dir(factor_path)
    html_path = page.render(os.path.join(factor_path, file_name))

    return html_path, file_name
