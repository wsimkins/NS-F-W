import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.DataFrame()

df['x'] = random.sample(range(1, 100), 2)
df['y'] = random.sample(range(1, 100), 2)

print(df)

sns.heatmap([df.y, df.x], annot=False, fmt="d")
sns.plt.show()
