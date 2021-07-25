from matplotlib import pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import streamlit as st
# Return the scatterplot with the correct axes and filters
def scatter_matplot_returner(dataX, dataY, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY, gradiant, colors, doColor):
    # Map data to floats
    dataX = dataX.map(lambda x: float(x))
    dataY = dataY.map(lambda x: float(x))

    # Generate unmarked chart
    fig, ax = plt.subplots()
    ax.axhline(y=0, lw=1.5, color='k')
    ax.axvline(x=0, lw=1.5, color='k')
    
    # Scatter the data and colors
    plt.scatter(x=dataX, y=dataY, s=3, c=gradiant)
    #Make line of best fit
    totalm = np.polyfit(dataX, dataY, 1)
       
    # If splitter
    if doColor:
        xmax = 0
        xmin = 0
        ymax = 0
        ymin = 0
        for c in colors:
            ins = []
            for index, row in gradiant.iteritems():
                if row == c:
                    ins.append(index)
            dataXTemp = dataX.loc[ins]
            dataYTemp = dataY.loc[ins]

            if dataXTemp.max() > xmax:
                xmax = dataXTemp.max()

            if dataXTemp.min() < xmin:
                xmin = dataXTemp.min()

            if dataYTemp.max() > ymax:
                ymax = dataYTemp.max()

            if dataYTemp.min() < ymin:
                ymin = dataYTemp.min()

            tempm = np.polyfit(dataXTemp, dataYTemp, 1)
            midpoint = [float(dataXTemp.max()+dataXTemp.min())/2.0,float(dataYTemp.max()+dataYTemp.min())/2.0]
            m2 = float(-1)/tempm[0]
            b = midpoint[1] - m2*(midpoint[0])
            #dataXTemp = dataXTemp[int((len(dataXTemp)/2)-5):int((len(dataXTemp)/2)+5)]
            plt.plot(dataXTemp, m2*dataXTemp+b, c)

    plt.plot(dataX, totalm[0] * dataX + totalm[1], 'r')

    # Generate and return the plot
    ax.set_title(str(dataOptionX) + " for " + str(nodeOptionX) + " vs " + str(dataOptionY) + " for " + str(nodeOptionY))
    ax.set_ylabel(str(nodeOptionY) + " " + str(dataOptionY))
    ax.set_xlabel(str(nodeOptionX) + " " + str(dataOptionX))
    if doColor:
        plt.legend(handles=make_legend(colors))
        ax.set(xlim=(xmin-(abs(xmin)/10), xmax+(abs(xmin)/10)), ylim=(ymin-(abs(ymin)/10), ymax+(abs(ymin)/10)))

    plt.grid()
    return fig

def make_legend(colors):
    color_one = mpatches.Patch(color=colors[0], label='To -2')
    color_two = mpatches.Patch(color=colors[1], label='-2 To 1')
    color_three = mpatches.Patch(color=colors[2], label='1 To 5')
    color_four = mpatches.Patch(color=colors[3], label='5 To')
    return [color_one, color_two, color_three, color_four]
