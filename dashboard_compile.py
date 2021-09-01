import pandas as pd, streamlit as st
import congestion_database_pull, nodes_database_pull, dashboard_graph_creator, weather_temperature_pull, filter_finder, data_formatter, cons_to_states, node_prioritizer
import datetime




# Dashboard compilation
def compile():
    time_until_end_of_day()
    # The node options, along with helper lists below.
    nodeOptions = ['Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 'DA-RT', 'RT-DA', 'Spread', 'Net Demand']
    nodeOptionsX = ['Sum of All Wind', 'Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'DA-RT', 'RT-DA', 'Spread', 'Net Demand']
    nodeOptionsY = ['Net Demand', 'Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 'DA-RT', 'RT-DA', 'Spread']
    nodeExclusive = ['DA-RT', 'RT-DA', 'DALMP']
    components = {'DA-RT': ['DALMP', 'RTLMP'], 'RT-DA': ['RTLMP', 'DALMP'], 'Spread': ['DALMP', 'RTLMP', 'RTLMP', 'DALMP'], 'DALMP': ['DALMP']}
    descriptors = {'Linear': 'Good for analyzing discrete classes, but easily oversimplifies',
                   'Polynomial': 'Provides generally good results, but very sensitive to outliers',
                   'Radial': 'Good tolerance for noise and generalization, but classifies only in ellipsoid areas',
                   'Sigmoid': 'Can handle discrete classes well, but struggles on more complicated problems',
                   'Logistic': 'Great at classifying less classes, but struggles on more complicated problems',
                   'Random Forest': 'Great at large datasets, but limited outside of highly populated areas',
                   'Gaussian': 'Good at handling multiple classes, but is very repulsed by ovelapping, perhaps overcompensating'}
    colors = [[0.502,0.502,0.502],[1,1,0],[1,0,0]]
    locations = {'OKC': ['OKC', 'GOK', 'OJA', 'RCE', '1F0'],
    'KAN': ['MKC', 'OWI', 'STJ', 'SLN', 'MYZ'],
    'DAK': ['BKX', 'ABR', 'GFK', 'DIK', 'MOT'],
    'NEB': ['BBW'],
    'TEX': ['HRX', 'AMA']}
    states = cons_to_states.cons
    bar = st.progress(0)
    pd.set_option('display.max_columns', None)

    all_iems = ['OKC', 'GOK', 'OJA', 'RCE', '1F0', 'MKC', 'OWI', 'STJ', 'SLN', 'MYZ', 'BKX', 'ABR', 'GFK', 'DIK', 'MOT', 'BBW', 'HRX', 'AMA']


    # Get the constraints, nodes, and iems, which are all cached
    cons, total = congestion_database_pull.get_constraints()
    nodes = nodes_database_pull.get_node_names()
    iems = weather_temperature_pull.get_iems().sort_values(by='IEMs')
    weekAgo = datetime.datetime.today() - datetime.timedelta(weeks=1)

    # Titles
    st.title("Constraints Data Visualizer")
    st.header("Constraint Selector")


    doPrioritize = st.checkbox("Do you want to rank constraints?")
    if doPrioritize or True:

        # Get weather forecasts
        fc = weather_temperature_pull.get_forecast(datetime.datetime.today()+datetime.timedelta(days=1))
        uniquedatetimes = pd.DataFrame(fc['PriceDate'].drop_duplicates())
        uniquedatetimes['DateID'] = range(len(uniquedatetimes.index))
        fc = pd.merge(fc, uniquedatetimes, on=['PriceDate'])

        # Get nodes information and weather station information, in order to match
        nodesPos = all_nodes_getter(cons, total, weekAgo)
        priorities = get_locations(locations, weekAgo).dropna()

        # Merge weather station and node information so we can match them
        bigData = pd.merge(nodesPos, priorities, on=['PriceDate', 'Hour'])

        # Merge dates with location information to create granularity
        uniquedatetimes = pd.DataFrame(priorities['PriceDate'].drop_duplicates())
        uniquedatetimes['DateID'] = range(len(uniquedatetimes.index))





        # potentially valueless. Figure it out.
        #priorities = pd.merge(priorities, uniquedatetimes, on=['PriceDate'])
        """scoresByHour = [[],[],[],[],[],[],[],[]]
        # Get IEM likelyhood
        for i in all_iems:
            mergedDays = pd.merge(fc, priorities[priorities['IEM']==i], on=['DateID', 'Hour', 'IEM'])
            mergedDays['score'] = mergedDays['Station Wind_y'] - mergedDays['Station Wind_x'] + mergedDays['Station Temperature_y'] - mergedDays['Station Temperature_x']
            hours = mergedDays.groupby(by=['Hour'])
            for index, row in hours:
                scoresByHour[int(index/3)].append((mergedDays.iloc[0]['IEM'], row))"""



        # Set ups with IEMs and get unique constraints
        nodeswithiems = []
        counter = 0
        unicon = bigData['Constraint'].unique()

        # For each unique constraint
        for c in unicon:
            # Progress bar
            counter += 1
            percent = (float(counter) / float(len(unicon)))
            bar.progress(percent)

            # If its not in constraints, go on
            if c not in states.keys():
                continue

            # Get the data for the constraint and the score for it, and append that
            nodeData = bigData[(bigData['Constraint'] == c) & (bigData['Region'] == states[c])]
            absol = node_prioritizer.line_fit(nodeData, fc)
            temp = [c, states[c], absol[0], absol[1]]
            nodeswithiems.append(temp)

        # Sort the scores and set the constraints in order
        nodeswithiems = pd.DataFrame(nodeswithiems, columns=['Constraint', 'State', 'IEM', 'Score']).sort_values(by='Score', ascending=True)
        cons = nodeswithiems['Constraint']



    # End of Tab





    # Choose constraint
    conSelect = st.selectbox(
        "Which Constraint?",
        cons
    )

    # Get the constraint information, and the mins and maxes of it
    row = total[total['Cons_name'] == conSelect]
    row = row.loc[row['Percentage'].idxmax()]
    minimaxes = congestion_database_pull.get_minimaxes(row, 5, False)

    # Format minimaxes
    minimaxes[0]['Percentage'] = row['Percentage'] * 100
    minimaxes[1]['Percentage'] = row['Percentage'] * 100
    for m in minimaxes:
        m['PriceDate'] = m['PriceDate'].map(lambda x: x.strftime("%Y-%m-%d"))
    minimaxes[1]['MinimumMCC'] = minimaxes[1]['MinimumMCC'].map(lambda x: float(x))
    minimaxes[0]['MaximumMCC'] = minimaxes[0]['MaximumMCC'].map(lambda x: float(x))

    # Write the mins and maxes
    st.write(minimaxes[1])
    st.write(minimaxes[0])

    # Set up the nodes list with the mins and maxes at the top in order
    pt1 = minimaxes[1]['Node'].values.tolist()
    pt2 = minimaxes[0]['Node'].values.tolist()
    allNodes = nodes['NodeName'].copy()
    allNodes.sort_values(inplace=True)
    allNodes = list(allNodes)

    # Remove them
    for i in range(len(pt1)):
        allNodes.remove(pt1[i])
        allNodes.remove(pt2[i])

    # Add them at the top
    for i in range(len(pt1))[::-1]:
        allNodes = [pt1[i]] + allNodes
        allNodes = [pt2[i]] + allNodes












    st.markdown("---")
    # Write the X selector
    st.header("X Data Selector")

    # Pick the information
    nodeSelectX, dataX, dataSelectX = info_picker(nodeOptionsX, iems, nodeExclusive, allNodes, components, nodes, "X")

    # Filter the data if selected
    st.markdown("---")
    st.subheader("X Data Filter")
    doFilter = st.checkbox("Do you want to filter X?")

    # If filtered
    if doFilter:
        # Filter the info
        tempy = filter(dataX, nodeOptions+['DALMP'], "X", iems, nodeExclusive, allNodes, components, nodes)

        # If it works, do it. If not, write no filter
        if len(tempy) == 0:
            st.write("No Filter")
        else:
            dataX = tempy


    # Same selection for Y
    st.markdown("---")
    st.header("Y Data Selector")

    # Pick info for Y
    nodeSelectY, dataY, dataSelectY = info_picker(nodeOptionsY, iems, nodeExclusive, allNodes, components, nodes, "Y")

    # Filter option
    st.subheader("Y Data Filter")
    doFilter = st.checkbox("Do you want to filter Y?")

    # If filtered
    if doFilter:
        # Filter the info
        tempy = filter(dataY, nodeOptions+['DALMP'], "Y", iems, nodeExclusive, allNodes, components, nodes)

        # If it works, do it. If not, write no filter
        if len(tempy) == 0:
            st.write("No Filter")
        else:
            dataY = tempy


    # Merge the information into one frame
    frame = pd.merge(dataX, dataY, how='left', on=['PriceDate', 'Hour'])
    frame.dropna(axis=0, how='any', inplace=True)

    # If they are the same, add the endings
    if dataSelectX == dataSelectY:
        dataSelectX += '_x'
        dataSelectY += '_y'

    st.markdown("---")
    st.subheader("Date Filter")
    doDates = st.checkbox("Do you want to filter by Dates?")

    if doDates:
        start = st.date_input('Start Date')
        end = st.date_input('End Date')
        frame = frame.loc[(frame['PriceDate'] >= start) & (frame['PriceDate'] <= end)]

    # Pick the colors based on the DA-RT, RT-DA or the Spread of nodes
    st.markdown("---")
    st.subheader("Color Picker")
    colorData = color_picker(allNodes, nodes, components, colors)
    frame = pd.merge(frame, colorData, how='left', on=['PriceDate', 'Hour'])
    frame.dropna(axis=0, how='any', inplace=True)

    # Create classification regions if desired
    st.markdown("---")
    st.subheader("Region Maker")
    doRegions = st.checkbox("Do you want to create regions?")
    if doRegions:
        kernel = st.selectbox(
            "Which Computation Method?",
            ['Linear', 'Polynomial', 'Radial', 'Sigmoid', 'Logistic', 'Random Forest', 'Gaussian']
        )
        st.write(descriptors[kernel])
    else:
        kernel = 'Linear'

    # Set color for information
    if not doRegions:
        frame['Color'] = frame['PricePoint'].map(lambda x: colors[0] if x < 1 else (colors[1] if x < 5 else colors[2]))
    else:
        frame['Color'] = frame['PricePoint'].map(lambda x: 0 if x < 1 else (1 if x < 5 else 2))

    # Make the scatterplot and plot it
    plot, work = dashboard_graph_creator.scatter_matplot_returner(frame[dataSelectX], frame[dataSelectY], nodeSelectX, nodeSelectY, dataSelectX, dataSelectY, frame['Color'], colors, doRegions, kernel)
    if work == False:
        st.write("Need more than 1 price class to create regions")
    st.markdown("---")
    st.pyplot(plot)
    st.markdown("---")

    # Convert to floats
    frame[dataSelectX] = frame[dataSelectX].map(lambda x: float(x))
    frame[dataSelectY] = frame[dataSelectY].map(lambda x: float(x))


    # Get the correlation and write it
    pearson = frame[dataSelectX].corr(frame[dataSelectY])
    st.write("Correlation between Data: " + str(pearson))


    # Make Seaborn chart of Means
    st.markdown("---")
    st.subheader("MEAN")
    bins, df, colors = data_formatter.make_table_matrix(frame, dataSelectX, dataSelectY, 'mean')
    plot = dashboard_graph_creator.bucket_chart_maker(bins, df, nodeSelectX, nodeSelectY, dataSelectX, dataSelectY, colors)
    st.pyplot(plot)

    # Make Seaborn chart of Medians
    st.markdown("---")
    st.subheader("MEDIAN")
    bins, df, colors = data_formatter.make_table_matrix(frame, dataSelectX, dataSelectY, 'median')
    plot = dashboard_graph_creator.bucket_chart_maker(bins, df, nodeSelectX, nodeSelectY, dataSelectX, dataSelectY, colors)
    st.pyplot(plot)



# Get the colors for the nodes
def color_picker(allNodes, nodes, components, colors):
    dataSelect = st.selectbox(
        "Which datapoint to color by?",
        ("DA-RT", "RT-DA", "Spread")
    )

    # Depending on the selected point, get different information. If spread, do this
    if dataSelect == 'Spread':
        # Choose long node
        nodeSelectShort = st.selectbox(
            "Which Node Long?",
            allNodes
        )
        data = pd.DataFrame()

        # Get DA-RT for Long
        for bit in components['DA-RT']:
            # Get data for Long node
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectShort].iloc[0]['Node_ID'], bit, dataSelect, "")
            # If gotten correctly, put it in the dataframe
            if data.empty:
                temp = temp.rename(columns={dataSelect: 'PricePoint'})
                data = temp
            else:
                temp = temp.rename(columns={dataSelect: 'PricePoint'})
                data["PricePoint"] -= temp["PricePoint"]


        # Choose short node
        nodeSelectLong = st.selectbox(
            "Which Node Short?",
            allNodes
        )
        dataTemp = pd.DataFrame()

        # Get RT-DA for Short
        for bit in components['RT-DA']:
            # Get data for Short node
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectLong].iloc[0]['Node_ID'], bit, dataSelect, "")
            # If gotten correctly, put it in dataframe
            if dataTemp.empty:
                temp = temp.rename(columns={dataSelect: 'PricePoint'})
                dataTemp = temp
            else:
                temp = temp.rename(columns={dataSelect: 'PricePoint'})
                dataTemp["PricePoint"] -= temp["PricePoint"]
        # Add long and short together for spread
        data["PricePoint"] += dataTemp["PricePoint"]
    else:
        # If DA-RT or RT-DA
        # Select Node
        nodeSelect = st.selectbox(
            "Which Node?",
            allNodes
        )
        data = pd.DataFrame()

        # For componant in data selected
        for bit in components[dataSelect]:
            # Get the bit of information
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelect].iloc[0]['Node_ID'],bit, dataSelect, "")
            if data.empty:
                # If the first one, then set it first
                temp = temp.rename(columns={dataSelect: 'PricePoint'})
                data = temp
            else:
                # If the second one, then subtract it
                temp = temp.rename(columns={dataSelect: 'PricePoint'})
                data["PricePoint"] -= temp["PricePoint"]

    return data




