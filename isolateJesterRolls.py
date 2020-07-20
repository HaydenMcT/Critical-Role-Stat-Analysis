import pandas as pd
import numpy as np

X = np.array(pd.read_csv("AllRollsWildemount.csv")) #load data

character_idx = 3 # the 3rd column refers to the character name

Jester_Rolls = X[X[:, character_idx] == 'Jester']

X = pd.DataFrame(Jester_Rolls, columns = ("Index of Roll in AllRollsWildemount.csv", "Episode", "Time", "Character", "Type of Roll", "Total Value", "Natural Value", "Crit?", "Damage Dealt", "# Kills", "Notes"))
X.to_csv("JesterRolls.csv")

#np.arange(X.shape[0])[np.any([X[:,character_idx] == "Jester", X[:, 2] == "Trinket"], axis=0)]