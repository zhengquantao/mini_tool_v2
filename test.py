from pyecharts.charts import Bar, Line
from pyecharts import options as opts

# 数据
x_data = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
bar_data = [820, 932, 901, 934, 1290, 1330, 1320]
line_data = [820, 932, 901, 934, 1290, 1330, 1320, 1400, 1500, 1600, 1700, 1800]

# 创建一个Bar对象
bar = (
    Bar()
    .add_xaxis(x_data)
    .add_yaxis("商家A", bar_data)
)

# 创建一个Line对象
line = (
    Line()
    .add_xaxis(x_data + ["Extra1", "Extra2", "Extra3", "Extra4", "Extra5"])
    .add_yaxis("商家B", line_data, yaxis_index=1)
)

# 将Line图添加到Bar图中
bar.overlap(line)

# 设置全局配置项
bar.set_global_opts(
    title_opts=opts.TitleOpts(title="Bar-Line双轴图"),
    yaxis_opts=opts.AxisOpts(name="商家A"),

)

# 渲染图像
bar.render()
