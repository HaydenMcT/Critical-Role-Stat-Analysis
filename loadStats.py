import pandas as pd
import numpy as np
import argparse
#TODO: read in data via url 
parser = argparse.ArgumentParser(description="Load a set of critical roll results (either Wildemount or Tal'Dorei) and convert it to csv. Data first needs to be downloaded and placed in this folder")
parser.add_argument("campaign", choices=["1", "2"], help="Which campaign for which to convert the data into a csv file")
arguments = parser.parse_args()
if arguments.campaign == "2": 
    #requires you to put the .xlsx file into the common data folder
    data = pd.read_excel('AllRollsWildemount.xlsx', sheet_name=None)
    data.pop('Time Shifts') # One of the sheets in the Wildemount roll tracking at https://docs.google.com/spreadsheets/d/1FFuw5c6Hk1NUlHv2Wvr5b9AElLA51KtRl9ZruPU8r9k/edit#gid=0 
                            # tracks information unrelated to rolls; we remove this row for our purposes. 

    X = np.zeros((1,10)) #create a (dummy) first row for X to begin accumulating data
    for value in data.values():
        toAdd = np.array(value)
        if toAdd.shape[1] == 11: #get rid of the "Old Time" column present in some sheets
            toAdd = np.delete(toAdd, 1, 1)
        X = np.concatenate((X, toAdd))
    X = X[1:,:] #remove the (dummy) first row
    X = pd.DataFrame(X, columns = ("Episode", "Time", "Character", "Type of Roll", "Total Value", "Natural Value", "Crit?", "Damage Dealt", "# Kills", "Notes"))
    X.to_csv("AllRollsWildemount.csv")
elif arguments.campaign == "1":
    data = pd.read_excel('AllRollsTalDorei.xlsx', sheet_name=None)
    data.pop('Sheet96') #For some as-yet-unexplained reason, there's an extra sheet by this name (which we don't want) that shows up when reading the excel file
    X = np.zeros((1,10)) #create a (dummy) first row for X to begin accumulating data
    #print(data)
    for value in data.values():
        toAdd = np.array(value)
        print(toAdd)
        print(toAdd.shape)
        if toAdd.shape[1] > 10: #get rid of the "Non-Roll Kills" information
            toAdd = toAdd[:,:10]
        if toAdd.shape[1] < 10: #some episodes, like 14, have no Damage Dealt or Number of Kills columns (because the session was all RP)
            toAdd = np.insert(toAdd, (7,7), float('NaN'), axis=1)
            print(toAdd)
        X = np.concatenate((X, toAdd))
    X = X[1:,:] #remove the (dummy) first row
    X = pd.DataFrame(X,  columns = ("Episode", "Time", "Character", "Type of Roll", "Total Value", "Natural Value", "Crit?", "Damage Dealt", "# Kills", "Notes"))
    X.to_csv("AllRollsTalDorei.csv")


