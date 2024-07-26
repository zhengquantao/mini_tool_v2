import os

from pyecharts.commons.utils import JsCode
from pyecharts.components import Table
from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Scatter, Line, Page, Grid, Bar
from common.common import random_name, create_dir
from settings.settings import float_size, main_title


def build_html(data_list, title, file_path, str_code, yaw_list=None):
    file_name = random_name(str_code, title)
    file_path = create_dir(file_path)
    if len(data_list) == 1:
        page = build_page(data_list[0])
        html_path = page.render(os.path.join(file_path, file_name))
        return html_path, file_name

    page = Page(layout=opts.PageLayoutOpts(justify_content="center"), page_title=main_title)
    child_page_list = [build_table(yaw_list)]
    for data in data_list:
        child_page = build_page(data)
        child_page_list.append(child_page)

    page.add(*child_page_list)
    html_path = page.render(os.path.join(file_path, file_name))
    return html_path, file_name


def build_page(data):
    colors = ["#EBDEF0", "#D7BDE2", "#C39BD3", "#AF7AC5", "#9B59B6", "#884EA0", "#76448A"]
    colors_size = len(colors)
    scatter = (
        Scatter(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px", page_title=main_title,
                                        bg_color="white"))
        .set_global_opts(
            title_opts=opts.TitleOpts(pos_left="25%",
                                      title=f"{data['turbine_code']} 偏航对风误差：{data['yaw_err_mean']}  "
                                            f"偏航状态：{data['yaw_err_status']}"),
            legend_opts=opts.LegendOpts(is_show=False),  # 将图例放在右边
            xaxis_opts=opts.AxisOpts(
                name="风向",
                type_="value",
                name_gap=35,
                name_location="middle",
                splitline_opts=opts.SplitLineOpts(is_show=False),
            ),
            yaxis_opts=opts.AxisOpts(
                name="风速",
                type_="value",
                name_gap=35,
                name_location="middle",
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=True, is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=True),
                min_=max(int(min(data['yaw_turbine_list'][0]['line_y'])) - 1, 0),
            ),
            tooltip_opts=opts.TooltipOpts(is_show=False),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                # orient="horizontal",  # 工具栏 icon 的布局朝向
                pos_left="right",  # 工具栏组件离容器左侧的距离
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
        )
    )
    for idx, item in enumerate(data['yaw_turbine_list']):
        add_scatter(scatter, item, color=colors[idx % colors_size])
        add_line(scatter, item, color=colors[idx % colors_size])

    bar = add_bar(data)
    grid = (
        Grid(init_opts=opts.InitOpts(bg_color="white"))
        .add(scatter, grid_opts=opts.GridOpts(pos_left="5%", width="80%"))
        .add(bar, grid_opts=opts.GridOpts(pos_left="90%", width="3%"))
    )
    return grid


def build_table(yaw_list):
    yaw_list.sort(key=lambda item: abs(item[1]))

    table = Table()
    headers = ["排行", "风机号", "偏航对风误差", "偏航状态", "简单描述"]
    rows = [[idx] + row for idx, row in enumerate(yaw_list, start=1)]
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=opts.ComponentTitleOpts(title="偏航对风分析总览")
    )
    return table


def add_line(scatter, item, color=None):
    line = (
        Line()
        .add_xaxis(item['line_x'].tolist())
        .add_yaxis(
            '',
            item['line_y'].tolist(),
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
            color=color,
            is_smooth=False,
            is_symbol_show=False,
            z=10, z_level=10,
            xaxis_index=0,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(symbol="diamond", symbol_size=10, coord=[*item["min_point"]],
                                       itemstyle_opts=opts.ItemStyleOpts(
                                           border_width=1, border_color="red", color="red"), ),
                ]
            ),
            markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(x="0")],
                                            linestyle_opts=opts.LineStyleOpts(color="red", type_="dashed")),
        )
    )
    scatter.overlap(line)


def add_scatter(scatter, data, color=None):
    obj = Scatter().add_xaxis(data['scatter_x'].tolist()).add_yaxis(
        '', data['scatter_y'].tolist(),
        color=color,
        xaxis_index=0,
        symbol_size=4,
        label_opts=opts.LabelOpts(is_show=False),
    ).set_series_opts(
        large=True,  # 大数据优化 数据>largeThreshold就优化
        largeThreshold=2000,
    )
    scatter.overlap(obj)


def add_bar(data):
    bar = Bar(init_opts=opts.InitOpts(bg_color="white"))
    bar.add_xaxis([item['power'] for item in data['yaw_turbine_list']])
    bar.add_yaxis('', [10] * len(data['yaw_turbine_list']), category_gap="0%",
                  label_opts=opts.LabelOpts(is_show=False),

                  itemstyle_opts=opts.ItemStyleOpts(color=JsCode(
                    """
                    function(value){
                        var colors = ['#EBDEF0', '#D7BDE2', '#C39BD3', '#AF7AC5', '#9B59B6', '#884EA0', '#76448A'];
                        var index = value['dataIndex'] % colors.length;
                        return colors[index];
                    }
                    """)))
    bar.reversal_axis()
    bar.set_global_opts(
        legend_opts=opts.LegendOpts(is_show=False),
        yaxis_opts=opts.AxisOpts(
            is_show=True,
            name="功率（kW）",
            name_location="middle",
            name_gap=50,
            position="right",
            splitline_opts=opts.SplitLineOpts(is_show=False),
            axisline_opts=opts.AxisLineOpts(is_show=False, is_on_zero=False),
            axistick_opts=opts.AxisTickOpts(is_show=False),
        ),
        xaxis_opts=opts.AxisOpts(is_show=False),
        tooltip_opts=opts.TooltipOpts(is_show=False),
    )
    return bar

