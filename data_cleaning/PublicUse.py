# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 21:00:51 2020
Script to clean the public use data into useable, compact, single-.csv file
format.
@author: sydne
"""

import pandas as pd
import numpy as np

public_use_yrs = ['1979', '1980-1984', '1985-1989', '1990-1994', '1995-1999', 
                    '2000-2004', '2005-2009', '2010-2018']

#acreage = pd.read_csv('Acreage.csv', sep=',', usecols=list(range(0,8)), header=0)
# Read first .csv to get header names
public_use_data = pd.read_csv('Public Use Statistics.csv', sep=',', index_col=0, 
                              header=0, usecols=list(range(18)), thousands=',')
    
parkTypes = ['National Parkway', 'National Park', 'National Recreation Area', 
              'National Lakeshore', 'National Monument', 'National Preserve', 
              'National River', 'National Seashore', 
              'National Reserve', 'National Wild & Scenic River', 
              'National Military Park']
public_use_data = public_use_data[public_use_data['ParkType'].isin(parkTypes)]
public_use_data = public_use_data[public_use_data['Year']==2018]

public_use = pd.merge(left=public_use_data[['ParkName', 'UnitCode', 'ParkType', 'State', 'Year', 'Month', 'RecreationVisits']], 
                right=acreage[['Gross Acres 2018', 'Gross Acres 2017', 'Gross Acres 2016', 'Gross Acres 2015', 'Gross Acres 2014', 'Unit Code']], 
                how='inner', left_on='UnitCode', right_on='Unit Code')
public_use.to_csv('PublicUseArea.csv')

public_use['VisitorDensity18'] = public_use[public_use['Year']==2018]['RecreationVisits'] / public_use['Gross Acres 2018']

public_use_2018 = public_use_2018.sort_values(by='VisitorDensity', ascending=False)
public_use_2018 = public_use_2018[public_use_2018['Gross Acres 2018'] > 100]
test = public_use_2018[public_use_2018['ParkType'] == 'National Park']

# Save public use data
#public_use_data.to_csv('nps_public_use.csv')

"""
# Load the boundaries data to calculate the area
fname = "nps_boundary.shp"
boundaries = gpd.read_file(fname)
#boundaries = boundaries.to_crs("epsg:4326")
boundaries['area_mi'] = boundaries['Shape_Area'] * 3768.2403016737157

# Merge the park boundaries on the unit code
public_use_data = pd.merge(public_use_data, boundaries[['Shape_Area', 'UNIT_CODE']], 
                           left_on='UnitCode', right_on='UNIT_CODE')

# Calculate the visitor use density
public_use_data['VistorDensity'] = public_use_data['RecreationVisits'] / public_use_data['Shape_Area']
public_use_data = public_use_data.sort_values(by=['VistorDensity'], ascending=False)
public_use_data = public_use_data.drop(columns=['Shape_Area', 'UNIT_CODE'], axis=1)
public_use_data = public_use_data[public_use_data['ParkType']=='National Park']
public_use_data.sort_values(by=['RecreationVisits'], ascending=True)

#clean_data.to_csv('nps_traffic_clean.csv')
"""





