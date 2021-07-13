from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn import svm
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib
import statistics

# Return the scatterplot with the correct axes and filters
def scatter_matplot_returner(dataX, dataY, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY):
    
    # Generate unmarked chart
    fig, ax = plt.subplots()
    ax.axhline(y=0, lw=1.5, color='k')
    ax.axvline(x=0, lw=1.5, color='k')

    go = plt.scatter(y=dataY, x=dataX)
    
    # Generate and return the plot
    ax.set_title(str(dataOptionX) + " for " + str(nodeOptionX) + " vs " + str(dataOptionY) + " for " + str(nodeOptionY))
    ax.set_ylabel(str(nodeOptionY) + " " + str(dataOptionY))
    ax.set_xlabel(str(nodeOptionX) + " " + str(dataOptionX))
    plt.grid()
    return fig

# Create the heatmap and return it
def scatter_seaborn_returner(dfs, con, reverse):
    df = dfs[con]

    # Load the correspondance dataset
    fig, ax = plt.subplots()
    corrs = df.corr()
    
    # Columns to drop
    dropsCols = ['AverageLoad', 'Region 1', 'Region 2', 'Region 3', 'Region 4', 'Region 5', 'WindSum', 'NetLoad']
    dropsRows = ['Shadow', 'HiCongestRT', 'LoCongestRT', 'HiPriceDA', 'HiPriceRT', 'LoPriceDA', 'LoPriceRT', 'LoShift', 'HiShift', 'Spread']
    corrs.drop('Hour', axis=0, inplace=True)
    corrs.drop('Hour', axis=1, inplace=True)
    
    # Drop the columns for rows and columns
    for d in dropsCols:
        corrs.drop(reverse[d], axis=0, inplace=True)
    for d in dropsRows:
        corrs.drop(reverse[d], axis=1, inplace=True)
    
    # Remove the node winds and temps
    threes = list(df.columns.values)
    threes = [item for item in threes if (("wind" in item or "temp" in item) and (" " not in item))]
    for t in threes:
        corrs.drop(t, axis=0, inplace=True)
        corrs.drop(t, axis=1, inplace=True)
    
    # This one is different for some reason
    corrs.drop("06D", axis=0, inplace=True)
    corrs.drop("06D", axis=1, inplace=True)

    # Generate and return the heatmap
    ax = sns.heatmap(corrs, annot=True)
    ax.set_title("Heatmap of Factors For " + str(df['NodesNames'].iloc[0]))
    plt.xticks(rotation=45)
    return fig
