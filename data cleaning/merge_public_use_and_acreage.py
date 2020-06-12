# -*- coding: utf-8 -*-
"""
Created on Sun May 10 18:21:15 2020
Merge Public use 2018 with acreage data
@author: sydne
"""
import pandas as pd

# Open the 2018 Public use file
publicUse = pd.read_csv('Public Use Statistics 2018.csv', index_col=0)

acreage = pd.read_csv('./Acreage/Acreage.csv')

# Merge on unit code

publicUse = pd.merge(left=publicUse, right=acreage[['Unit Code', 'Gross Acres 2018']],
                how='left', left_on='UnitCode', right_on='Unit Code')

# Drop the extra unit code column
publicUse = publicUse.drop(columns=['UnitCode'])

# Calculate the visitor density for 2018
publicUse['VisitorDensity2018'] = publicUse['RecVisitors2018'] / publicUse['Gross Acres 2018']

# Save the plot
publicUse.to_csv('Public Use Statistics 2018.csv')