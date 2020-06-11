# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 13:50:07 2020

@author: sydne
"""
from shapely.geometry import Polygon
import geopandas as gpd
import pandas as pd
import numpy as np
from nps_utils import load_traffic_data, load_public_use_data
from pathlib import Path

data_path = Path('./data/')


# Load data
traffic = load_traffic_data()
traffic = traffic.drop_duplicates()
boundaries = gpd.read_file(data_path / 'nps_boundaries.geojson')

"""
# Re-orient the dataframe so that the traffic for each month is it's own col
new_traffic = traffic[traffic['Month']==1].rename(columns = 
                     {'TrafficCountDay': 'TrafficCountDay1', 
                      'TrafficCount': 'TrafficCount1'}).reset_index()
new_traffic = new_traffic.drop(columns=['index', 'Year', 'Month'])
new_traffic = new_traffic.drop_duplicates(subset='CountID')

for month in range(2, 13):
    new_col = traffic[traffic['Month']==month].rename(columns = 
                     {'TrafficCountDay': 'TrafficCountDay'+str(month), 
                     'TrafficCount': 'TrafficCount'+str(month)}).reset_index()
    new_col = new_col[['CountID', 
                       'TrafficCountDay' + str(month), 
                      'TrafficCount' + str(month)]]
    new_col = new_col.drop_duplicates(subset='CountID')
    new_traffic = pd.merge(left=new_traffic, right=new_col, on='CountID')
    
traffic = new_traffic.copy() 
traffic.to_csv(data_path / 'nps_traffic_2019.csv')
"""

# Set variables
radius = 0.05
theta = np.arange(start=0,stop=2*np.pi-(np.pi/16),step=np.pi/16)

# Generate polygons to map radius around traffic counters
geometry = []
for index in list(traffic.index):
    unit = traffic.loc[index, 'UnitCode']
    
    lat = traffic.loc[index, 'latitude']
    lon = traffic.loc[index, 'longitude']
    new_lat = radius*np.cos(theta) + lat
    new_lon = radius*np.sin(theta) + lon
    pgon = Polygon(zip(new_lon, new_lat))
    
    # Check if the polygon intersects with the outer park boundary
    ind = list(boundaries[boundaries['UNIT_CODE']==unit].index)[0]
    park_boundary = boundaries.loc[ind, 'geometry']
    
    if park_boundary.is_valid:
        intersect = pgon.intersection(park_boundary)
    else:
        intersect = pgon.intersection(park_boundary.buffer(0))
    
    geometry.append(intersect)
 
crs = {'init': 'epsg:4269'}
geotraffic = gpd.GeoDataFrame(traffic, geometry=geometry, crs=crs)

geotraffic.to_file(data_path / "geotraffic.geojson", driver='GeoJSON')