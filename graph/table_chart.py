import os

from pyecharts.globals import CurrentConfig

from common.common import random_name, create_dir

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.components import Table
from pyecharts.charts import Scatter, Page
from settings.settings import main_title


def build_html(factor_path, turbine, plot_power_df, result_str, *args, **kwargs):

    plot_power_df = plot_power_df.sort_values(by="Weighted_diff", ascending=False)

    file_name = random_name(turbine, "赛马排行总览")
    factor_path = create_dir(factor_path)
    table = Table()
    plot_power_df = plot_power_df[["turbine_code", "Weighted_diff", "EBA_ratio", "pdf_power(mWh)", "iec_power(mWh)"]]
    headers = ["排行", "风机号", "能效偏差率(%)", "能量可利用率(%)", "理论发电量(kW·h)", "实际发电量(kW·h)"]
    rows = [[idx] + row.tolist() for idx, row in enumerate(plot_power_df.values, start=1)]
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=opts.ComponentTitleOpts(
            title="赛马排行总览", subtitle=result_str,
            subtitle_style={"style": "font-size: 14px;padding: 0 2ch;text-indent: 2ch;"}),
    )

    page = Page(layout=opts.PageLayoutOpts(justify_content="center"), page_title=main_title)
    child_page_list = [table, build_scatter(turbine, plot_power_df,)]

    page.add(*child_page_list)
    html_path = page.render(os.path.join(factor_path, file_name))

    return html_path, file_name


def build_scatter(turbine, plot_power_df,):
    scatter = (
        Scatter()
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
            title_opts=opts.TitleOpts(title=f"能效偏差率总览", pos_top="32", padding=""),
            yaxis_opts=opts.AxisOpts(name="能效偏差率(%)", name_gap=30, name_location="middle",),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                orient="vertical",  # 工具栏 icon 的布局朝向
                pos_top="40",
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
                }),
            visualmap_opts=opts.VisualMapOpts(max_=plot_power_df["Weighted_diff"].max(),
                                              min_=plot_power_df["Weighted_diff"].min(),
                                              pos_right="10", pos_bottom="50",),
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
                formatter="{c} %",
            )))
    return scatter
