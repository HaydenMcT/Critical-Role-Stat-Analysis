import pandas as pd
import numpy as np
import re

X = np.array(pd.read_csv("JesterRollsManualDiceRanges.csv")) #load data

timestamp_idx = 3
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
    if rollType == 'hit points' or rollType == 'hit dice': #Jester rolls a d8 when deciding how many hit points to gain/recover when leveling up or using hit dice
        return False
    if rollType == 'other': # the "other" category often refers to non d20 rolls 
                            # (because most d20 rolls correspond to easily classifiable types of rolls: 
                            #  usually specific types of ability checks, saving throws, or attack rolls)
                            # We can likely disregard the d20 rolls in this column without introducing any bias.
                            # There is also no easy way to differentiate between "other" d20 rolls and non d20 rolls
                            # without a detailed parsing of the notes column
        return False
    return True

# Given a discrete distribution across te numbers lower to upper, inclusive, 
# updates roll tally with the associated probabilities
# defaults to assuming a uniform distribution
def updateTallyWithDist(lower, upper, pmf= lambda i: 1/(upper_bound - lower_bound + 1)):
    #for each of the possible values, add the pmf to the roll tally:
    for roll_val in np.arange(lower_bound, upper_bound+1): #lists the numbers from lower_bound to upper_bound, inclusive
        roll_tally[roll_val - 1] += pmf(roll_val)

#use regex to recover the lower and upper bound on the dice roll values, assuming they were entered in the format '[lower,upper]'
def recoverBoundsFromRollRange(roll_range):
    first_entry = re.search(r'(?<=\[).+,', roll_range).group(0) # matches to the first entry in the roll range (the range is of the form '[a,b]', and so the result here is 'a,' where a is the number we want)
    lower_bound = int(first_entry[:-1]) #remove the comma, then parse value as integer
    second_entry = m = re.search(r'(?<=,).+\]',roll_range).group(0) #matches to the second entry in the roll range (the range is of the form '[a,b]', and so the result here is 'b]' where b is the number we want)
    upper_bound = int(second_entry[:-1]) #remove the bracket, then parse value as integer
    return lower_bound, upper_bound

d20_rolls = filterToD20Rolls(X)
print(d20_rolls.shape)

