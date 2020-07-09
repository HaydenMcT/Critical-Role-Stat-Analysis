import pandas as pd
import numpy as np

data = pd.read_csv("AllRolls.csv")
X = np.array(data)
X = X[:,2:]

#print(X)

#Percy = X[X[:,2]=='Percy']
#print(Percy.shape)

Laura = X[np.any([X[:,2] == 'Vex\'ahlia', X[:,2] == "Jester"], axis=0)]
print(Laura.shape)
tidyDiceRolls = []
adv = 0
disadv = 0
plusd4 = 0
missingData = 0
rolls = np.zeros(21)
for i, roll in enumerate(Laura[:,5]):
    d4 = False
    rollType = str(Laura[i, 3]).lower()
    notes = str(Laura[i, 9]).lower()
    if rollType == 'healing' or rollType == 'damage' or rollType == 'other':
        pass
    else: 
        if ('bless' in notes and 'blessing' not in notes) or 'guidance' in notes:
            plusd4 += 1
            #print(notes)
            if (roll == 'Unknown' or np.isnan(float(roll))):
                missingData += 1
                #print("disregarded a d4 roll because bless roll was unknown")
                #I think these can be treated as MCAR (although they probably aren't ones or 20s, and might not be in the 17-19 range because why would you roll bless then)
                #I could actually go through each of these and (using the stats sheets) recover the 4possible d20 rolls if the total value is present (and just not the d20 roll)
            else: 
                print("rolled a " + str(roll) + " but with unknown d4 roll")
                #I might just treat these as MCAR, or I could do a uniform distribution over d4 rolls

        if roll == 'Unknown':
            if ('disadvantage' in notes) or ('disdavantage' in notes): #there are 2 typos in the dataset
                disadv += 1
                nextRoll = Laura[i+1, 5] #I'm assuming the disregarded roll is always the first of a pair in the recordkeeping, which might not always hold
                #we know this roll was between nextRoll and 20, inclusive - not unreasonable to take a uniform distribution of that
            elif 'advantage' in notes:
                adv += 1
                nextRoll = Laura[i+1, 5] #I'm assuming the disregarded roll is always the first of a pair in the recordkeeping, which might not always hold
                #we know this roll was between 1 and nextRoll, inclusive - not unreasonable to take a uniform distribution of that
                #possible problem: what if bless also, or fortune's favour
                #       answer: that's going to affect like 2 rolls. Ok to disregard for now, and track down manually later.
            else: 
                #pass
                #print(i)
                print(notes) #will have to check for advantage, disadvantage, fortune's favour, luck
        elif roll == '--':
            pass
            #print(Laura[i, 9])
            #pass #we could analyze damage, healing here
        else:
            #print(roll)
            # roll = float(roll)
            # if (np.isnan(roll)):
            #     missingData += 1
            # else: 
            tidyDiceRolls.append(roll) # will have to check for fortune's favour, luck, bless
    #print(LauraDiceRolls)
LauraDiceRolls = np.array(tidyDiceRolls, dtype=float)
LauraDiceRolls = LauraDiceRolls[~np.isnan(LauraDiceRolls)]
print(adv)
print(disadv)
print(plusd4)
print(LauraDiceRolls.shape)
print(np.mean(LauraDiceRolls)) #gotta track down adv, disadv, etc
#print(Laura[:,5])