# Information getter
def info_picker(nodeOptions, iems, nodeExclusive, allNodes, components, nodes, point):
    # Choose piece of information
    dataSelect = st.selectbox(
        "Which Info On " + point + "?",
        nodeOptions
    )

    # If teemperature
    if dataSelect == 'Station Temperature':
        nodeSelect = st.selectbox(
            "Which IEM for Temperature for " + point + "?",
            iems
        )
        # Select temperature at chosen point
        data = weather_temperature_pull.get_temperature(nodeSelect, datetime.datetime.strptime("2020-01-01", '%Y-%m-%d'))
    elif dataSelect == 'Station Wind':
        # If wind temperatuer
        nodeSelect = st.selectbox(
            "Which IEM for Wind for " + point + "?",
            iems
        )
        # Select wind at certain point
        data = weather_temperature_pull.get_wind(nodeSelect, datetime.datetime.strptime("2020-01-01", '%Y-%m-%d'))
    elif dataSelect in nodeExclusive:
        # If it needs a node
        nodeSelect = st.selectbox(
            "Which Node On " + point + "?",
            allNodes
        )
        data = pd.DataFrame()
        # Get the relevant bit information at each node
        for bit in components[dataSelect]:
            # Get the information
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelect].iloc[0]['Node_ID'], bit, dataSelect, "")
            # Select information and subtract it
            if data.empty:
                data = temp
            else:
                data[dataSelect] -= temp[dataSelect]
    elif dataSelect == 'Spread':
        # If it's spread, get long and short
        nodeSelectShort = st.selectbox(
            "Which Node Long On " + point + "?",
            allNodes
        )
        data = pd.DataFrame()

        # Get the DA-RT information
        for bit in components['DA-RT']:
            # Get bit of information, and select it
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectShort].iloc[0]['Node_ID'], bit, dataSelect, "")
            if data.empty:
                data = temp
            else:
                data[dataSelect] -= temp[dataSelect]

        # Select short node
        nodeSelectLong = st.selectbox(
            "Which Node Short On " + point + "?",
            allNodes
        )
        dataTemp = pd.DataFrame()

        # Get the RT-DA information
        for bit in components['RT-DA']:
            # Get bit of information
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectLong].iloc[0]['Node_ID'], bit, dataSelect, "")

            # Select information and subtract
            if dataTemp.empty:
                dataTemp = temp
            else:
                dataTemp[dataSelect] -= temp[dataSelect]

        # Add them together
        data[dataSelect] += dataTemp[dataSelect]
        nodeSelect = nodeSelectShort + " and " + nodeSelectLong
    else:
        # Otherwise, put get information
        nodeSelect = "All"
        data = weather_temperature_pull.get_information(dataSelect)

    return nodeSelect, data, dataSelect






