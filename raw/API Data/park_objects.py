# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 14:29:50 2020
Use .txt files from the NPS API to create a database of features within 
national parkland, along with their GPS coordinates
@author: sydne
"""
import pandas as pd
import dill

places = pd.read_json('places.txt')
campgnds = pd.read_json('campgrounds.txt')
parks = pd.read_json('parks.txt')
events = pd.read_json('events.txt')
activities = pd.read_json('alerts.txt')
vcenters = pd.read_json('visitorcenters.txt')
    
# Create an overall dataframe using the parks as the main key
# Recast dataframes only to relevant columns
campgnds = campgnds[['name', 'latLong', 'parkCode']]
vcenters = vcenters[['name', 'latitude', 'longitude', 'parkCode']]

# Split latLong into latitude and longitude columns
split_data = campgnds['latLong'].str.split(", ")
data = split_data.to_list()
lats = np.zeros((len(data), 1))
longs = np.zeros((len(data), 1))
for i in range(len(data)):
    if len(data[i]) > 1:
        lats[i] = float(data[i][0].lstrip('{lat:'))
        longs[i] = float(data[i][1].lstrip('lng:').rstrip('}'))
    else:
        lats[i] = np.nan
        longs[i] = np.nan
campgnds['latitude'] = lats
campgnds['longitude'] = longs
campgnds = campgnds.drop(columns='latLong', axis=1)

# Add an additional column specifying type of location
campgnds['type'] = ['CAMPGROUND']*len(campgnds)
vcenters['type'] = ['VISITORCENTER']*len(vcenters)

places = pd.concat([campgnds, vcenters], axis=0)

dill.dump(places, open('nps_places.pkd', 'wb'))