import pandas as pd
import numpy as np
import re

X = np.array(pd.read_csv("JesterRollsManualDiceRanges.csv")) #load data

roll_type_idx = 5
natural_roll_idx = 7
notes_idx = 11
nat_roll_range_idx = 12
roll_tally = np.zeros(20) #roll_tally[x - 1]/np.sum(roll_tally) represents the proportion of rolls that had value x (x in [1,20])

#given a dataset of rolls, filters out all rolls which we do not know for sure are d20 rolls
def filterToD20Rolls(rolls):
    validRows = []
    for i, roll in enumerate(rolls):
        roll_type = roll[roll_type_idx].lower()
        if isD20Roll(roll_type):
            validRows.append(i)
    return rolls[validRows, :]

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


d20_rolls = filterToD20Rolls(X)

for roll in d20_rolls: #each row of the dataset represents information about a single dice roll
    roll_range = str(roll[nat_roll_range_idx])
    if roll_range != 'nan':
        #use regex to recover the lower and upper bound on the dice roll values, assuming they were entered in the format '[lower,upper]'
        first_entry = re.search(r'(?<=\[).+,', roll_range).group(0) #matches to the first entry in the roll range (the range is of the form '[a,b]', and so the result here is 'a,' where a is the number we want)
        lower_bound = int(first_entry[:-1]) #remove the comma, then parse value as integer
        second_entry = m = re.search(r'(?<=,).+\]',roll_range).group(0) #matches to the second entry in the roll range (the range is of the form '[a,b]', and so the result here is 'b]' where b is the number we want)
        upper_bound = int(second_entry[:-1]) #remove the bracket, then parse value as integer

        # when roll_range is specified, we take it to denote a discrete uniform distribution on the possible dice roll values. 
        # So the pmf for each value within the range (inclusive of the bounds) is:
        pmf = 1/(upper_bound - lower_bound + 1)

        #for each of the possible values, add the pmf to the roll tally:
        for roll_val in np.arange(lower_bound, upper_bound+1): #lists the numbers from lower_bound to upper_bound, inclusive
            roll_tally[roll_val - 1] += pmf
    else: 
        natural_roll = str(roll[natural_roll_idx])
        if natural_roll != 'nan' and natural_roll.lower() != 'unknown':
            if natural_roll.lower() == 'nat1':
                natural_roll = 1
            elif natural_roll.lower() == 'nat20':
                natural_roll = 20
            else: 
                natural_roll = int(natural_roll)
            if natural_roll > 20: 
                print("error with roll! value above 20!")
                print("row num is" + str(roll[0]))
            roll_tally[natural_roll-1] += 1
        else: 
            pass #handle advantage

print(roll_tally)

# tidyDiceRolls = []
# adv = 0
# adv_idcs = []
# disadv = 0
# disadv_idcs = []
# plusd4 = 0
# missingData = 0
# suspicious_idcs = [] #Indices for possible data misentries, things that require manual inspection
# rolls = np.zeros(21)
# for i, roll in enumerate(Laura[:,natural_roll_idx]):
#     d4 = False
#     rollType = str(Laura[i, 3]).lower()
#     notes = str(Laura[i, 9]).lower()
#     if not isD20Roll(rollType):
#         pass
#     else: 
#         #determine whether the roll is a d20 with an additional d4
#         if ('bless' in notes and 'blessing' not in notes) or 'guidance' in notes:
#             plusd4 += 1
#             #print(notes)
#             if (roll == 'Unknown' or np.isnan(float(roll))):
#                 missingData += 1
#                 #print("disregarded a d4 roll because bless roll was unknown")
#                 #I think these can be treated as MCAR (although they probably aren't ones or 20s, and might not be in the 17-19 range because why would you roll bless then)
#                 #I could actually go through each of these and (using the stats sheets) recover the 4possible d20 rolls if the total value is present (and just not the d20 roll)
#             else: 
#                 print("rolled a " + str(roll) + " but with unknown d4 roll")
#                 #I might just treat these as MCAR, or I could do a uniform distribution over d4 rolls

#         if roll == 'Unknown':
#             if ('disadvantage' in notes) or ('disdavantage' in notes): #there are 2 typos in the dataset, hence the check for disdavantage
#                 disadv += 1
#                 adv_idcs.append(Laura_idcs[i])
#                 #nextRoll = Laura[i+1, 5] #I'm assuming the disregarded roll is always the first of a pair in the recordkeeping, which might not always hold - it is sometimes the previous one
#                 #we know this roll was between nextRoll and 20, inclusive - not unreasonable to take a uniform distribution of that
#             elif 'advantage' in notes:
#                 adv += 1
#                 adv_idcs.append(Laura_idcs[i])
#                 #nextRoll = Laura[i+1, 5] #I'm assuming the disregarded roll is always the first of a pair in the recordkeeping, which might not always hold
#                 #we know this roll was between 1 and nextRoll, inclusive - not unreasonable to take a uniform distribution of that
#                 #possible problem: what if bless also, or fortune's favour
#                 #       answer: that's going to affect like 2 rolls. Ok to disregard for now, and track down manually later.
#             else: 
#                 pass
#                 #print(i)
#                 #print(notes) #will have to check for advantage, disadvantage, fortune's favour, luck
#         elif roll == '--':
#             pass
#             #print(Laura[i, 9])
#             #pass #we could analyze damage, healing here
#         else:
#             roll = float(roll)
#             if (np.isnan(roll)):
#                 missingData += 1
#             else: 
#                 if int(roll) > 20: 
#                    suspicious_idcs.append(Laura_idcs[i])
#                 else:
#                     rolls[int(roll)] += 1
#             tidyDiceRolls.append(roll) # will have to check for fortune's favour, luck, bless
#     #print(LauraDiceRolls)
# LauraDiceRolls = np.array(tidyDiceRolls, dtype=float)
# LauraDiceRolls = LauraDiceRolls[~np.isnan(LauraDiceRolls)]
# print(adv)
# print(disadv)
# print(plusd4)
# print(LauraDiceRolls.shape)
# print(np.mean(LauraDiceRolls)) #gotta track down adv, disadv, etc
# print(adv_idcs)
# #print(Laura[:,5])