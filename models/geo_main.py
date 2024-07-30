
import os

from graph import geo_power_chart
from models.utils.AEP import aep_analysis
from models.utils.Energy_compare import base_data_process
from settings.settings import power_theoretical
from common.loggers import logger


# #IEC代码
def geo_main(file_path, project_path):
    factor_name = project_path.split(os.sep)[-1]
    curve_line_path = os.path.join(project_path, power_theoretical)
    turbine_code = file_path.split(os.sep)[-1].split(".")[0]

    base_turbine, all_statistics = aep_analysis.aep_main(file_path, factor_name, ["real_time"], ["wind_speed"],
                                                         ["wind_direction"],
                                                         ["nacelle_temperature"], ["air_density"],
                                                         ["power"], curve_line_path, confidence_num=0.8,
                                                         logger=logger)
    data_result = base_data_process(file_path, base_turbine, result_path=None,
                                    flag=1, feature_columns=["wind_speed", "wind_direction"], target_columns=["power"],
                                    wind_col=["wind_speed"], confidence=0.8, logger=logger,
                                    farm_name=factor_name)
    file_paths, file_name = geo_power_chart.build_html(project_path, factor_name, data_result, )

    return file_paths, file_name

