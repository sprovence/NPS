# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 16:10:21 2020

@author: sydne
"""

import geopandas as gpd
import descartes

# Import the shape file
fname = "nps_boundary.shp"
data = gpd.read_file(fname)

# Download the world and nearest cities
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
cities = gpd.read_file(gpd.datasets.get_path('naturalearth_cities'))
base = world[world.name=='United States of America'].plot(color='white',
            edgecolor='black')
data.plot(ax=base, color='red', markersize=5)