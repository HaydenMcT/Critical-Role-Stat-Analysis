import pandas as pd
import numpy as np

X = np.array(pd.read_csv("AllRolls.csv")) #load data
X = X[:,2:] #remove the first column (which is just a row number)

#given the text for the "Type of Roll" column, determines whether the roll described is a d20 roll
def isD20Roll(rollType):
    if rollType == 'healing': #healing rolls use d10's, d8's, d6's, and d4's, never any other type of die (to my knowledge)
        return False
    if rollType == 'damage': #damage rolls are never done with d20's
        return False
    if rollType == 'other': # the "other" category often refers to non d20 rolls 
                            # (because most d20 rolls correspond to easily classifiable types of rolls: 
                            #  usually specific types of ability checks, saving throws, or attack rolls)
                            # We can likely disregard the d20 rolls in this column without introducing any bias.
                            # There is also no easy way to differentiate between "other" d20 rolls and non d20 rolls
                            # without a detailed parsing of the notes column
        return False
    return True

#Laura rolls for 3 characters on Critical Role, Vex'ahlia, Jester, and Trinket
Laura_idcs = np.arange(X.shape[0])[np.any([X[:,2] == 'Vex\'ahlia', X[:,2] == "Jester", X[:, 2] == "Trinket"], axis=0)]
#TODO: filter out episodes where Laura was absent from the game, and someone else rolled for her

Laura = X[Laura_idcs]

tidyDiceRolls = []
adv = 0
adv_idcs = []
disadv = 0
disadv_idcs = []
plusd4 = 0
missingData = 0
suspicious_idcs = [] #Indices for possible data misentries, things that require manual inspection
rolls = np.zeros(21)
for i, roll in enumerate(Laura[:,5]):
    d4 = False
    rollType = str(Laura[i, 3]).lower()
    notes = str(Laura[i, 9]).lower()
    if not isD20Roll(rollType):
        pass
    else: 
        #determine whether the roll is a d20 with an additional d4
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
            if ('disadvantage' in notes) or ('disdavantage' in notes): #there are 2 typos in the dataset, hence the check for disdavantage
                disadv += 1
                adv_idcs.append(Laura_idcs[i])
                #nextRoll = Laura[i+1, 5] #I'm assuming the disregarded roll is always the first of a pair in the recordkeeping, which might not always hold - it is sometimes the previous one
                #we know this roll was between nextRoll and 20, inclusive - not unreasonable to take a uniform distribution of that
            elif 'advantage' in notes:
                adv += 1
                adv_idcs.append(Laura_idcs[i])
                #nextRoll = Laura[i+1, 5] #I'm assuming the disregarded roll is always the first of a pair in the recordkeeping, which might not always hold
                #we know this roll was between 1 and nextRoll, inclusive - not unreasonable to take a uniform distribution of that
                #possible problem: what if bless also, or fortune's favour
                #       answer: that's going to affect like 2 rolls. Ok to disregard for now, and track down manually later.
            else: 
                pass
                #print(i)
                #print(notes) #will have to check for advantage, disadvantage, fortune's favour, luck
        elif roll == '--':
            pass
            #print(Laura[i, 9])
            #pass #we could analyze damage, healing here
        else:
            roll = float(roll)
            if (np.isnan(roll)):
                missingData += 1
            else: 
                if int(roll) > 20: 
                   suspicious_idcs.append(Laura_idcs[i])
                else:
                    rolls[int(roll)] += 1
            tidyDiceRolls.append(roll) # will have to check for fortune's favour, luck, bless
    #print(LauraDiceRolls)
LauraDiceRolls = np.array(tidyDiceRolls, dtype=float)
LauraDiceRolls = LauraDiceRolls[~np.isnan(LauraDiceRolls)]
print(adv)
print(disadv)
print(plusd4)
print(LauraDiceRolls.shape)
print(np.mean(LauraDiceRolls)) #gotta track down adv, disadv, etc
print(adv_idcs)
#print(Laura[:,5])