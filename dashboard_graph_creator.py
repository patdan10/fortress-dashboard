from matplotlib import pyplot as plt
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
