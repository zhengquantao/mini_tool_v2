import os

import chardet
import pandas as pd

def detect_encoding(filename):
    with open(filename, 'rb') as file:
        rawdata = file.read(1000)
        encoding = chardet.detect(rawdata)['encoding']
        return encoding

def transform_data(path):
    for file in os.listdir(path):
        if not file.endswith(".csv"):
            continue
        print(file)
        data = pd.read_csv(os.path.join(path, file), encoding=detect_encoding(os.path.join(path, file)))
        data.loc[:, "wind_speed"] = data.loc[:, "wind_speed"].astype("float")
        data.loc[:, "wind_direction"] = data.loc[:, "wind_direction"].astype("float")

        data.loc[:, "air_density"] = data.loc[:, "air_density"].astype("float")
        data.loc[:, "pitch_angle"] = data.loc[:, "pitch_angle"].astype("float")

        data.loc[:, "nacelle_temperature"] = data.loc[:, "nacelle_temperature"].apply(lambda x: str(x).replace(",", ""))
        data.loc[:, "nacelle_temperature"] = data.loc[:, "nacelle_temperature"].astype("float")

        data.loc[:, "power"] = data.loc[:, "power"].apply(lambda x: str(x).replace(",", ""))
        data.loc[:, "power"] = data.loc[:, "power"].astype("float")

        data.loc[:, "generator_speed"] = data.loc[:, "generator_speed"].apply(lambda x: str(x).replace(",", ""))
        data.loc[:, "generator_speed"] = data.loc[:, "generator_speed"].astype("float")

        data["power"] = pd.to_numeric(data["power"])
        data["generator_speed"] = pd.to_numeric(data["generator_speed"])
        data["nacelle_temperature"] = pd.to_numeric(data["nacelle_temperature"])

        data.to_csv(os.path.join(path, file), encoding="utf-8")


if __name__ == '__main__':
    transform_data(r"C:\Users\EDY\Desktop\30057")
