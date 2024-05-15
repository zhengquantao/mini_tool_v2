import pandas as pd 

# 创建一个示例时间序列数据框 
data = {'date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'), 
        'value': range(365), "value1": range(365)}
df = pd.DataFrame(data) 

# 将日期列设置为索引 
df.set_index('date', inplace=True) 

# 使用resample()方法进行重新采样 
# 将每日数据转换为每月数据并计算每月的总和 
monthly_data = df.resample('M').mean()

# 将每月数据转换为每季度数据并计算每季度的平均值 
quarterly_data = monthly_data.resample('Q').mean() 

# 将每季度数据转换为每年数据并计算每年的最大值 
annual_data = quarterly_data.resample('Y').max() 

print(monthly_data) 
print(quarterly_data) 
print(annual_data) 