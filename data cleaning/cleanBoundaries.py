# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 16:10:21 2020

@author: sydne
"""

import geopandas as gpd
import pandas as pd


publicUse = pd.read_csv('Public Use Statistics 2018.csv', index_col=0)
# Import the shape file
fname = "nps_boundary.shp"
boundaries = gpd.read_file(fname)

unit_codes = publicUse['UnitCode'].unique()

# Get rid of boundaries for parks with no public use data
boundaries = boundaries[boundaries['UNIT_CODE'].isin(unit_codes)]


# Write a shapefile
boundaries.to_file("nps_boundary_clean.shp")
