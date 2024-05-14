from pyecharts import options as opts
from pyecharts.charts import Line

line = Line()
line.add_xaxis(["A", "B", "C", "D", "E", "F"])
line.add_yaxis("示例系列", [12, 34, 56, 10, 23, 45])

# 自定义JavaScript来改变series_name的位置
line.set_global_opts(
    title_opts=opts.TitleOpts(title="Line 图表示例"),
    # 使用JavaScript来覆盖默认的图表样式
    init_opts=opts.InitOpts(
        # 在这里插入自定义的JavaScript代码
        js_codes=[
            """
            chart.on('updateAxisPointer', function (event) {
                var xAxisInfo = event.axesInfo[0];
                if (xAxisInfo) {
                    var dimension = xAxisInfo.value + 1;
                    chart.setOption({
                        series: [{
                            label: {
                                normal: {
                                    show: true,
                                    position: 'inside', // 改变位置
                                    formatter: '{c}'
                                }
                            },
                            // 其他需要的配置...
                        }]
                    });
                }
            });
            """
        ]
    ),
)

line.render("line_custom_name_position.html")