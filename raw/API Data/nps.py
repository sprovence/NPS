# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 12:01:18 2020
Scraping the NPS API, saves datasets as .txt files
@author: sydne
"""
import urllib.request
import requests
import json

# Configure API request
api_token = "4k4hiWnY5toIp7RvSogtqUmrcsxwmqqIJsQmPTR9"
url = "https://developer.nps.gov/api/v1/"
#datasets = ["alerts", "articles", "campgrounds", "events", "newsreleases", 
#            "parks", "people", "places", "vistorcenters"]
datasets = "vistorcenters"

# Cycle through each dataset and save json data to .txt file
for dataName in datasets:    
    # Request parks dataset
    endpoint = url + dataName + "?api_key=" + api_token + "&limit=600"
    response = requests.get(endpoint)

    # Execute request and parse response
    json_data = json.loads(response.text)

    # Parse json data to get total number of items
    total = json_data["total"]
    data = json_data["data"]
    
    # If there's more than 50 items, continue querying to get all items
    start = 0
    if int(total) > 50:
        while start < int(total):
            start = start + 50
            # Make another request to the server to get all information available
            endpoint = endpoint + "&start=" + str(start)
            req = urllib.request.Request(endpoint)
            response = urllib.request.urlopen(req).read()
            more_json_data = json.loads(response.decode('utf-8'))
            more_data = more_json_data["data"]
            data = data + more_data
            

    # Save data as .txt file
    if '/' in dataName:
        dataName = dataName.replace("/", "-")
    with open(dataName + ".txt", 'w') as outfile:
        json.dump(data, outfile)

# Read the json data into pandas df
places = pd.read_json('places.txt')

