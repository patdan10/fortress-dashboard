from matplotlib import pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from mlxtend.plotting import plot_decision_regions
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
# Return the scatterplot with the correct axes and filters

# The region creation ML algorithms
kernels = {'Linear': 'linear', 'Polynomial': 'poly', 'Radial': 'rbf', 'Sigmoid': 'sigmoid'}
classifiers = {'Logistic': LogisticRegression(random_state=1,solver='newton-cg',multi_class='multinomial'),
               'Random Forest':  RandomForestClassifier(random_state=1, n_estimators=100),
               'Gaussian': GaussianNB()}

# Create a matplot scatter chart
def scatter_matplot_returner(dataX, dataY, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY, gradiant, colors, doRegions, algorithm):
    # Map data to floats
    dataX = dataX.map(lambda x: float(x))
    dataY = dataY.map(lambda x: float(x))

    # Generate unmarked chart
    fig, ax = plt.subplots()
    
    # If regions are online, apply them
    if doRegions:
        # Format to numpy
        gradiant = gradiant.to_numpy().astype(np.integer)
        totalData = []
        dataXList = dataX.to_numpy()
        dataYList = dataY.to_numpy()

        # Append numpy arrays to list, then convert that to numpy
        for i in range(len(dataXList)):
            totalData.append(np.array([dataXList[i], dataYList[i]]))
        totalData = np.array(totalData)

        # If the chosen algorithm is a kerenel, apply it. Otherwise, use the correct algorithm
        if algorithm in kernels.keys():
            clf = SVC(C=0.5, kernel=kernels[algorithm])
        else:
            clf = classifiers[algorithm]

        # Fit the data
        clf.fit(totalData, gradiant)
        # Plotting decision regions
        plot_decision_regions(totalData, gradiant, clf=clf, legend=3, colors='black,yellow,red', scatter_kwargs={'s':3, 'edgecolor': None})
    else:
        # If not regions, scattere with gradiants as normal
        plt.scatter(x=dataX, y=dataY, s=3, c=gradiant)
        plt.legend(handles=make_legend(colors))

    # Make line of best fit
    totalm = np.polyfit(dataX, dataY, 1)
    plt.plot(dataX, totalm[0] * dataX + totalm[1], 'b')

    # Format the actual chart itself
    ax.set_title(str(dataOptionX) + " for " + str(nodeOptionX) + " vs " + str(dataOptionY) + " for " + str(nodeOptionY))
    ax.set_ylabel(str(nodeOptionY) + " " + str(dataOptionY))
    ax.set_xlabel(str(nodeOptionX) + " " + str(dataOptionX))
    ax.axhline(y=0, lw=1.5, color='k')
    ax.axvline(x=0, lw=1.5, color='k')
    ax.set_xlim(left=-10)
    ax.set_ylim(bottom=-10)
    plt.grid()

    return fig

# If a legend is necessary, create one with the correct colors
def make_legend(colors):
    # The three colors, create them in a format where the legend can be interpreted
    color_one = mpatches.Patch(color=colors[0], label='To 1')
    color_two = mpatches.Patch(color=colors[1], label='1 To 5')
    color_three = mpatches.Patch(color=colors[2], label='5 To')
    return [color_one, color_two, color_three]


# Make a seaborn chart of the matrices
def bucket_chart_maker(bins, df, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY, colors):
    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df, cellColours=colors, loc='center', rowLabels=bins[1][1:], colLabels=bins[0][1:], fontsize=fontsize)
    the_table.auto_set_font_size(False)
    the_table.scale(2.5,1.5)
    ax.set_title(str(dataOptionX) + " for " + str(nodeOptionX) + " vs " + str(dataOptionY) + " for " + str(nodeOptionY))

    return fig