# Filter the information
def filter(data, nodeOptions, point, iems, nodeExclusive, allNodes, components, nodes):
    # Get info to filter
    node, toShow, dataName = info_picker(nodeOptions[:-4]+[nodeOptions[-1]], iems, nodeExclusive, allNodes, components, nodes, "Filter " + point)
    st.write(toShow[dataName].dropna(axis=0, how='any').sort_values().reset_index(drop=True))

    # Select direction to filter
    direction = st.selectbox(
        "Which direction to filter on " + point + "?",
        ("Greater Than", "Less Than", "Equal To")
    )

    # Select the limit
    limit = st.number_input("What is the limit on " + point + "?")

    # Make filter and get dates
    filterDates = filter_finder.filter_helper(dataName, direction, limit, node)

    # If you get dates, merge them
    if len(filterDates) != 0:
        data = pd.merge(filterDates, data, left_on=['PriceDate', 'Hour'], right_on=['PriceDate', 'Hour'])
    else:
        st.write("Failure")

    # Sort and drop values
    data.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    data.dropna(axis=0, how='any', inplace=True)
    return data



@st.cache(suppress_st_warning=True)
def get_locations(locations, weekAgo):
    priorities = pd.DataFrame()
    for loc in locations.keys():
        for n in locations[loc]:
            if priorities.empty:
                priorities = pd.merge(weather_temperature_pull.get_wind(n, weekAgo), weather_temperature_pull.get_temperature(n, weekAgo), how='left', on=['PriceDate', 'Hour'])
                priorities['Region'] = loc
                priorities['IEM'] = n
            else:
                merged = pd.merge(weather_temperature_pull.get_wind(n, weekAgo), weather_temperature_pull.get_temperature(n, weekAgo), how='left', on=['PriceDate', 'Hour'])
                merged['Region'] = loc
                merged['IEM'] = n
                priorities = pd.concat([priorities, merged], ignore_index=True)

    return priorities.reset_index(drop=True)



