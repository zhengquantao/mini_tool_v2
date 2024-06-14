import os

from pyecharts.globals import CurrentConfig

from common.common import random_name, create_dir
from graph.power_sort_chart import sort_chart
from settings.settings import float_size, main_title

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Page
from pyecharts.commons.utils import JsCode


def build_html(factor_path, turbine, plot_power_df, *args, **kwargs):

    page = page_simple_layout(plot_power_df)
    file_name = random_name(turbine, "能效评估结果总览")
    factor_path = create_dir(factor_path)
    html_path = page.render(os.path.join(factor_path, file_name))

    return html_path, file_name


def top_page(plot_power_df):
    plot_power_df = plot_power_df.sort_values(by="Weighted_diff")
    bar = (
        Bar(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px"))
        .add_xaxis(plot_power_df["turbine_code"].tolist())
        .add_yaxis("理论发电量", plot_power_df["pdf_power(mWh)"].tolist(), yaxis_index=1)
        .add_yaxis("实际发电量", plot_power_df["iec_power(mWh)"].tolist(), yaxis_index=1)
        .extend_axis(
            yaxis=opts.AxisOpts(
                type_="value",
                name="发电量(kwh)",
                min_=0,
                position="left",
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
                splitline_opts=opts.SplitLineOpts(
                    is_show=True
                ),
            ),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="能效评估结果总览"),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="系数(%)",
                position="right",
                # splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                # min_=0,
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
                trigger="axis",
                axis_pointer_type="shadow",
                formatter=JsCode('''function (params) {
                    let ret_val = params[0].name + '<br />';
                    ret_val += params[0].seriesName + ': ' + params[0].value + ' kw <br />';
                    ret_val += params[1].seriesName + ': ' + params[1].value + ' kw <br />';
                    ret_val += params[2].seriesName + ': ' + params[2].value[1] + ' % <br />';
                    ret_val += params[3].seriesName + ': ' + params[3].value[1] + ' % <br />';
                    return ret_val;
                }''')
        ))
        )

    # 创建Line图
    line1 = (
        Line()
        .add_xaxis(plot_power_df["turbine_code"].tolist())
        .add_yaxis("能效系数", plot_power_df["Weighted_diff"].tolist(),
                   label_opts=opts.LabelOpts(is_show=False),
                   is_symbol_show=True, is_smooth=True, symbol_size=7,
                   z=1, z_level=1, yaxis_index=0, linestyle_opts=opts.LineStyleOpts(width=4))
        .add_yaxis("能量可利用率", plot_power_df["EBA_ratio"].tolist(),
                   label_opts=opts.LabelOpts(is_show=False),
                   is_symbol_show=True, is_smooth=True, symbol_size=7,
                   z=1, z_level=1, yaxis_index=0, linestyle_opts=opts.LineStyleOpts(width=4))
    )

    page = bar.overlap(line1)
    return page


def page_simple_layout(plot_power_df):
    page = Page(layout=Page.SimplePageLayout, page_title=main_title)
    page.add(
        top_page(plot_power_df),
        sort_chart(plot_power_df),

    )
    return page
