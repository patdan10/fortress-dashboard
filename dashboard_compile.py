import pandas as pd, streamlit as st
import congestion_database_pull, nodes_database_pull, dashboard_graph_creator, weather_temperature_pull, filter_finder, data_formatter
import streamlit.components.v1 as components

# Dashboard compilation
def compile():
    # The node options, along with helper lists below.
    nodeOptions = ['Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 'DA-RT', 'RT-DA', 'Spread', 'Net Demand']
    nodeOptionsX = ['Sum of All Wind', 'Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'DA-RT', 'RT-DA', 'Spread', 'Net Demand']
    nodeOptionsY = ['Net Demand', 'Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 'DA-RT', 'RT-DA', 'Spread']
    nodeExclusive = ['DA-RT', 'RT-DA', 'DALMP']
    components = {'DA-RT': ['DALMP', 'RTLMP'], 'RT-DA': ['RTLMP', 'DALMP'], 'Spread': ['DALMP', 'RTLMP', 'RTLMP', 'DALMP'], 'DALMP': ['DALMP']}
    colors = [[0.502,0.502,0.502],[1,1,0],[1,0,0]]
        
    # Get the constraints, nodes, and iems, which are all cached
    cons, total = congestion_database_pull.get_constraints()
    nodes = nodes_database_pull.get_node_names()
    iems = weather_temperature_pull.get_iems().sort_values(by='IEMs')

    # Titles
    st.title("Constraints Data Visualizer")
    st.header("Constraint Selector")

    # Choose constraint
    conSelect = st.selectbox(
        "Which Constraint?",
        cons
    )

    # Get the constraint information, and the mins and maxes of it
    row = total[total['Cons_name'] == conSelect]
    row = row.loc[row['Percentage'].idxmax()]
    minimaxes = congestion_database_pull.get_minimaxes(row)

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


    # Write the X selector
    st.header("X Data Selector")

    # Pick the information
    nodeSelectX, dataX, dataSelectX = info_picker(nodeOptionsX, iems, nodeExclusive, allNodes, components, nodes, "X")

    # Filter the data if selected
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

    # Pick the colors based on the DA-RT, RT-DA or the Spread of nodes
    st.subheader("Color Picker")
    colorData = color_picker(allNodes, nodes, components, colors)
    frame = pd.merge(frame, colorData, how='left', on=['PriceDate', 'Hour'])
    frame.dropna(axis=0, how='any', inplace=True)

    # Create classification regions if desired
    st.subheader("Region Maker")
    doRegions = st.checkbox("Do you want to create regions?")
    if doRegions:
        kernel = st.selectbox(
            "Which Computation Method?",
            ['Linear', 'Polynomial', 'Radial', 'Sigmoid', 'Logistic', 'Random Forest', 'Gaussian']
        )
    else:
        kernel = 'Linear'

    # Set color for information
    if not doRegions:
        frame['Color'] = frame['PricePoint'].map(lambda x: colors[0] if x < 1 else (colors[1] if x < 5 else colors[2]))
    else:
        frame['Color'] = frame['PricePoint'].map(lambda x: 0 if x < 1 else (1 if x < 5 else 2))

    # Make the scatterplot and plot it
    plot = dashboard_graph_creator.scatter_matplot_returner(frame[dataSelectX], frame[dataSelectY], nodeSelectX, nodeSelectY, dataSelectX, dataSelectY, frame['Color'], colors, doRegions, kernel)
    st.pyplot(plot)

    # Convert to floats
    frame[dataSelectX] = frame[dataSelectX].map(lambda x: float(x))
    frame[dataSelectY] = frame[dataSelectY].map(lambda x: float(x))


    # Make Seaborns chart
    bins, df, colors = data_formatter.make_seaborn_matrix(frame, dataSelectX, dataSelectY)
    #fontsize = st.number_input("Fontsize?")
    plot = dashboard_graph_creator.bucket_chart_maker(bins, df, nodeSelectX, nodeSelectY, dataSelectX, dataSelectY, colors)
    st.pyplot(plot)

    # Get the correlation and write it
    pearson = frame[dataSelectX].corr(frame[dataSelectY])
    st.write("Correlation between Data: " + str(pearson))



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
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectShort].iloc[0]['Node_ID'], bit, dataSelect)
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
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectLong].iloc[0]['Node_ID'], bit, dataSelect)
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
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelect].iloc[0]['Node_ID'],bit, dataSelect)
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
        data = weather_temperature_pull.get_temperature(nodeSelect)
    elif dataSelect == 'Station Wind':
        # If wind temperatuer
        nodeSelect = st.selectbox(
            "Which IEM for Wind for " + point + "?",
            iems
        )
        # Select wind at certain point
        data = weather_temperature_pull.get_wind(nodeSelect)
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
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelect].iloc[0]['Node_ID'],
                                                     bit, dataSelect)
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
            temp = nodes_database_pull.get_node_info(
                nodes.loc[nodes['NodeName'] == nodeSelectShort].iloc[0]['Node_ID'], bit, dataSelect)
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
            temp = nodes_database_pull.get_node_info(
                nodes.loc[nodes['NodeName'] == nodeSelectLong].iloc[0]['Node_ID'], bit, dataSelect)
            
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
