import os

from pyecharts.globals import CurrentConfig

from common.common import random_name, create_dir

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts import options as opts
from pyecharts.components import Table


def build_html(factor_path, turbine, plot_power_df, *args, **kwargs):

    plot_power_df = plot_power_df.sort_values(by="Weighted_diff", ascending=False)

    file_name = random_name(turbine, "赛马排行总览")
    factor_path = create_dir(factor_path)
    table = Table()
    plot_power_df = plot_power_df[["turbine_code", "Weighted_diff", "EBA_ratio", "pdf_power(mWh)", "iec_power(mWh)"]]
    headers = ["排行", "风机号", "能效系数(%)", "能量可利用率(%)", "理论发电量(kw/h)", "实际发电量(kw/h)"]
    rows = [[idx] + row.tolist() for idx, row in enumerate(plot_power_df.values, start=1)]
    table.add(headers, rows)
    table.set_global_opts(
        title_opts=opts.ComponentTitleOpts(title="赛马排行总览")
    )

    html_path = table.render(os.path.join(factor_path, file_name))

    return html_path, file_name
