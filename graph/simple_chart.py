import os

from pyecharts.globals import CurrentConfig

from common.common import random_name, create_dir
from settings.settings import opening_dict, main_title

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Scatter


Echarts_Type = {
    "Bar": Bar,
    "BarStack": Bar,
    "BarReversal": Bar,
    "BarStackReversal": Bar,
    "Line": Line,
    "LineGap": Line,
    "Scatter": Scatter,
}


def build_html(x, y, title, echart_type="bar", save_path=None):
    echarts = Echarts_Type.get(echart_type, Bar)
    obj = echarts(init_opts=opts.InitOpts(page_title=main_title, bg_color="white"))
    obj.add_xaxis(x.to_list())
    if echart_type == "BarStack":
        add_yaxis(obj, y, stack="stack1")
    elif echart_type == "BarReversal":
        add_yaxis(obj, y)
        obj.reversal_axis()
        obj.set_series_opts(label_opts=opts.LabelOpts(position="right"))
    elif echart_type == "LineGap":
        add_yaxis(obj, y)
        obj.set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False))
        obj.set_global_opts(
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),)
    else:
        add_yaxis(obj, y)

    obj.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
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
        # 区域缩放
        datazoom_opts=opts.DataZoomOpts(
            is_show=True,  # 是否显示 组件。如果设置为 false，不会显示，但是数据过滤的功能还存在
            type_="slider",  # 组件类型，可选 "slider", "inside"
            orient="horizontal",  # 可选值为：'horizontal', 'vertical'
            range_start=0,
            range_end=5,
        ),
        # 提示
        tooltip_opts=opts.TooltipOpts(
            is_show=True,  # 是否显示提示框组件，包括提示框浮层和 axisPointer。
            # 触发类型。可选：
            # 'item': 数据项图形触发，主要在散点图，饼图等无类目轴的图表中使用。
            # 'axis': 坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。
            # 'none': 什么都不触发
            trigger="axis",
        )
    )
    file_name = random_name("00", echart_type)
    save_path = save_path or opening_dict[os.getpid()]["path"]
    save_path = create_dir(save_path)
    html_path = obj.render(os.path.join(save_path, file_name))
    return html_path, file_name


def add_yaxis(bar, y, **kwargs):
    for column_name in y.columns:
        bar.add_yaxis(column_name, y[column_name].to_list(), label_opts=opts.LabelOpts(is_show=False), **kwargs)
