# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 07:55:18 2020
Script to merge Traffic Counts into a single .csv
@author: sydne
"""

import pandas as pd
import numpy as np
from bokeh.plotting import figure, output_file, show
import dill
from data_cleaning_utils import *
import requests
import json

"""
traffic_counts_yrs = ['1985-1989', '1990-1994', '1995-1999','2000-2004', 
                      '2005-2009', '2010-2014', '2015-2019']
# Open the first .csv file
traffic_data = pd.read_csv('Traffic Counts 1985-1989.csv', sep=',', header=2, 
                           usecols=list(range(8)), thousands=',')
# Merge all of the .csvs into a single dataframe.
for yr in traffic_counts_yrs[1:]:
    fname = 'Traffic Counts ' + yr + '.csv'
    df = pd.read_csv(fname, sep=',', header=2, usecols=list(range(8)), 
                     thousands=',')
    traffic_data = pd.concat([traffic_data,df], axis=0)
"""
# Get an additional column with informaton about the location of the traffic
# counter
"""
brpkwy = traffic_data[traffic_data['UnitCode'] == 'BLRI']
nparks = traffic_data[traffic_data['ParkType'] == 'National Park']

nparks_by_time = nparks.groupby(['Year', 'Month'])
# Plot traffic to national parks in aggregate as a function of month
x = list(nparks_by_time.index)
d = list(zip(*x))
yr = d[0]
mo = d[1]
y = nparks_by_time['TrafficCount']
yrs = np.unique(yr)
num_yrs = len(np.unique(yr))

output_file("nparks_traffic_agg.html")
p = figure(title='Total Traffic to all National Parks, 1985-2019', 
           plot_width=800, plot_height=250, x_axis_type="datetime")
alpha = np.linspace(0.1, 1, num=num_yrs)
for i in range(num_yrs):
    p.line(mo[12*i:12*i+12], y[12*i:12*i+12], line_width=2, color='navy', 
           alpha=alpha[i], legend_label=str(yr[i]))
    
show(p)
"""
"""
# Get rid of battlefields and historic sites
parkTypes = ['National Parkway', 'National Park', 'National Recreation Area', 
              'National Lakeshore', 'National Monument', 'National Preserve', 
              'National River', 'National Seashore', 'Park (Other)', 
              'National Reserve', 'National Wild & Scenic River']
traffic_data = traffic_data[traffic_data['ParkType'].isin(parkTypes)]

traffic_data['CountLocation'] = traffic_data['TrafficCounter'].str.upper()


# Separate out the traffic counter location
traffic_data['CountLocation'] = traffic_data['CountLocation'].apply(remove_words)
traffic_data.to_csv('nps_traffic.csv')
"""
traffic_data = pd.read_csv('nps_traffic.csv', index_col=0)

# Set API Key and url for Google Places search
api_key = 'secret'
url = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

# Merge the traffic data with location coordinates
places = dill.load(open('nps_places.pkd', 'rb'))
places['latitude'] = pd.to_numeric(places['latitude'])
places['longitude'] = pd.to_numeric(places['longitude'])

traffic_data = traffic_data.reset_index(drop=True)
latitude = pd.Series(index=traffic_data.index.copy(), name='latitude', dtype=float)
longitude = pd.Series(index=traffic_data.index.copy(), name='longitude', dtype=float)
# Find all traffic counter locations within a unit code
counters_by_unit = traffic_data.groupby('UnitCode')['CountLocation'].apply(lambda x: list(np.unique(x)))
#locations = list(traffic_data['CountLocation'].unique())
for unitCode, counter in counters_by_unit.items():
    unitPlaces = find_unit_places(unitCode, places)
    
    # Find the index of a match
    for loc in counter:
        lat, long = match_locations_in_unit(loc, unitPlaces)
        indices = list(traffic_data[(traffic_data['UnitCode'] == unitCode) &
                                    (traffic_data['CountLocation'] == loc)].index)
        
        if (lat == 0) and (long == 0):
            parkName = pd.unique(traffic_data[traffic_data['UnitCode']==unitCode]['ParkName'])[0]
            query = loc + ' near ' + parkName
            req = requests.get(url + 'query=' + query + '&key=' + api_key)
            jsondata = req.json()
            try:
                results = jsondata['results'][0]['geometry']['location']
                lat = results['lat']
                long = results['lng']
            except:
                continue
            
        if lat != 0:
            latitude.at[indices] = lat
        if long != 0:
            longitude.at[indices] = long
            
# Append latitude and longitude to the traffic_data DF
traffic_data = pd.concat([traffic_data, latitude, longitude], axis=1)

# Remove counters at parks that aren't being used  
from nps_utils import load_public_use_data
publicUse = load_public_use_data()
valid_unit_codes = list(publicUse['UnitCode'].unique())

traffic_data = traffic_data[traffic_data['UnitCode'].isin(valid_unit_codes)]

clean_data = traffic_data.dropna(subset=['latitude','longitude'])

month2days = {1:31, 2:28, 3:31, 4: 30, 5:31, 6:30, 7:31, 8:31, 9:30,
                      10:31, 11:30, 12:31}
clean_data['DaysInMonth'] = clean_data['Month'].apply(lambda x: month2days[x])
clean_data['TrafficCountDay'] = clean_data['TrafficCount']/clean_data['DaysInMonth']

clean_data = clean_data.drop(columns=['Region', 'TrafficCounter', 'DaysInMonth'])
clean_data = clean_data.drop_duplicates()

# Assign a unique counter id value to each counter
pairs = clean_data[['UnitCode', 'CountLocation']]
pairs = pairs.drop_duplicates()
pairs['CountID'] = list(range(1,len(pairs)+1))

clean_data = pd.merge(left=clean_data, right=pairs, 
                      on=['UnitCode', 'CountLocation'],
                      how='left')

clean_data_2018 = clean_data[clean_data['Year']==2018]
clean_data_2019 = clean_data[clean_data['Year']==2019]

clean_data.to_csv('nps_traffic_clean.csv')
clean_data_2018.to_csv('nps_traffic_clean_2018.csv')

clean_data_2019.to_csv('nps_traffic_clean_2019.csv')

    