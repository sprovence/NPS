# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 09:54:39 2020
GISPandas to plot traffic counters against park bounaries
@author: sydne
"""

from nps_utils import load_parks_data, load_public_use_data, load_traffic_data, load_geo_data, makeMap
import panel as pn
import panel.widgets as pnw
import pandas as pd

month_dict = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 
              'June':6, 'July':7, 'August':8, 'September':9, 'October':10,
              'November':11, 'December':12}

parks = load_parks_data()
traffic_data = load_traffic_data()
boundaries = load_geo_data()
publicUse = load_public_use_data()
park_dict = dict(zip(publicUse['ParkName'].unique(), publicUse['UnitCode'].unique()))

def map_dash():
    """Map dashboard"""
    # Create the map
    map_pane = pn.pane.plot.Folium(sizing_mode="stretch_width")
    map_pane.object = makeMap(parks, publicUse, traffic_data, boundaries, 
                              month=7, unit='JOTR', density=False)

    # Create the dropdown menus for month and visitors
    month_buttons = pnw.RadioButtonGroup(name = 'Month', 
                                         options = list(month_dict.keys()),
                                         button_type = 'primary',
                                         value = 'July')
    name2col = {'Average Daily Visitors': 'DailyVisitors2018', 
                'Average Acres Per Visitor': 'DailyAcreagePerVisitor2018'}
    data_select = pnw.Select(name='Visitor Data', 
                             options=list(name2col.keys()))
    traffic_checkbox = pnw.Checkbox(name='Display traffic counters',
                                    value=True)
    park_select = pnw.Select(name='Where do you want to go?', 
                             options=list(park_dict.keys()),
                             value='Joshua Tree NP')
    
    
    # Trigger map updates
    def update_map(event):
        if data_select.value=='Average Daily Visitors':
            density = False
        else:
            density = True
        month = month_dict[month_buttons.value]
        unit = park_dict[park_select.value]
        map_pane.object = makeMap(parks, publicUse, traffic_data, boundaries, 
                                  month=month, unit=unit, density=density,
                                  traffic=traffic_checkbox.value)
        return
    
    # Updates
    month_buttons.param.watch(update_map,'value')
    month_buttons.param.trigger('value')
    data_select.param.watch(update_map,'value')
    data_select.param.trigger('value')
    park_select.param.watch(update_map,'value')
    park_select.param.trigger('value')
    traffic_checkbox.param.watch(update_map, 'value')
    traffic_checkbox.param.trigger('value')
    
    # Fully return the map
    app = pn.Column(month_buttons,
                    pn.Row(data_select, traffic_checkbox),
                    map_pane,
                    park_select,
                    width_policy='fit')
    return app

#pn.extension()

#app = map_dash()
#app.servable()
#server = app.show(threaded=True)