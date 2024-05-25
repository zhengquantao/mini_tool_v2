import os

from pyecharts.commons.utils import JsCode
from pyecharts.globals import CurrentConfig

from common.common import random_name, create_dir
from settings.settings import float_size

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Scatter


def build_html(factor_path, turbine, plot_power_df, *args, **kwargs):

    scatter = (
        Scatter(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px"))
        .add_xaxis(plot_power_df["turbine_code"].to_list())
        .add_yaxis(
            series_name="",
            y_axis=plot_power_df["Weighted_diff"].to_list(),
            symbol_size=20,
            label_opts=opts.LabelOpts(is_show=True),
            # label_opts=opts.LabelOpts(formatter=JsCode(
            #         "function (params) {return params.name + ' : ' + params.value[1];}"
            #     )),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"{turbine}能效等级总览"),
            # xaxis_opts=opts.AxisOpts(is_show=False),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                orient="vertical",  # 工具栏 icon 的布局朝向
                pos_left="95%",  # 工具栏组件离容器左侧的距离
                feature={
                    "saveAsImage": opts.ToolBoxFeatureSaveAsImageOpts(background_color="#ffffff", title="保存图片"),
                    "restore": opts.ToolBoxFeatureRestoreOpts(),
                    "dataView": opts.ToolBoxFeatureDataViewOpts(),
                    "dataZoom": opts.ToolBoxFeatureDataZoomOpts(back_title="缩放还原"),
                    "magicType": opts.ToolBoxFeatureMagicTypeOpts(line_title="切换折线", bar_title="切换柱状",
                                                                  stack_title="切换堆叠", tiled_title="切换平铺", ),
                    "brush": None,
                }),
            visualmap_opts=opts.VisualMapOpts(max_=plot_power_df["Weighted_diff"].max(),
                                              min_=plot_power_df["Weighted_diff"].min()),
            # # 区域缩放
            # datazoom_opts=opts.DataZoomOpts(
            #     is_show=True,  # 是否显示 组件。如果设置为 false，不会显示，但是数据过滤的功能还存在
            #     type_="inside",  # 组件类型，可选 "slider", "inside"
            #     orient="horizontal",  # 可选值为：'horizontal', 'vertical'
            #     range_start=0,  # 显示区域开始
            #     range_end=100,  # 显示区域结束
            # ),
            # 提示
            tooltip_opts=opts.TooltipOpts(
                is_show=True,  # 是否显示提示框组件，包括提示框浮层和 axisPointer。
                # 触发类型。可选：
                # 'item': 数据项图形触发，主要在散点图，饼图等无类目轴的图表中使用。
                # 'axis': 坐标轴触发，主要在柱状图，折线图等会使用类目轴的图表中使用。
                # 'none': 什么都不触发
                trigger="item",
                # axis_pointer_type="cross",
            )))

    file_name = random_name(turbine, "能效等级总览")
    factor_path = create_dir(factor_path)
    html_path = scatter.render(os.path.join(factor_path, file_name))

    return html_path, file_name
