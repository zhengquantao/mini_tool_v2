
import os

from graph import geo_power_chart
from models.utils.AEP import aep_analysis
# from models.utils.Energy_compare import base_data_process
from settings.settings import power_theoretical
from common import loggers


# #IEC代码
def geo_main(file_path, project_path):
    factor_name = project_path.split(os.sep)[-1]
    curve_line_path = os.path.join(project_path, power_theoretical)
    turbine_code = file_path.split(os.sep)[-1].split(".")[0]

    base_turbine, all_statistics = aep_analysis.aep_main(file_path, factor_name, ["real_time"], ["wind_speed"],
                                                         ["wind_direction"],
                                                         ["nacelle_temperture"], [],  # ["air_density"]
                                                         ["power"], curve_line_path, confidence_num=0.8,
                                                         logger=loggers.logger)

    file_paths, file_name = geo_power_chart.build_html(project_path, turbine_code, all_statistics)

    return file_paths, file_name

