# Import packages
import folium
import geopandas as gpd
import pandas as pd
#from data_cleaning_utils import getPublicUse
import geojson
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Spectral11, viridis


month2days = {1:31, 2:28, 3:31, 4: 30, 5:31, 6:30, 7:31, 8:31, 9:30,
                      10:31, 11:30, 12:31}
data_path = Path('./data/')

def load_parks_data():
    return pd.read_csv(data_path / 'parks.csv', index_col=0)

def load_geo_data():
    fname = 'boundaries.geojson'
    with open(data_path / fname) as file:
        boundaries = geojson.load(file)
    return boundaries

def load_geopd_data():
    fname = 'boundaries.geojson'
    return gpd.read_file(data_path / fname)
    
def load_public_use_data():
    fname = 'nps_public_use.csv'
    data = pd.read_csv(data_path / fname, index_col=0)
    return data[data['ParkType']=='National Park']

def load_public_use_data_2018():
    fname = 'PublicUseStatistics2018_clean.csv'
    data = pd.read_csv(data_path / fname, index_col=0)
    return data[data['ParkType']=='National Park']

def load_public_use_data_full():
    fname = 'nps_public_use.csv'
    return pd.read_csv(data_path / fname, index_col=0)

def load_traffic_data():
    fname = 'nps_traffic_2019.csv'
    return pd.read_csv(data_path / fname, index_col=0)

def get_coords(unit, parks):
    if not parks[parks['parkCode'].str.upper() == unit].empty:
        park_index = parks[parks['parkCode'].str.upper() == unit].index[0]
        latLong = parks.at[park_index, 'latLong']
        latLong = latLong.split(', ')
        lat = float(latLong[0][4:])
        long = float(latLong[1][5:])   
    else:
        lat = 33.91418525
        long = -115.8398125
    return lat, long

def get_visitors(unit, month, publicUse):
    return publicUse[(publicUse['Month']==month) & 
                     (publicUse['UnitCode']==unit)]

def get_bounds(unit, boundaries):
    return boundaries[boundaries['UNIT_CODE'] == unit.upper()]

def get_traffic(unit, traffic_data):
    return traffic_data[traffic_data['UnitCode'] == unit.upper()]

def makeMap(unit, month, coords, boundaries, visitors, traffic, 
            useTraffic=True):
    # Initialize the map at the park coordinates
    npsmap = folium.Map(location=coords, zoom_start=9)
    
    # Set the bins for the Choropleth
    bins = [0, 500, 2000, 6000, 10000, 51634] # Max daily vistors in 2018
    
    # Draw the choropleth (is the number of visitors high or low? Use color 
    # representation)
    folium.Choropleth(
        geo_data=boundaries,
        data = visitors,
        columns = ['UnitCode', 'DailyVisitors2018'],
        key_on = 'feature.properties.UNIT_CODE',
        legend = 'Average Daily Visitors, 2018',
        fill_color = 'YlOrRd',
        nan_fill_color = 'black',
        name = 'Choropleth',
        line_weight=2,
        bins = bins,
        highlight = True,
        ).add_to(npsmap)
    
    # Draw the geoJson (doesn't actually draw boundaries, used to create the 
    # Tooltip functionality)
    folium.GeoJson(
        data=boundaries,
        name='GeoJson',
        style_function=lambda x: {'weight': 0, 'fillColor': '#FF69B4'},
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=['Park Name', 
                                              'Average Daily Visitors ' + str(month), 
                                              'Average Acres Available per Visitor ' + str(month)], 
                                    aliases=['Park Name', 
                                             'Average Daily Visitors', 
                                             'Average Acres per Visitor'],
                                  labels=True, sticky=True, localize=True)
        ).add_to(npsmap)
    
    # Draw traffic markers
    if useTraffic:
        npsmap = addTraffic(npsmap, traffic, month)
    
    return npsmap

