# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 16:10:21 2020

@author: sydne
"""
import pandas as pd
import geopandas as gpd
publicUse = getPublicUse(2018)

# Import the shape file
fname = "nps_boundary.shp"
boundaries = gpd.read_file(fname)

public_use = pd.read_csv('Public Use Statistics.csv', sep=',', index_col=0, 
                              header=0, usecols=list(range(18)), thousands=',')
parkTypes = ['National Parkway', 'National Park', 'National Recreation Area', 
              'National Lakeshore', 'National Monument', 'National Preserve', 
              'National River', 'National Seashore', 
              'National Reserve', 'National Wild & Scenic River', 
              'National Military Park']
publicUse = public_use[public_use['ParkType'].isin(parkTypes)]
publicUse = publicUse[publicUse['Year'] == 2018]
publicUse = publicUse.rename(columns={'RecreationVisits':'RecVisitors2018'})

publicUse.to_csv('Public Use Statistics 2018.csv')

#traffic_data = pd.read_csv('nps_traffic.csv', index_col=0)
unit_codes = publicUse['UnitCode'].unique()

# Get rid of boundaries for parks with no public use data
boundaries = boundaries[boundaries['UNIT_CODE'].isin(unit_codes)]

"""
# Merge the boundaries dataframe with the public use data
left = boundaries[['UNIT_CODE', 'UNIT_NAME', 'geometry']]
right = publicUse[['ParkName', 'UnitCode', 'ParkType', 'Month', 
                   'RecVisitors2018']]
merged_bounds = left.merge(right=right, how='outer', right_on='UnitCode', 
                           left_on='UNIT_CODE')
merged_bounds = merged_bounds.drop(columns=['UNIT_CODE', 'UNIT_NAME'])
"""
# Convert the geopandas file to json
boundaries.to_file("nps_boundary.geojson", driver='GeoJSON')