for i, roll in enumerate(d20_rolls): #each row of the dataset represents information about a single dice roll
    roll_range = str(roll[nat_roll_range_idx])
    if roll_range != 'nan':
        #if a roll range is specified, parse the lower and upper bounds
        lower_bound, upper_bound = recoverBoundsFromRollRange(roll_range)
        # when roll_range is specified, we take it to denote a discrete uniform distribution on the possible dice roll values ,and update tallies accordingly
        updateTallyWithDist(lower_bound, upper_bound)
    else: 
        natural_roll = str(roll[natural_roll_idx])

        #if we're given a valid natural roll, we parse that as such
        if natural_roll != 'nan' and natural_roll.lower() != 'unknown':
            natural_roll = int(natural_roll)
            roll_tally[natural_roll-1] += 1

        else:
            #if we don't know a value, we may be able to infer it
            notes = str(roll[notes_idx]).lower()
            time = str(roll[timestamp_idx])
            if 'advantage' in notes: # disadvantage and advantage (which both contain the string 'advantage' and are therefore covered in this condition)
                                     # cause players to roll a pair of dice, disregarding one of the two rolls. Unfortunately, although the dataset 
                                     # marks when a roll was disregarded due to advantage/disadvantage, it doesn't always tell us which other roll
                                     # was part of the pair (the roll above or the roll below). We can infer this, though, by looking at timestamps
                roll_above = d20_rolls[i-1]
                roll_below = d20_rolls[i+1]
                if str(roll_above[timestamp_idx]) == time: #if two rolls were made at the same time, we assume that they are part of the same advantage/disadvantage roll
                    paired_roll = roll_above
                else:
                    paired_roll = roll_below
                    if str(paired_roll[timestamp_idx]) != time:
                        print('Error! No paired roll found! ' + str(paired_roll))
                
                if 'disadvantage' in notes: 
                    # for disadvantage, the higher of the two rolls is disregarded, so we make the assumption that the higher roll is
                    # uniformly distributed across all values >= the paired roll. One slight issue with this assumption is that it's
                    # possible that if the player rolled a 20 or a 1 on the disregarded die they would still have mentioned that 
                    # (so the fact that this value is unknown might make it less likely that the number is a 1 or a 20)
                    upper_bound = 20
                    lower_bound = str(paired_roll[natural_roll_idx]).lower()
                    if lower_bound != 'nan' and lower_bound != 'unknown':
                        lower_bound = int(lower_bound)
                        updateTallyWithDist(lower_bound, upper_bound)
                    else:
                        #this is a trickier case: we found the paired roll, but that paired roll's value is unknown

                        # If we have a roll range, then we can still leverage the information we have about that roll
                        paired_roll_range = str(paired_roll[nat_roll_range_idx])
                        if paired_roll_range != 'nan':
                            paired_roll_lower_bound, paired_roll_upper_bound = recoverBoundsFromRollRange(paired_roll_range)
                            # we assume that the paired roll is uniformly distributed from paired_roll_lower_bound to 
                            # paired_roll_upper_bound, inclusive.
                            # So we consider as equally likely all of the possible values for our paired roll, and update our tallies accordingly
                            # recall that for the disadvantage case the paired roll is a lower bound on the unknown roll
                            for lower_bound in np.arange(paired_roll_lower_bound, paired_roll_upper_bound + 1):
                                probability_of_lower_bound = 1/(paired_roll_upper_bound - paired_roll_lower_bound + 1)
                                #when we update, we have to adjust the pmf based on the probability of the particular lower bound case we're considering.
                                updateTallyWithDist(lower_bound, upper_bound, pmf = lambda i: probability_of_lower_bound * 1/(upper_bound - lower_bound + 1))
                        else:
                            # If we don't know the roll value and also don't have a roll range, then there's not a lot 
                            # we can do pending manually fixing the entry, or disregarding the roll altogether 
                            # but at least we aren't counting either roll in the pair (so we're less likely to introduce bias)
                            print("Missing data: " + str(roll))

                else:
                    # for advantage, the lower of the two rolls is disregarded, so we assume the lower, unknown roll is uniformly distributed
                    # across all values <= the paired, known roll. The same issue as for disadvantage does hold, however: we are disregarding the
                    # possibility that a player might have reported the roll on the disregraded die if the number were particularly high or particularly low
                    # - so the fact that this data is unknown might give us more information than just this uniform distribution.
                    upper_bound = str(paired_roll[natural_roll_idx]).lower()
                    lower_bound = 1
                    if upper_bound != 'nan' and upper_bound != 'unknown':
                        upper_bound = int(upper_bound)
                        updateTallyWithDist(lower_bound, upper_bound)
                    else:
                        # again a trickier case: we found the paired roll, but that paired roll's value is unknown

                        # If we DO have a roll range, then we can still leverage the information we have about that roll
                        paired_roll_range = str(paired_roll[nat_roll_range_idx])
                        if paired_roll_range != 'nan':
                            paired_roll_lower_bound, paired_roll_upper_bound = recoverBoundsFromRollRange(paired_roll_range)
                            # we assume that the paired roll is uniformly distributed from paired_roll_lower_bound to 
                            # paired_roll_upper_bound, inclusive.
                            # So we consider as equally likely all of the possible values for our paired roll, and update our tallies accordingly
                            # recall that for the advantage case the paired roll is an upper bound on the unknown roll
                            for upper_bound in np.arange(paired_roll_lower_bound, paired_roll_upper_bound + 1):
                                probability_of_upper_bound = 1/(paired_roll_upper_bound - paired_roll_lower_bound + 1)
                                #when we update, we have to adjust the pmf based on the probability of the particular upper bound case we're considering.
                                updateTallyWithDist(lower_bound, upper_bound, pmf = lambda i: probability_of_upper_bound * 1/(upper_bound - lower_bound + 1))
                        else:
                            # If we don't know the roll value and also don't have a roll range, then there's not a lot 
                            # we can do pending manually fixing the entry, or disregarding the roll altogether 
                            # but at least we aren't counting either roll in the pair (so we're less likely to introduce bias)
                            print("Missing data: " + str(roll))
                
            else:
                #if the notes don't mention advantage and the natural roll is missing, we may have to disregard the results or fill them in manually
                print("Missing data: " + str(roll))

print(roll_tally)
print(np.sum(roll_tally))

#TODO: "Run Chi Sq goodness of fit test against a discrete uniform distribution"