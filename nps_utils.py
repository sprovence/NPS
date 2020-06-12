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
    return pd.read_csv(data_path / 'parks.csv')

def load_geo_data():
    fname = 'boundaries.geojson'
    with open(data_path / fname) as file:
        boundaries = geojson.load(file)
    return boundaries
    
def load_public_use_data():
    fname = 'PublicUseStatistics2018_clean.csv'
    return pd.read_csv(data_path / fname, index_col=0)

def load_public_use_data_full():
    fname = 'nps_public_use.csv'
    return pd.read_csv(data_path / fname, index_col=0)

def load_traffic_data():
    fname = 'nps_traffic_2019.csv'
    return pd.read_csv(data_path / fname, index_col=0)

#traffic = load_traffic_data()
#boundaries = load_geo_data()
#publicUse = load_public_use_data()

def addTraffic(nmap, traffic, month):
    #traffic = load_traffic_data()
    
    means = traffic.groupby('UnitCode').mean()['TrafficCountDay' + str(month)]
    stds = traffic.groupby('UnitCode').std()['TrafficCountDay' + str(month)]
    
    # Create a marker for each traffic counter
    for ind in traffic['CountID'].index:
        num_cars = traffic.loc[ind, 'TrafficCountDay' + str(month)]
        unit = traffic.loc[ind, 'UnitCode']
        park = traffic.loc[ind, 'ParkName']
        
        if ~np.isnan(stds[unit]):
            if num_cars < (means[unit] - stds[unit]):
                qualifier = 'VERY LOW'
                color = '#009933'
            elif num_cars < (means[unit] - (stds[unit]/2.0)):
                qualifier = 'LOW'
                color = '#8cff1a'
            elif num_cars < (means[unit] + (stds[unit]/2.0)):
                qualifier = 'AVERAGE'
                color = '#ffff00'
            elif num_cars < (means[unit] + stds[unit]):
                qualifier = 'HIGH'
                color = '#ff9900'
            else:
                qualifier = 'VERY HIGH'
                color = '#990000'
        
        
        popup = folium.Popup(
                html='<p></strong>' + traffic.loc[ind, 'CountLocation'] + '</strong></p>'
                + '<p>Mean daily car count at this location: <strong>{}</strong></p>'.format(int(num_cars))
                + '<p>Mean daily car count at all locations in ' + park + ': <strong>{}</strong></p>'.format(int(means[unit])) 
                + '<p>Mean daily car count at all NPS locations : <strong>{}</strong></p>'.format(int(traffic.mean()['TrafficCountDay' + str(month)])),
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


def makeMap(parks, publicUse, traffic_data, boundaries, month=7, unit='JOTR', 
            density=True, traffic=True):
    # Load in data
    #boundaries_fname, boundaries = load_geo_data()
    #publicUse = load_public_use_data()

    data = publicUse[publicUse['Month']==month]
    
    parks = pd.read_csv(data_path / 'parks.csv')
    if not parks[parks['parkCode'].str.upper() == unit].empty:
        park_index = parks[parks['parkCode'].str.upper() == unit].index[0]
        latLong = parks.at[park_index, 'latLong']
        latLong = latLong.split(', ')
        lat = float(latLong[0][4:])
        long = float(latLong[1][5:])
        zoom=9
    else:
        lat = 33.91418525
        long = -115.8398125
        zoom=9
    
    npsmap = folium.Map(location=[lat, long], zoom_start=zoom)
    
    if density:
        bins = [0, 100, 500, 1000, 10000, max(data['DailyAcreagePerVisitor2018'])]
        #bins = list(publicUse['DailyDensity'].quantile([0, 0.2, 0.4, 0.6, 0.8, 1]))

        folium.Choropleth(
                geo_data=boundaries,
                data = data,
                columns = ['UnitCode', 'DailyAcreagePerVisitor2018'],
                key_on = 'feature.properties.UNIT_CODE',
                legend = 'Average Acres per Visitor, 2018',
                fill_color = 'PuRd',
                nan_fill_color = 'black',
                name = 'Choropleth',
                line_weight=2,
                bins = bins,
                highlight = True,
                ).add_to(npsmap)
    else:
        #bins = list(publicUse['DailyVisitors'].quantile([0, 0.1, 0.2, 
        #            0.3, 0.4, 0.5, 0.6, 0.8, 1]))
        bins = [0, 100, 500, 1000, 2000, 4000, 6000, 8000, 10000, 
                max(data['DailyVisitors2018'])]

        folium.Choropleth(
                geo_data=boundaries,
                data = data,
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
    
    folium.GeoJson(
        data=boundaries,
        name='GeoJson',
        style_function=lambda x: {'weight': 0, 'fillColor': '#FF69B4'},
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=['Park Name', 'Park Type',
                                              'Average Daily Visitors ' + str(month), 
                                              'Average Acres Available per Visitor ' + str(month)], 
                                    aliases=['Park Name', 'Park Type', 
                                             'Average Daily Visitors', 
                                             'Average Acres Available Per Visitor'],
                                  labels=True, sticky=True)
        ).add_to(npsmap)
    
    if traffic:
        npsmap = addTraffic(npsmap, traffic_data, month=month)
    
    
    return npsmap

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
    