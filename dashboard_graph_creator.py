from matplotlib import pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import streamlit as st
# Return the scatterplot with the correct axes and filters
def scatter_matplot_returner(dataX, dataY, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY, gradiant, colors, doColor):
    dataX = dataX.map(lambda x: float(x))
    dataY = dataY.map(lambda x: float(x))

    # Generate unmarked chart
    fig, ax = plt.subplots()
    ax.axhline(y=0, lw=1.5, color='k')
    ax.axvline(x=0, lw=1.5, color='k')

    plt.scatter(x=dataX, y=dataY, s=3, c=gradiant)
    m = np.polyfit(dataX, dataY, 1)
    plt.plot(dataX, m[0] * dataX + m[1])

    # Generate and return the plot
    ax.set_title(str(dataOptionX) + " for " + str(nodeOptionX) + " vs " + str(dataOptionY) + " for " + str(nodeOptionY))
    ax.set_ylabel(str(nodeOptionY) + " " + str(dataOptionY))
    ax.set_xlabel(str(nodeOptionX) + " " + str(dataOptionX))
    if doColor:
        plt.legend(handles=make_legend(colors))

    plt.grid()
    return fig

def make_legend(colors):
    color_one = mpatches.Patch(color=colors[0], label='To -2')
    color_two = mpatches.Patch(color=colors[1], label='-2 To 1')
    color_three = mpatches.Patch(color=colors[2], label='1 To 5')
    color_four = mpatches.Patch(color=colors[3], label='5 To')
    return [color_one, color_two, color_three, color_four]