def time_until_end_of_day():
    dt = datetime.datetime.now()
    tomorrow = dt + datetime.timedelta(days=1)
    temp = datetime.datetime.combine(tomorrow, datetime.time.min) - dt
    return temp.total_seconds()

@st.cache(ttl=6000)
def all_nodes_getter(cons, total, weekAgo):
    nodesAffectedPos = pd.DataFrame()
    weekAgo = weekAgo-datetime.timedelta(days=75)

    for c in cons:
        r = total[total['Cons_name'] == c]
        r = r.loc[r['Percentage'].idxmax()]
        minimaxesTemp = congestion_database_pull.get_minimaxes(r, 1, True)[0]
        node = minimaxesTemp.iloc[0]['Node']
        minimaxesTemp = nodes_database_pull.get_node_info(minimaxesTemp.iloc[0]['ID'], 'rtlmp', 'RTLMP', " AND p.pricedate>='"+weekAgo.strftime("%Y-%m-%d")+"'")

        if type(minimaxesTemp) == type(False):
            continue

        minimaxesTemp['Node'] = node
        minimaxesTemp['Constraint'] = c
        if nodesAffectedPos.empty:
            nodesAffectedPos = minimaxesTemp
        else:
            nodesAffectedPos = pd.concat([nodesAffectedPos, minimaxesTemp], ignore_index=True)

    nodesAffectedPos.dropna(inplace=True)
    nodesAffectedPos['RTLMP'] = nodesAffectedPos['RTLMP'].map(lambda x: float(x))

    return nodesAffectedPos