def addTraffic(nmap, traffic, month):
    # Get the mean and standard deviation of traffic at counters
    mean = traffic.mean()['TrafficCountDay' + str(month)]
    std = traffic.std()['TrafficCountDay' + str(month)]
    
    # Create a marker for each traffic counter
    for ind in traffic['CountID'].index:
        num_cars = traffic.loc[ind, 'TrafficCountDay' + str(month)]
        park = traffic.loc[ind, 'ParkName']
        
        if ~np.isnan(std):
            if num_cars <= (mean - 0.8*std):
                qualifier = 'VERY LOW'
                color = '#009933'
            elif (num_cars <= (mean - 0.5*std)) and (num_cars > (mean - 0.8*std)):
                qualifier = 'LOW'
                color = '#8cff1a'
            elif (num_cars <= (mean + 0.5*std)) and (num_cars > (mean - 0.5*std)):
                qualifier = 'AVERAGE'
                color = '#ffff00'
            elif (num_cars <= (mean + 0.8*std)) and (num_cars > (mean + 0.5*std)):
                qualifier = 'HIGH'
                color = '#ff9900'
            else:
                qualifier = 'VERY HIGH'
                color = '#990000'
        else:
            qualifier = 'AVERAGE'
            color = '#ffff00'
        
        
        popup = folium.Popup(
                html='<p></strong>' + traffic.loc[ind, 'CountLocation'] + '</strong></p>'
                + '<p>Mean daily car count at this location: <strong>{}</strong></p>'.format(int(num_cars))
                + '<p>Mean daily car count at all locations in ' + park + ': <strong>{}</strong></p>'.format(int(mean)),
                min_width = 280,
                max_width = 280
                )
        
        tooltip = folium.Tooltip(
                text='Traffic at ' + traffic.loc[ind, 'CountLocation'] + ' is '
                    + qualifier + ' compared to the rest of ' + park,
                sticky=False
                )
        
        folium.CircleMarker(
            location = [traffic.loc[ind, 'latitude'], traffic.loc[ind, 'longitude']],
            popup=popup,
            tooltip = tooltip,
            radius = 6,
            fill = True,
            color = 'grey',
            weight = 1,
            fill_color = color,
            fill_opacity = 0.9
            ).add_to(nmap) 
    
    return nmap

def highlight_function(feature):
    return {
            'weight': 3,
            'color': 'black'
            }
    
def plotVisitors():
    public = load_public_use_data_full()
    # Only plot national parks
    nps = public[public['ParkType']=='National Park']
    
    # Create the Bokeh figure
    p = figure(title="National Park Visitors Over Time", 
               tools="pan,box_zoom,reset,save",
               x_axis_label='Year', 
               y_axis_label='Recreational Visitors',
               x_range=(1989,2018),
               y_range=(2E6, 1E8),
               y_axis_type='log')
    
    # Create x-data
    years = list(nps.groupby('Year').mean().index)
    
    # Create y-data
    allparks = nps.groupby('Year').sum()['RecreationVisits']
    totals = nps[nps['Year']==2018].groupby('UnitCode').sum()['RecreationVisits'].sort_values()
    p.line(x=years, y=allparks, line_color='red', line_width=3,
           legend_label='All National Parks', hover_color='grey')
    
    # Most-visited 10 parks
    top = list(totals.index)[-10:]
    top_parks = nps[nps['UnitCode'].isin(top)]
    top_parks = top_parks.groupby('Year').sum()['RecreationVisits']
    p.line(x=years, y=top_parks, line_color='blue', line_width=3,
           legend_label='10 Most Visited National Parks (in 2018)', 
           hover_color='grey')
    
    # All parks without the top 10 most visited parks
    bottom = allparks-top_parks
    p.line(x=years, y=bottom, line_color='purple', line_width=3,
           legend_label='51 Least Visited National Parks (in 2018)', 
           hover_color='grey')
    
    # Utah
    utah = nps[nps['State']=='UT'].groupby('Year').sum()['RecreationVisits']
    p.line(x=years, y=utah, line_color='orange', line_width=3,
           legend_label='Utah "Mighty 5" Parks', 
           hover_color='grey')
    
    p.legend.location = "center_left"
    p.legend.click_policy="hide"
    
    p.add_tools(
            HoverTool(tooltips=[( '(x,y)',   '($x{int},$y)' )])
            )
    
    return p

def plotIndividualParkVisitors():
    public = load_public_use_data_full()
    # Only plot national parks
    nps = public[public['ParkType']=='National Park']
    totals = nps.groupby('UnitCode').sum()['RecreationVisits'].sort_values()
    
    # Create the Bokeh figure
    p = figure(title="National Park Visitors Over Time", 
               tools="pan,box_zoom,reset,save",
               x_axis_label='Year', 
               y_axis_label='Recreational Visitors',
               x_range=(1989,2018), y_range=(0,1.2E7),
               plot_width=700, plot_height=700)
    
    numlines=len(nps['UnitCode'].unique())
    palette=viridis(numlines)
    color=0
    
    for unit, visitors in totals.items():
        park = nps[nps['UnitCode']==unit]
        years = list(park['Year'].unique())
        name = park['ParkName'].max()
        # Create y-data
        park = park.groupby('Year').sum()
        # Plot the line
        p.line(x=years, y=park['RecreationVisits'], line_color=palette[color], 
               line_width=2, name=name, hover_color='red')
        color+=1
    
    p.add_tools(
            HoverTool(
                    tooltips=[('Park', '$name'),
                              ( '(x,y)',   '($x{int},$y)' )]
                    )
            )
    
    return p
    