import os

from pyecharts.components import Table
from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.charts import Line, Page
from common.common import random_name, create_dir
from settings.settings import float_size, main_title


def build_html(wind_flow_dict, title, file_path, str_code):
    file_name = random_name(str_code, title)
    file_path = create_dir(file_path)
    lines_obj = (
        Line(init_opts=opts.InitOpts(width=f"{float_size[0]}px", height=f"{float_size[1]}px", page_title=main_title,
                                     bg_color="white"))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"湍流强度"),
            # legend_opts=opts.LegendOpts(is_show=True, pos_right=0),  # 将图例放在右边
            xaxis_opts=opts.AxisOpts(
                name="风速",
                type_="value",
                name_gap=30,
                name_location="middle",
                splitline_opts=opts.SplitLineOpts(is_show=False),
                min_=2.5,
            ),
            yaxis_opts=opts.AxisOpts(
                name="湍流强度",
                type_="value",
                name_gap=30,
                name_location="middle",
                splitline_opts=opts.SplitLineOpts(is_show=False),
                axisline_opts=opts.AxisLineOpts(is_show=True, is_on_zero=False),
                axistick_opts=opts.AxisTickOpts(is_show=True),
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True, trigger="axis",),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,  # 是否显示该工具
                orient="vertical",  # 工具栏 icon 的布局朝向
                pos_left="",
                pos_top="30",
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
        )
    )
    for item in wind_flow_dict.values():
        add_line(lines_obj, item)

    page = Page(layout=opts.PageLayoutOpts(justify_content="center"), page_title=main_title)
    child_page_list = [build_table(wind_flow_dict), lines_obj]

    page.add(*child_page_list)
    html_path = page.render(os.path.join(file_path, file_name))
    return html_path, file_name


def add_line(line_obj, item):
    line = (
        Line()
        .add_xaxis(item['wind_speed'])
        .add_yaxis(
            item['turbine_code'],
            item['terrain'],
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
            is_smooth=False,
            is_symbol_show=True,
            z=10, z_level=10,
            xaxis_index=0,
        )
    )
    line_obj.overlap(line)


def build_table(wind_flow_dict):
    table = Table()
    headers = ["机组编号", "平均风速(m/s)", "平均风功率密度(kW/m^2)", "全风速湍流强度", "2.5~15风速湍流强度", "最大风速(m/s)", ]
    rows = [[row["turbine_code"], row["wind_mean"], row["wind_density"], row["terrain_mean_all"], row["terrain_mean"],
             row["wind_max"]]
            for row in wind_flow_dict.values()]
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=opts.ComponentTitleOpts(title="风况总览")
    )
    return table

