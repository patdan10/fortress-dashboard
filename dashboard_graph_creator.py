from matplotlib import pyplot as plt
# Return the scatterplot with the correct axes and filters
def scatter_matplot_returner(dataX, dataY, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY):
    dataX = dataX.map(lambda x: float(x))
    dataY = dataY.map(lambda x: float(x))
    
    # Generate unmarked chart
    fig, ax = plt.subplots()
    ax.axhline(y=0, lw=1.5, color='k')
    ax.axvline(x=0, lw=1.5, color='k')

    plt.plot(dataX, dataY, 'o')
    m = np.polyfit(dataX, dataY, 1)
    plt.plot(dataX, m[0] * dataX + m[1])

    # Generate and return the plot
    ax.set_title(str(dataOptionX) + " for " + str(nodeOptionX) + " vs " + str(dataOptionY) + " for " + str(nodeOptionY))
    ax.set_ylabel(str(nodeOptionY) + " " + str(dataOptionY))
    ax.set_xlabel(str(nodeOptionX) + " " + str(dataOptionX))
    plt.grid()
    return fig
