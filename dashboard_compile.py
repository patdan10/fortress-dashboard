import pandas as pd, streamlit as st
import congestion_database_pull, nodes_database_pull, dashboard_graph_creator, weather_temperature_pull, filter_finder
from streamlit import caching

# 'Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 
# 'Sum of All Wind', 

def compile():
    nodeOptions = ['Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 'DA-RT', 'RT-DA', 'Spread']
    nodeExclusive = ['DA-RT', 'RT-DA', 'DALMP']
    components = {'DA-RT': ['DALMP', 'RTLMP'], 'RT-DA': ['RTLMP', 'DALMP'], 'Spread': ['DALMP', 'RTLMP', 'RTLMP', 'DALMP'], 'DALMP': ['DALMP']}

    # If password, enter the dataframe
    password = st.text_input("Password: ")
    if password == "constraint123":
        cons = congestion_database_pull.get_constraints()
        nodes = nodes_database_pull.get_node_names()
        iems = weather_temperature_pull.get_iems().sort_values(by='IEMs')

        st.title("Constraints Data Visualizer")

        st.header("Constraint Selector")

        # Choose based on regex
        conSelect = st.selectbox(
            "Which Constraint?",
            cons['Cons_name'].sort_values()
        )
        row = cons.loc[cons['Cons_name'] == conSelect]
        minimaxes = congestion_database_pull.get_minimaxes(row['PriceDate'].iloc[0], (row['Hour'].iloc[0].item()))

        st.write(minimaxes[1])
        st.write(minimaxes[0])

        pt1 = minimaxes[1]['Node'].values.tolist()
        pt2 = minimaxes[0]['Node'].values.tolist()
        allNodes = nodes['NodeName'].copy()
        allNodes.sort_values(inplace=True)
        allNodes = list(allNodes)

        for i in range(len(pt1)):
            allNodes.remove(pt1[i])
            allNodes.remove(pt2[i])

        for i in range(len(pt1))[::-1]:
            allNodes = [pt1[i]] + allNodes
            allNodes = [pt2[i]] + allNodes







        st.header("X Data Selector")
        nodeSelectX, dataX, dataSelectX = info_picker(nodeOptions, iems, nodeExclusive, allNodes, components, nodes, "X")

        st.subheader("X Data Filter")
        doFilter = st.checkbox("Do you want to filter X?")
        if doFilter:
            tempy = filter(dataX, nodeOptions+['DALMP'], "X", iems, nodeExclusive, allNodes, components, nodes)
            if len(tempy) == 0:
                st.write("No Filter")
            else:
                dataX = tempy

        st.subheader("X Data")
        st.write(dataX[dataSelectX].sort_values().reset_index(drop=True))






        st.header("Y Data Selector")
        nodeSelectY, dataY, dataSelectY = info_picker(nodeOptions, iems, nodeExclusive, allNodes, components, nodes, "Y")

        st.subheader("Y Data Filter")
        doFilter = st.checkbox("Do you want to filter Y?")
        if doFilter:
            tempy = filter(dataY, nodeOptions+['DALMP'], "Y", iems, nodeExclusive, allNodes, components, nodes)
            if len(tempy) == 0:
                st.write("No Filter")
            else:
                dataY = tempy

        st.subheader("Y Data")
        st.write(dataY[dataSelectY].sort_values().reset_index(drop=True))






        frame = pd.merge(dataX, dataY, how='left', on=['PriceDate', 'Hour'])
        frame.dropna(axis=0, how='any', inplace=True)

        if dataSelectX == dataSelectY:
            dataSelectX += '_x'
            dataSelectY += '_y'
        plot = dashboard_graph_creator.scatter_matplot_returner(frame[dataSelectX], frame[dataSelectY], nodeSelectX, nodeSelectY, dataSelectX, dataSelectY)
        st.pyplot(plot)






def info_picker(nodeOptions, iems, nodeExclusive, allNodes, components, nodes, point):
    # Choose based on regex
    dataSelect = st.selectbox(
        "Which Info On " + point + "?",
        nodeOptions
    )

    if dataSelect == 'Station Temperature':
        nodeSelect = st.selectbox(
            "Which IEM for Temperature for " + point + "?",
            iems
        )
        data = weather_temperature_pull.get_temperature(nodeSelect)
    elif dataSelect == 'Station Wind':
        nodeSelect = st.selectbox(
            "Which IEM for Wind for " + point + "?",
            iems
        )
        data = weather_temperature_pull.get_wind(nodeSelect)
    elif dataSelect in nodeExclusive:
        nodeSelect = st.selectbox(
            "Which Node On " + point + "?",
            allNodes
        )
        data = pd.DataFrame()
        for bit in components[dataSelect]:
            temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelect].iloc[0]['Node_ID'],
                                                     bit, dataSelect)
            if data.empty:
                data = temp
            else:
                data[dataSelect] -= temp[dataSelect]
    elif dataSelect == 'Spread':
        nodeSelectShort = st.selectbox(
            "Which Node Long On " + point + "?",
            allNodes
        )
        data = pd.DataFrame()
        for bit in components['DA-RT']:
            temp = nodes_database_pull.get_node_info(
                nodes.loc[nodes['NodeName'] == nodeSelectShort].iloc[0]['Node_ID'], bit, dataSelect)
            if data.empty:
                data = temp
            else:
                data[dataSelect] -= temp[dataSelect]

        nodeSelectLong = st.selectbox(
            "Which Node Short On " + point + "?",
            allNodes
        )
        dataTemp = pd.DataFrame()
        for bit in components['RT-DA']:
            temp = nodes_database_pull.get_node_info(
                nodes.loc[nodes['NodeName'] == nodeSelectLong].iloc[0]['Node_ID'], bit, dataSelect)
            if dataTemp.empty:
                dataTemp = temp
            else:
                dataTemp[dataSelect] -= temp[dataSelect]
        data[dataSelect] += dataTemp[dataSelect]
        nodeSelect = nodeSelectShort + " and " + nodeSelectLong
    else:
        nodeSelect = "All"
        data = weather_temperature_pull.get_information(dataSelect)

    return nodeSelect, data, dataSelect







def filter(data, nodeOptions, point, iems, nodeExclusive, allNodes, components, nodes):
    # FILTER STUFF
    node, toShow, dataName = info_picker(nodeOptions[:-4]+[nodeOptions[-1]], iems, nodeExclusive, allNodes, components, nodes, "Filter " + point)
    st.write(toShow[dataName].dropna(axis=0, how='any').sort_values().reset_index(drop=True))

    direction = st.selectbox(
        "Which direction to filter on " + point + "?",
        ("Greater Than", "Less Than", "Equal To")
    )

    # Choose the limit
    limit = st.number_input("What is the limit on " + point + "?")
    filterDates = filter_finder.filter_helper(dataName, direction, limit, node)
    if len(filterDates) != 0:
        data = pd.merge(filterDates, data, left_on=['PriceDate', 'Hour'], right_on=['PriceDate', 'Hour'])
    else:
        st.write("Failure")
    data.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    data.dropna(axis=0, how='any', inplace=True)
    return data
