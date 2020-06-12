# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 22:08:30 2020

@author: sydne
"""
import pandas as pd
from collections import defaultdict
import re

def set_unit_code_index(df, parks):
    parkNames = df['Area Name']
    unitCodes = []
    for name in parkNames:
        words = name.upper()
        words = re.split(' |-',words)
        # Only search the correct park type subset
        if 'NP' in words:
            subset = parks[parks['designation']=='National Park']
            words.remove('NP')
        elif 'NRA' in words:
            subset = parks[parks['designation']=='National Recreation Area']
            words.remove('NRA')
        elif 'NHP' in words:
            subset = parks[parks['designation']=='National Historical Park']
            words.remove('NHP')
        elif 'NM' in words:
            subset = parks[parks['designation']=='National Monument']
            words.remove('NM')
        elif 'NMEM' in words:
            subset = parks[parks['designation']=='National Memorial']
            words.remove('NMEM')
        else:
            subset = parks.copy()
            
        match = defaultdict(int)
        closest_match = ''
        closest_match_score = 0
        for word in words:
            if any(subset['name'].str.contains(word, case=False)) and (len(word) > 2):
                keys = subset[subset['name'].str.contains(word, case=False)]['parkCode'].str.upper()
                for key in keys:
                    index = subset[subset['parkCode']==key.lower()].index[0]
                    key_name = parks.loc[index, 'fullName'].upper().split()
                    if word in key_name:
                        match[key] += 2
                    else:
                        match[key] += 1
                        
                    if match[key] > closest_match_score:
                        closest_match = key
                        closest_match_score = match[key]
        unitCodes.append(closest_match)
        
    df['UnitCode'] = unitCodes
    df = df.set_index('UnitCode')
    return df

# Open parks.txt to get park names and codes key
#parks = pd.read_json('parks.txt')
#parks = parks.replace(regex='&#333;', value='o')
#parks = parks.replace(regex='&#257;', value='a')
#parks = parks.replace(regex='á', value='a')
#parks = parks.replace(regex='&#241;', value='n')

# Create a base acreage dataframe
base = 'NPS-Acreage-12-31-'
data = pd.read_excel(base + '2019.xlsx', skiprows=1)
acreage = data[['Area Name', 'State', 'NPS Fee Acres']]
acreage = acreage.rename(columns={'NPS Fee Acres': 'FeeAcres2019'})
acreage = acreage.dropna(axis=0)

# Use the park unit codes as an index
acreage = set_unit_code_index(acreage, parks)
"""
parkNames = acreage['Area Name']
unitCodes = []
for name in parkNames:
    words = name.upper()
    words = re.split(' |-',words)
    match = defaultdict(int)
    closest_match = ''
    closest_match_score = 0
    for word in words:
        if any(parks['name'].str.contains(word, case=False)):
            keys = parks[parks['name'].str.contains(word, case=False)]['parkCode'].str.upper()
            for key in keys:
                match[key] += 1
                if match[key] > closest_match_score:
                    closest_match = key
                    closest_match_score = match[key]
    unitCodes.append(closest_match)
    
acreage['UnitCode'] = unitCodes
acreage = acreage.set_index('UnitCode')


for year in range(2018, 1997, -1):
    data = pd.read_excel(base + str(year) + '.xlsx', skiprows=1)
    if 'NPS Fee Acres' in data.columns:
        data = data[['Area Name', 'State', 'NPS Fee Acres']]
    elif 'Fee Acres' in data.columns:
        data = data[['Area Name', 'State', 'Fee Acres']]
    
    data = data.dropna(axis=0)
    # Set the index of the df as the park unitcodes
    data = set_unit_code_index(data, parks)
    
    # Merge the dataframe with the total acreage df
    if 'NPS Fee Acres' in data.columns:
        acreage = acreage.merge(data['NPS Fee Acres'], how='outer', 
                                left_index=True, right_index=True)
        acreage.rename(columns={'NPS Fee Acres':'FeeAcres'+str(year)})
    elif 'Fee Acres' in data.columns:
        acreage = acreage.merge(data['Fee Acres'], how='outer', 
                                left_index=True, right_index=True)
        acreage.rename(columns={'Fee Acres':'FeeAcres'+str(year)})
    
    test = pd.concat([acreage, data['NPS Fee Acres']], join='outer', axis=1)



#for yr in range(2019, 1997, -1):
#    data = pd.read_excel(base + '1997.xlsx', skiprows=1)
"""