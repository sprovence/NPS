# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 14:25:59 2020
Plotting utilities for the NPS datasets
@author: sydne
"""

# Libraries
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
import pandas as pd
import numpy as np
from math import pimatplotlib.use('Agg')

def radar(df):
    """
    Main function to plot a radar plot
    Input:
        df = the dataframe to plot
    """
    spoke_labels = list(df)
    N = len(spoke_labels) # The number of spokes on the polygon
    clusters = len(df.index)
    
    angles = [i / float(N) * 2 * pi for i in range(N)]
    angles += angles[:1]  # repeat the first value to close the circle
    
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in angles]
    plt.subplot(111, polar=True, gridspec_kw)
    plt.Polygon(verts, closed=True, edgecolor='k')
    
    
    fig, ax = plt.subplots(figsize=(9, 9), nrows=1, ncols=1,
                             subplot_kw=dict(projection='radar'))
    
    for d in range(clusters):
        ax.plot(theta, df.iloc[d])
        ax.fill(theta, df.iloc[d], alpha=0.25)
        
    #ax.set_thetagrids(tuple(np.degrees(theta)), labels=None)
