import pandas as pd
from sqlalchemy import create_engine


def export_data(db_url, export_fields, table_list, filters):
    engine = create_engine(db_url)
    for table in table_list:
        # SQL查询语句，选择你需要的字段
        field_str = ",".join([f"{field[0]} AS {field[1]}" for field in export_fields])
        query = f"SELECT {field_str} FROM {table} WHERE real_time > '{filters[0]}' AND real_time < '{filters[1]}'"

        # 使用pandas的read_sql_query函数执行SQL语句并获取数据
        df = pd.read_sql_query(query, engine)

        # 将数据保存为CSV文件
        df.to_csv(f'{table}.csv', index=False)


if __name__ == '__main__':
    db_url = "mysql+pymysql://develop:szly2022@10.168.1.246:5029/db30000_2024?charset=utf8"
    export_fields = [("real_time", "real_time"),
                     ("wtid", "turbine_code"),
                     ("grWindSpeed", "wind_speed"),
                     ("grGeneratorSpeed1", "generator_speed"),
                     ("grPitchAngle1A", "pitch_angle"),
                     ("grNacellePositionToNorth", "nacelle_direction"),
                     ("grWindDirction", "wind_direction"),
                     ("grAirDensity",  "air_density"),
                     ("grNacelleTemperture", "nacelle_temperature"),
                     ("grGridActivePower", "power"),
                     ]
    table_list = ["t30000001_all", "t30000006_all"]
    filters = ["2024-01-01 00:00:00", "2024-12-31 23:59:59"]
    export_data(db_url, export_fields, table_list, filters)
