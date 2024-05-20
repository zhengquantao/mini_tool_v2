import os

from pyecharts.globals import CurrentConfig

CurrentConfig.ONLINE_HOST = "http://127.0.0.1:38121/"

from pyecharts.charts import Page
from common.common import random_name, create_dir
from graph.power_density_chart import build_page


def build_html(factor_path, data_list, factor_name, *args, **kwargs):
    page = Page(layout=Page.SimplePageLayout)
    child_page_list = []
    for data in data_list:
        child_page = build_page(data[1][0], data[1][1],)
        child_page_list.append(child_page)
    page.add(*child_page_list)

    file_name = random_name(factor_name, "风资源对比总览图")
    factor_path = create_dir(factor_path)
    html_path = page.render(os.path.join(factor_path, file_name))

    return html_path, file_name

