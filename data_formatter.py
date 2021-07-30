import datetime
import pandas as pd

# Format dataframe for further calculations
def names_and_format(df):
    # Two weeks ago
    oldday = datetime.datetime.today()-datetime.timedelta(days=14)
    # Remove zero shadow prices in a dataframe copy
    df2 = df[df.Shadow != 0].copy()
    # Keep dataframe points from last two weeks, keeping unique constraint names
    df2 = df2[df2['PriceDate'] >= oldday.strftime("%Y-%m-%d")]
    df2 = df2.Cons_name.unique()
    df2.sort()

    # Calculate the percentage in the original dataframe
    df['Percentage'] = df['Shadow'] / df.groupby(['PriceDate', 'Hour'])['Shadow'].transform('sum')

    # Sort and return
    df.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df2, df

# Make an array of arrays with the data option selected at each point
def make_table_matrix(frame, dp1, dp2, dataOption):
    # Create the bins and buckets, and transform to list
    buckets1, bins1 = pd.cut(frame[dp1], 15, retbins=True, include_lowest=True)
    buckets2, bins2 = pd.cut(frame[dp2], 15, retbins=True, include_lowest=True)
    bins1 = list(bins1)
    bins2 = list(bins2)
    avgs = []
    colors = []

    # Add 0s for formatting
    bins1.insert(0,0)
    bins2.insert(0,0)

    # Go through bins of first averages
    for i in range(len(bins1))[1:]:
        # Add a new color and average for every new bucket
        avgs.append([])
        colors.append([])
        # go through the other bucket
        for j in range(len(bins2))[1:]:
            # Get the parts of the dataframe that is within the two averages
            temp = frame[((frame[dp1] >= bins1[i-1]) & (frame[dp1] < bins1[i])) & ((frame[dp2] >= bins2[j-1]) & (frame[dp2] < bins2[j]))]
            # If they exist
            if not temp.empty:
                # If it's mean or median, select one
                if dataOption == 'mean':
                    avgs[-1].append(int(temp['PricePoint'].mean()))
                else:
                    avgs[-1].append(int(temp['PricePoint'].median()))

                # Color them as relevant
                if avgs[-1][-1] > 2.0:
                    colors[-1].append('turquoise')
                else:
                    colors[-1].append('tomato')
            else:
                # Otherwise color it tomato
                avgs[-1].append(" ")
                colors[-1].append('tomato')

    # Turn them into INTs
    for i in range(len(bins1)):
        bins1[i] = int(bins1[i])
        bins2[i] = int(bins2[i])

    # Add the labels
    for i in range(len(bins1)):
        bins1[i] = "TO " + str(bins1[i])
        bins2[i] = "TO " + str(bins2[i])

    # Return
    return [bins1, bins2], avgs, colors
