from matplotlib import pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import streamlit as st
import scipy
from sklearn import svm
from mlxtend.plotting import plot_decision_regions
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
# Return the scatterplot with the correct axes and filters

kernels = {'Linear': 'linear', 'Polynomial': 'poly', 'Radial': 'rbf', 'Sigmoid': 'sigmoid'}
classifiers = {'Logistic': LogisticRegression(random_state=1,solver='newton-cg',multi_class='multinomial'),
               'Random Forest':  RandomForestClassifier(random_state=1, n_estimators=100),
               'Gaussian': GaussianNB()}

def scatter_matplot_returner(dataX, dataY, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY, gradiant, colors, doRegions, kernel):
    # Map data to floats
    dataX = dataX.map(lambda x: float(x))
    dataY = dataY.map(lambda x: float(x))

    # Generate unmarked chart
    fig, ax = plt.subplots()
    
    # Scatter the data and colors
    if doRegions:
        gradiant = gradiant.to_numpy().astype(np.integer)
        totalData = []
        dataXList = dataX.to_numpy()
        dataYList = dataY.to_numpy()
        for i in range(len(dataXList)):
            totalData.append(np.array([dataXList[i], dataYList[i]]))
        totalData = np.array(totalData)
        if kernel in kernels.keys():
            clf = SVC(C=0.5, kernel=kernels[kernel])
        else:
            clf = classifiers[kernel]
        clf.fit(totalData, gradiant)
        # Plotting decision regions
        plot_decision_regions(totalData, gradiant, clf=clf, legend=3, colors='black,yellow,red', scatter_kwargs={'s':3, 'edgecolor': None})
    else:
        plt.scatter(x=dataX, y=dataY, s=3, c=gradiant)
        plt.legend(handles=make_legend(colors))

    # Make line of best fit
    totalm = np.polyfit(dataX, dataY, 1)
    plt.plot(dataX, totalm[0] * dataX + totalm[1], 'b')

    # Generate and return the plot
    ax.set_title(str(dataOptionX) + " for " + str(nodeOptionX) + " vs " + str(dataOptionY) + " for " + str(nodeOptionY))
    ax.set_ylabel(str(nodeOptionY) + " " + str(dataOptionY))
    ax.set_xlabel(str(nodeOptionX) + " " + str(dataOptionX))
    ax.axhline(y=0, lw=1.5, color='k')
    ax.axvline(x=0, lw=1.5, color='k')
    ax.set_xlim(left=-10)
    ax.set_ylim(bottom=-10)

    plt.grid()

    return fig

def make_legend(colors):
    color_one = mpatches.Patch(color=colors[0], label='To 1')
    color_two = mpatches.Patch(color=colors[1], label='1 To 5')
    color_three = mpatches.Patch(color=colors[2], label='5 To')
    return [color_one, color_two, color_three]


    #SPLITTER BACKUP
    if doColor and False:
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
        ax.set(xlim=(xmin - (abs(xmin) / 10), xmax + (abs(xmin) / 10)),
               ylim=(ymin - (abs(ymin) / 10), ymax + (abs(ymin) / 10)))