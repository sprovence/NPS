# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 09:54:53 2020

@author: sydne
"""
import numpy as np
import pandas as pd
from collections import defaultdict

def remove_words(string):
    words = string.split()
    removewords = ['RAW', 'ADJUSTED', 'ADJ', 'TRAFFIC', 'COUNT', 'AT', 'TOTAL', 'COUNTER']
    words = [word for word in words if word not in removewords]
    return ' '.join(words)

def find_unit_places(unit_code, places):
    unit_code = unit_code.upper()
    return places[places['parkCode'].str.upper() == unit_code]

def match_locations_in_unit(CounterLocation, UnitPlaces):
    words = CounterLocation.upper().split()
    match = defaultdict(int)
    closest_match = ''
    closest_match_score = 0
    for word in words:
        for place in UnitPlaces['name']:
            if word in place.upper().split():
                match[place.upper()] += 1
                if match[place.upper()] > closest_match_score:
                    closest_match = place
                    closest_match_score = match[place.upper()]
                
    if closest_match_score == 0:
        return 0, 0
    else:
        place_index = UnitPlaces[UnitPlaces['name'] == closest_match].index[0]
        if ~np.isnan(UnitPlaces.at[place_index, 'latitude']) and ~np.isnan(UnitPlaces.at[place_index, 'longitude']):
            return  UnitPlaces.at[place_index, 'latitude'], UnitPlaces.at[place_index, 'longitude']
        else:
            return 0, 0
    
def getPublicUse(year):
    public_use = pd.read_csv('PublicUseArea.csv', sep=',', index_col=0, 
                              header=0)
    public_use = public_use[public_use['Year']==year]
    public_use['VisitorDensity'] = public_use['RecreationVisits'] / public_use['Gross Acres ' + str(year)]
    return public_use

def add_usage_to_geojson(boundaries, publicUse):
    month2days = {1:31, 2:28, 3:31, 4: 30, 5:31, 6:30, 7:31, 8:31, 9:30,
                      10:31, 11:30, 12:31}
    
    # Initialize a monthly features dictionary
    for i, park in enumerate(boundaries['features']):
        boundaries['features'][i]['properties']['Park Name'] = boundaries['features'][i]['properties']['UNIT_NAME']
        boundaries['features'][i]['properties']['Park Type'] = boundaries['features'][i]['properties']['UNIT_TYPE']
    
    # Iterate through each month of the yera to get the public use summary
    # for that month
    for month in range(1,13):
        publicUse_month = publicUse[publicUse['Month']==month]
        days = month2days[month]
        # Iterate through every boundary file and add the visitor use data to its
        # properties    
        for i, park in enumerate(boundaries['features']):
            unit_code = park['properties']['UNIT_CODE']
            # match the unit code to the public use unit code
            index = publicUse_month[publicUse_month['UnitCode']==unit_code].index[0]
            visitors = publicUse_month.at[index,'RecVisitors2018']
            visitor_density = publicUse_month.at[index,'VisitorDensity2018']
            acres = publicUse_month.at[index, 'Gross Acres 2018']
        
            boundaries['features'][i]['properties']['Average Daily Visitors ' + str(month)] = float(visitors/days)
            if visitor_density == 0.:
                boundaries['features'][i]['properties']['Average Acres Available per Visitor ' + str(month)] = acres
            else:
                boundaries['features'][i]['properties']['Average Acres Available per Visitor ' + str(month)] = float(1.0/(visitor_density/days))
    return boundaries