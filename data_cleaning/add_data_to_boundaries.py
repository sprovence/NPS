# -*- coding: utf-8 -*-
"""
Created on Sun May 10 18:18:04 2020
Add the acreage, number of visitors, and visitor density to the boundary.json
file
@author: sydne
"""

import pandas as pd
import geojson
"""
# Open the boundaries file
boundaries_fname = 'nps_boundary.geojson'
    with open(boundaries_fname) as file:
        boundaries = geojson.load(file)
        
# Open the 2018 Public use file
publicUse = pd.read_csv('Public Use Statistics 2018.csv', index_col=0)
"""

def add_usage_to_geojson(boundaries, publicUse, month):
    if month:
        publicUse = publicUse[publicUse['Month']==month]
        
    # Iterate through every boundary file and add the visitor use data to its
    # properties    
    for i, park in enumerate(boundaries['features']):
        unit_code = park['properties']['UNIT_CODE']
        # match the unit code to the public use unit code
        index = publicUse[publicUse['UnitCode']==unit_code].index[0]
        visitors = publicUse.at[index,'RecVisitors2018']
        visitor_density = publicUse.at[index,'VisitorDensity2018']
        
        boundaries['features'][i]['properties']['Visitors'] = visitors
        boundaries['features'][i]['properties']['Visitor Density'] = visitor_density
        
    return boundaries


test = add_usage_to_geojson(boundaries, publicUse, month=7)
    
