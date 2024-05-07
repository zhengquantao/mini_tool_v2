import pandas as pd


def Ti_feature_add(data, speed_label, time_label, time):
    """
    计算湍流强度
    Parameters
    ----------
    data
    speed_label
    time_label

    Returns
    -------

    """

    data[time_label] = pd.to_datetime(data[time_label])
    pass
    for i in range(data.shape[0]):
        time = data.iloc[i, time_label]
        data.iloc[i, "TI"] = None
