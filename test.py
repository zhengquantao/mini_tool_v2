from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.options import TooltipOpts

# 数据
data = [
    ("商品A", 300),
    ("商品B", 200),
    ("商品C", 100),
]

# 创建Bar图表
bar = Bar()

# 添加数据
bar.add_xaxis([item[0] for item in data])
bar.add_yaxis("销量", [item[1] for item in data], tooltip_opts=TooltipOpts(
        formatter='''function (params) {
            let ret_val = params[0].name + "<br />";
            ret_val += params[0].seriesName + ": " + params[0].value + " kw <br />";
            ret_val += params[1].seriesName + ": " + params[1].value + " kw <br />";
            ret_val += params[2].seriesName + ": " + params[2].value[1] + " % <br />";
            ret_val += params[3].seriesName + ": " + params[3].value[1] + " % <br />";
            return ret_val;
        }'''  # 这里的{c}表示数据值，{a}表示x轴的标签
    ))

# 自定义tooltip格式化字符串，添加单位
bar.set_global_opts(
    yaxis_opts=opts.AxisOpts(
                type_="value",
                name="系数(%)",
                position="right",
                # splitline_opts=opts.SplitLineOpts(is_show=True),
                axislabel_opts=opts.LabelOpts(formatter="{value} %"),
                # min_=0,
            ),
    tooltip_opts=TooltipOpts(
        trigger="axis",
    )
)

# 渲染图表
bar.render("bar_with_unit.html")