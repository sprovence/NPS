# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 17:26:31 2020
Merge the public use statistics into a single .csv
@author: sydne
"""

import pandas as pd
import numpy as np
from sklearn import cluster, linear_model
from radar_chart import radar_chart
import matplotlib.pyplot as plt

public_use_yrs = ['1979', '1980-1984', '1985-1989', '1990-1994', '1995-1999', 
                    '2000-2004', '2005-2009', '2010-2018']
traffic_counts_yrs = ['1985-1989', '1990-1994', '1995-1999','2000-2004', 
                      '2005-2009', '2010-2014', '2015-2019']

# Read first .csv to get header names
public_use_data = pd.read_csv('Public Use Statistics 1979.csv', sep=',', 
                              header=2, usecols=list(range(18)), thousands=',')
traffic_data = pd.read_csv('Traffic Counts 1985-1989.csv', sep=',', header=2, 
                           usecols=list(range(8)), thousands=',')

for yr in public_use_yrs[1:]:
    fname = 'Public Use Statistics ' + yr + '.csv'
    df = pd.read_csv(fname, sep=',', header=2, usecols=list(range(18)), 
                     thousands=',')
    public_use_data = pd.concat([public_use_data,df], axis=0)
    
for yr in traffic_counts_yrs[1:]:
    fname = 'Traffic Counts ' + yr + '.csv'
    df = pd.read_csv(fname, sep=',', header=2, usecols=list(range(8)), 
                     thousands=',')
    traffic_data = pd.concat([traffic_data,df], axis=0)

# Get the total number of recreational visits vs hours for each type of park
public_by_type = public_use_data.drop(columns=['Year','Month'])
public_by_type = public_by_type.groupby(['ParkType']).sum()
public_by_type = public_by_type.sort_values('RecreationVisits',ascending=False)
traffic_by_type = traffic_data.drop(columns=['Year','Month'])
traffic_by_type = traffic_by_type.groupby(['ParkType']).sum()
traffic_by_type = traffic_by_type.sort_values('TrafficCount', ascending=False)

# Get a list of the names of the parks under each type subset, ordered by visits
national_parks_use = public_use_data[(public_use_data['ParkType'] == 'National Park')].drop(columns=['Year','Month'])
national_parks_most_used = national_parks_use.groupby('ParkName').sum()
national_parks_most_used = national_parks_most_used.sort_values(
        'RecreationVisits',ascending=False)

"""
Where can I go to camp if I'm a tent camper who doesn't want to be by RV 
campers?
What percentage of people who visit the parks recreationally camp?
What does the division between camping sets look like when recreational visits
    are added in?
