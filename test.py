import numpy as np
import pandas as pd

# 定义你的数据
a = np.array([1, 2, 3, 4])
b = np.array([0.3, 0.4, 1.4, 3.4, 3.5])

# 使用pandas的cut函数将b分组
bins = pd.cut(b, a)

# 创建一个DataFrame来存储数据
df = pd.DataFrame({'a': a, 'b': b, 'bins': bins})

# 对每个分组获取a的最大值
result = df.groupby('bins')['a'].max()

print(result)
