from pyecharts import options as opts
from pyecharts.charts import Line

line = Line()
line.add_xaxis(["A", "B", "C", "D", "E", "F"])
line.add_yaxis("示例系列", [12, 34, 56, 10, 23, 45])

# 自定义JavaScript来改变series_name的位置
line.set_global_opts(
    title_opts=opts.TitleOpts(title="Line 图表示例"),
    # 使用JavaScript来覆盖默认的图表样式
    legend_opts=opts.LegendOpts(pos_left="right", pos_top="50%"),
    toolbox_opts=opts.ToolboxOpts(
        is_show=True,  # 是否显示该工具
        orient="vertical",  # 工具栏 icon 的布局朝向
        pos_left="right",  # 工具栏组件离容器左侧的距离
        # pos_top="5%"
    ),
    # 区域缩放
    datazoom_opts=opts.DataZoomOpts(
        is_show=True,  # 是否显示 组件。如果设置为 false，不会显示，但是数据过滤的功能还存在
        type_="slider",  # 组件类型，可选 "slider", "inside"
        orient="horizontal",  # 可选值为：'horizontal', 'vertical'
        range_start=0,  # 显示区域开始
        range_end=100,  # 显示区域结束
    ),
)

line.render("line_custom_name_position.html")