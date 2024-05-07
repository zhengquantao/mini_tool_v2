'''
coding:utf-8
@Software:PyCharm
@Time:2023/8/25 16:49
@Author: Natsu
'''
import os

# 日志配置

log_dir = 'logs'
log_name = 'aep_log'
root_dir = os.getcwd()

farm_name = "guazhouMY1.5"

# 置信区间范围
confidence_num = 0.8

# 文件存放地址
##尖峰
# file_path = r"E:\scy\能效评估数据\尖峰"
##骆驼台子
# file_path = r"E:\scy\能效评估数据\骆驼台子\处理完成数据"
##桃山湖
# file_path = r"E:\scy\能效评估数据\桃山湖\桃山湖10分钟数据2023上半年\处理完成数据"
##霍林河
# file_path = r"E:\scy\能效评估数据\hlh\新建文件夹\wsts"
##瓜州
file_path = r"E:\scy\能效评估数据\瓜州\明阳1.5"



# #标杆风机
# base_turbine = "10026006.csv"


# 标志位，判断是要比对结果(1)还是匹配的数据(0)
flag = 0

# 所需特征
##霍林河
# feature_columns = ["wind_speed","Direction"]
##尖峰
# feature_columns = ["平均风速(m/s)", "平均风向（机舱）", "平均机舱温度", "平均空气密度"]
##骆驼台子
# feature_columns = ['风速', '风角度（对北）', '功率']
##桃山湖
# feature_columns = ["grwindspeed_avg",
#                    "grvanedirection_1sec_avg"]

# ## 瓜州
feature_columns = ["风速", "风向"]

# 时间标签
## 霍林河
# real_time = ["real_time"]
##尖峰
# real_time = ["时间"]
##骆驼台子
# real_time = ["记录时间"]
##桃山湖
# real_time = ["rectime"]
## 瓜州
real_time = ["real_time"]

# 风速标签
#霍林河
# wind_col = ["wind_speed"]
##尖峰
# wind_col = ["平均风速(m/s)"]
##骆驼台子
# wind_col = ["风速"]
##桃山湖
# wind_col = ["grwindspeed_avg"]
#瓜州
wind_col = ["风速"]

# 风向标签
## 霍林河
# dirction_col = ["Direction"]
##尖峰
# dirction_col = ["平均风向（机舱）"]
##骆驼台子
# dirction_col = ["风角度（对北）"]
##桃山湖
# dirction_col = ["grvanedirection_1sec_avg"]
## 瓜州
dirction_col = ["风向"]

# 温度标签
##尖峰
# temperature_col = ["平均机舱温度"]
##骆驼台子
# temperature_col = []
##桃山湖
### 存在一部分风机的温度数值异常，暂不取   grtempoutdoor_avg
temperature_col = []

# 空气密度标签
##尖峰
# airdensity_col = ["平均空气密度"]
##骆驼台子
# airdensity_col = []
##桃山湖
airdensity_col = []

# 目标值
##霍林河
# target_columns = ["power"]
##尖峰
# target_columns = ["平均功率"]
##骆驼台子
# target_columns = ["功率"]
##桃山湖
# target_columns = ["grgenpowerforprocess_avg"]
##瓜州
target_columns = ["功率"]

# 理论功率曲线文件路径
# curve_line_path = r"E:\scy\能效评估数据\桃山湖\1.5MW-82理论静态功率曲线_1.255.xls"
##霍林河
# curve_line_path = r"E:\scy\能效评估数据\hlh\cov_data\tb_wind_base_farm_power.csv"
##瓜州
curve_line_path = r"H:\scy\文档\能效评估\DSWE-Python-main\config\MY_power_theoretical.csv"

# 结果存放路径
result_path = r"H:\scy\文档\能效评估\DSWE-Python-main\result"

## 图片存放路径
img_path = r"H:\scy\文档\能效评估\DSWE-Python-main\img"