"""
# subset the public use data into the total usage of all parks from 2010-2019
parks = public_use_data[public_use_data['Year'] >= 2010]
parks = parks.drop(columns=['Year','Month']).groupby(['ParkName']).sum()

# Create new column headers for camping and camping as a percentage of
# all recreational overnight stays
camping_columns = ['ConcessionerLodging','ConcessionerCamping','TentCampers',
                'RVCampers','Backcountry']
camping_columns_percent = [s + 'Percent' for s in camping_columns]

# Get the total number of camping instances in each park
parks['CampingTotal'] = parks[camping_columns].sum(axis=1)

# Create a new subset of parks that only includes parks where the total 
# camping usage is greater than zero.
camping = parks[parks['CampingTotal'] != 0]

# What percentage of people who visit the parks recreationally camp overnight?
print('Total number of national parks included in analysis (2010-2019): ' + 
      str(len(parks)))
print('Total number of national parks with no recreational camping: ' + 
      str(len(parks) - len(camping)))

camping['PercentVisitorsCamping'] = 100* camping['CampingTotal'] / (camping['RecreationVisits'] + camping['CampingTotal'])
camping = camping.sort_values('PercentVisitorsCamping', ascending=True)
print('Parks with the fewest campers (by percentage):')
print(camping['PercentVisitorsCamping'].head())
camping = camping.sort_values('PercentVisitorsCamping', ascending=False)
print('Parks with the most campers (by percentage):')
print(camping['PercentVisitorsCamping'].head())

# Append a percentage column for each type of camping.
camping_percent = camping.apply(lambda x:x[camping_columns]/x['CampingTotal'], 
                                axis=1)
camping_percent.columns = [str(col) + 'Percent' for col in camping_percent.columns]
camping = pd.concat([camping,camping_percent], axis=1)

# Get a list of the park names in which camping occurs
park_names = list(camping.index.values)

# Cluster the parks based on the percentage of each type of camping.
np_camping = camping[camping_columns_percent].to_numpy()
k_means = cluster.KMeans(n_clusters=4)
k_means.fit(np_camping)
values = pd.DataFrame(k_means.cluster_centers_.squeeze(),
                      columns=camping_columns_percent)
# Plot a spider chart of each of the clusters
fig, ax = radar_chart(values, camping_columns)
labels = k_means.labels_
camping['Cluster'] = labels
#pd.plotting.parallel_coordinates(camping, 'Cluster', cols=camping_columns_percent)

# Figure out the top 10 most visited parks in each cluster.
backcountry_cluster = camping[camping['Cluster'] == 0]
backcountry_cluster = backcountry_cluster.sort_values('RecreationVisits', 
                                                      ascending=False)
backcountry = list(backcountry_cluster.index[0:10])

concessioner_cluster = camping[camping['Cluster'] == 1]
concessioner_cluster = concessioner_cluster.sort_values('RecreationVisits', 
                                                        ascending=False)
concessioner = list(concessioner_cluster.index[0:10])

tent_cluster = camping[camping['Cluster'] == 2]
tent_cluster = tent_cluster.sort_values('RecreationVisits', ascending=False)
tent = list(tent_cluster.index[0:10])

RV_cluster = camping[camping['Cluster'] == 3]
RV_cluster = RV_cluster.sort_values('RecreationVisits', ascending=False)
RV = list(RV_cluster.index[0:10])

# Append the top 5 to the radar chart
fig.text(0.5, 0.965, 'K-Means Clustering of National Parks by Camping (Percent Occurance)',
             horizontalalignment='center', color='black', weight='bold',
             size='large')
newline = '\n'
fig.text(0.86, 0.79, 'Most Visited Parks in Cluster 1:', fontweight='bold', ha='center',
         wrap=True)
fig.text(0.86, 0.7, newline.join(backcountry[0:5]), ha='center', wrap=True)
fig.text(0.2, 0.85, 'Most Visited Parks in Cluster 2:', fontweight='bold', ha='center',
         wrap=True)
fig.text(0.2, 0.76, newline.join(concessioner[0:5]), ha='center', wrap=True)
fig.text(0.275, 0.14, 'Most Visited Parks in Cluster 3:', fontweight='bold', ha='center',
         wrap=True)
fig.text(0.275, 0.05, newline.join(tent[0:5]), ha='center', wrap=True)
fig.text(0.75, 0.14, 'Most Visited Parks in Cluster 4:', fontweight='bold', ha='center',
         wrap=True)
fig.text(0.75, 0.05, newline.join(RV[0:5]), ha='center', wrap=True)

# Add columns for the total usage
parks_by_year = public_use_data.drop(columns=['Month']).groupby('Year').sum()
parks_by_year['CampingTotal'] = parks_by_year[camping_columns].sum(axis=1)
parks_by_year['TotalVisits'] = parks_by_year['CampingTotal'] + parks_by_year['RecreationVisits'] + parks_by_year['NonRecreationVisits'] + parks_by_year['NonRecreationOvernightStays'] + parks_by_year['MiscellaneousOvernightStays']
parks_by_year['TotalRecreationVisits'] = parks_by_year['CampingTotal'] + parks_by_year['RecreationVisits']

# Append a percentage column for each type of camping.
camping_percent_by_year = parks_by_year.apply(lambda x:x[camping_columns]/x['CampingTotal'], 
                                axis=1)
camping_percent_by_year.columns = [str(col) + 'Percent' for col in camping_percent_by_year.columns]
parks_by_year = pd.concat([parks_by_year,camping_percent_by_year], axis=1)

# Fit a trendline to the data to predict the total number of visits to each
# national park in 2020.     
# Create linear regression object
regr = linear_model.LinearRegression()

# Train the model using year as X and recreational visitors per year
X = parks_by_year.index.values.reshape(-1,1)
Y = parks_by_year['TotalVisits'].values.reshape(-1,1)
regr.fit(X, Y)

# Make predictions using the testing set
visitors_trendline = np.linspace(start=1979, stop=2030, num=2030-1979+1)
visitors_prediction = regr.predict(visitors_trendline.reshape(-1,1))

# Train the model using total number of campers per year
Y = parks_by_year['CampingTotal'].values.reshape(-1,1)
regr.fit(X, Y)

# Make predictions using the testing set
campers_trendline = np.linspace(start=1979, stop=2030, num=2030-1979+1)
campers_prediction = regr.predict(visitors_trendline.reshape(-1,1))

# Plot the predictions for number of visitors and number of campers
fig1, axs1 = plt.subplots(figsize=(9, 9), nrows=2, ncols=1, 
                        gridspec_kw = {'hspace':0.3, 'wspace':0, 'top':0.95, 
                                       'left':0.1, 'right':0.95, 
                                       'bottom':0.05})
axs1[0].plot(parks_by_year.index.values, parks_by_year['TotalVisits']/1E6,
    linewidth=3, linestyle='-', color='tomato') 
axs1[0].plot(visitors_trendline, visitors_prediction/1E6, linewidth=2, 
    linestyle=':', color='tomato')
axs1[0].set_ylabel('Number of Visitors, (Millions)', fontsize=12)
axs1[0].set_xlabel('Year', fontsize=12)
axs1[0].set_title('Total Number of Visitors to National Parks, 1979-2018', 
   fontweight='bold')
axs1[0].set_xlim([1979,2020])
axs1[0].legend(labels=['Total Visitors', 
   'Linear Regression Fit'], loc='upper left')
    
axs1[1].plot(parks_by_year.index.values, parks_by_year['CampingTotal']/1E6,
    linewidth=3, linestyle='-', color='sandybrown') 
axs1[1].plot(campers_trendline, campers_prediction/1E6, linewidth=2, 
    linestyle=':', color='sandybrown')
axs1[1].set_ylabel('Number of Campers, (Millions)', fontsize=12)
axs1[1].set_xlabel('Year', fontsize=12)
axs1[1].set_title('Total Number of Camping Visits to National Parks, 1979-2018', 
   fontweight='bold')
axs1[1].set_xlim([1979,2020])
axs1[1].legend(labels=['Total Campers', 
   'Linear Regression Fit'], loc='upper right')


# Plot the total number of visits per year over time
fig, axs = plt.subplots(figsize=(9, 9), nrows=2, ncols=1, 
                        gridspec_kw = {'hspace':0.375, 'wspace':0, 'top':0.9, 
                                       'left':0.1, 'right':0.95, 
                                       'bottom':0.05})

# Plot overall recreation visits by year
labels = ['Recreational Visits', 'Non-Recreational Visits', 
          'Recreational Camping Visits', 'Non-Recreational Overnight Stays', 
          'Miscellaneous Overnight Stays']
colors = ['skyblue', 'sandybrown', 'tomato', 'thistle', 'lightgreen']
y = np.vstack([parks_by_year['RecreationVisits'], 
               parks_by_year['NonRecreationVisits'], 
               parks_by_year['CampingTotal'],
               parks_by_year['NonRecreationOvernightStays'],
               parks_by_year['MiscellaneousOvernightStays']])
y = y/1E6
axs[0].stackplot(parks_by_year.index.values, y, labels=labels, colors=colors, 
                   edgecolor='black')
axs[0].set_ylabel('Number of Visits, (Millions)', fontsize=12)
axs[0].set_xlabel('Year', fontsize=12)
axs[0].set_title('Total Number of Visits to National Parks, 1979-2018', 
   fontweight='bold', pad=40)
axs[0].set_xlim([1979,2018])
axs[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=3)

# Plot a breakdown of camping types by year
labels = ['Concessioner Lodging', 'Concessioner Camping', 'Tent Campers', 
          'RV Campers', 'Backcountry Campers']
colors = ['chocolate', 'salmon', 'cornflowerblue', 'mediumturquoise', 'orchid']
y = np.vstack([parks_by_year[camping_columns_percent]])
y = y*100
axs[1].stackplot(parks_by_year.index.values, np.transpose(y), labels=labels,
   colors=colors, edgecolor='black')
axs[1].set_ylabel('Percentage of Camping Visitors, (%)', fontsize=12)
axs[1].set_xlabel('Year', fontsize=12)
axs[1].set_title('Types of Campers in National Parks, 1979-2018', 
   fontweight='bold', pad=40)
axs[1].set_xlim([1979,2018])
axs[1].set_ylim([0,100])
axs[1].legend(loc='upper center', bbox_to_anchor=(0.5, 1.18), ncol=3)

# Track national park usage compared to boundaries in 2019. 