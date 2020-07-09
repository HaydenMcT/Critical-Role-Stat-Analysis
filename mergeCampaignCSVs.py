import pandas as pd
import numpy as np

data_c2 = pd.read_csv("AllRollsWildemount.csv")
data_c1 = pd.read_csv("AllRollsTalDorei.csv")

c2 = np.array(data_c2)
c1 = np.array(data_c1)

merged = np.concatenate((c1, c2))

merged_data = pd.DataFrame(merged)
merged_data.to_csv("AllRolls.csv")