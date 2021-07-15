import pandas as pd, streamlit as st
import congestion_database_pull, nodes_database_pull, dashboard_graph_creator, weather_temperature_pull
from streamlit import caching

def compile():
    nodeOptions = ['Load', 'Station Temperature', 'Station Wind', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 'DA-RT', 'RT-DA', 'Spread']
    nodeExclusive = ['DA-RT', 'RT-DA']
    components = {'DA-RT': ['DALMP', 'RTLMP'], 'RT-DA': ['RTLMP', 'DALMP'], 'Spread': ['DALMP', 'RTLMP', 'RTLMP', 'DALMP']}

    # If password, enter the dataframe
    password = st.text_input("Password: ")
    if password == "constraint123" or True:
        cons = congestion_database_pull.get_constraints()
        nodes = nodes_database_pull.get_node_names()
        iems = weather_temperature_pull.get_iems()

        st.title("Constraints Data Visualizer")

        st.header("Constraint Selector")

        # Choose based on regex
        conSelect = st.selectbox(
            "Which Constraint?",
            cons['Cons_name']
        )
        row = cons.loc[cons['Cons_name'] == conSelect]
        minimaxes = congestion_database_pull.get_minimaxes(row['PriceDate'].iloc[0], (row['Hour'].iloc[0].item()))

        st.write(minimaxes[0])
        st.write(minimaxes[1])

        pt1 = minimaxes[0]['Node'].values.tolist()
        pt2 = minimaxes[1]['Node'].values.tolist()
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
        # Choose based on regex
        dataSelectX = st.selectbox(
            "Which Info On X?",
            nodeOptions
        )

        if dataSelectX == 'Station Temperature':
            nodeSelectX = st.selectbox(
                "Which IEM for Temperature?",
                iems
            )
            dataX = weather_temperature_pull.get_temperature(nodeSelectX)
        elif dataSelectX == 'Station Wind':
            nodeSelectX = st.selectbox(
                "Which IEM for Wind?",
                iems
            )
            dataX = weather_temperature_pull.get_wind(nodeSelectX)
        elif dataSelectX in nodeExclusive:
            nodeSelectX = st.selectbox(
                "Which Node On X?",
                allNodes
            )
            dataX = pd.DataFrame()
            for bit in components[dataSelectX]:
                temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectX].iloc[0]['Node_ID'], bit, dataSelectX)
                if dataX.empty:
                    dataX = temp
                else:
                    dataX[dataSelectX] -= temp[dataSelectX]
        elif dataSelectX == 'Spread':
            nodeSelectXShort = st.selectbox(
                "Which Node Long On X?",
                allNodes
            )
            dataX = pd.DataFrame()
            for bit in components['DA-RT']:
                temp = nodes_database_pull.get_node_info(
                    nodes.loc[nodes['NodeName'] == nodeSelectXShort].iloc[0]['Node_ID'], bit, dataSelectX)
                if dataX.empty:
                    dataX = temp
                else:
                    dataX[dataSelectX] -= temp[dataSelectX]


            nodeSelectXLong = st.selectbox(
                "Which Node Short On X?",
                allNodes
            )
            dataXTemp = pd.DataFrame()
            for bit in components['RT-DA']:
                temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectXLong].iloc[0]['Node_ID'], bit, dataSelectX)
                if dataXTemp.empty:
                    dataXTemp = temp
                else:
                    dataXTemp[dataSelectX] -= temp[dataSelectX]
            dataX[dataSelectX] += dataXTemp[dataSelectX]
            nodeSelectX = nodeSelectXShort + " and " + nodeSelectXLong
        else:
            nodeSelectX = "All"
            dataX = weather_temperature_pull.get_information(dataSelectX)


        dataX.sort_values(by=['PriceDate', 'Hour'], inplace=True)
        dataX.dropna(axis=0, how='any', inplace=True)
        st.write(dataX)



        st.header("Y Data Selector")

        # Choose based on regex
        dataSelectY = st.selectbox(
            "Which Info On Y?",
            nodeOptions
        )

        if dataSelectY == 'Station Temperature':
            nodeSelectY = st.selectbox(
                "Which IEM for Temperature?",
                iems
            )
            dataY = weather_temperature_pull.get_temperature(nodeSelectY)
        elif dataSelectY == 'Station Wind':
            nodeSelectY = st.selectbox(
                "Which IEM for Wind?",
                iems
            )
            dataY = weather_temperature_pull.get_wind(nodeSelectY)
        elif dataSelectY in nodeExclusive:
            nodeSelectY = st.selectbox(
                "Which Node On Y?",
                allNodes
            )
            dataY = pd.DataFrame()
            for bit in components[dataSelectY]:
                temp = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectY].iloc[0]['Node_ID'], bit, dataSelectY)
                if dataY.empty:
                    dataY = temp
                else:
                    dataY[dataSelectY] -= temp[dataSelectY]
        elif dataSelectY == 'Spread':
            nodeSelectYShort = st.selectbox(
                "Which Node Long On Y?",
                allNodes
            )
            dataY = pd.DataFrame()
            for bit in components['DA-RT']:
                temp = nodes_database_pull.get_node_info(
                    nodes.loc[nodes['NodeName'] == nodeSelectYShort].iloc[0]['Node_ID'], bit, dataSelectY)
                if dataY.empty:
                    dataY = temp
                else:
                    dataY[dataSelectY] -= temp[dataSelectY]

            nodeSelectYLong = st.selectbox(
                "Which Node Short On Y?",
                allNodes
            )
            dataYTemp = pd.DataFrame()
            for bit in components['RT-DA']:
                temp = nodes_database_pull.get_node_info(
                    nodes.loc[nodes['NodeName'] == nodeSelectYLong].iloc[0]['Node_ID'], bit, dataSelectY)
                if dataYTemp.empty:
                    dataYTemp = temp
                else:
                    dataYTemp[dataSelectY] -= temp[dataSelectY]
            dataY[dataSelectY] += dataYTemp[dataSelectY]
            nodeSelectY = nodeSelectYShort + " and " + nodeSelectYLong
        else:
            nodeSelectY = "All"
            dataY = weather_temperature_pull.get_information(dataSelectY)

        dataY.sort_values(by=['PriceDate', 'Hour'], inplace=True)
        dataY.dropna(axis=0, how='any', inplace=True)
        st.write(dataY)

        frame = pd.merge(dataX, dataY, how='left', on=['PriceDate', 'Hour'])
        frame.dropna(axis=0, how='any', inplace=True)

        if dataSelectX == dataSelectY:
            dataSelectX += '_x'
            dataSelectY += '_y'
        plot = dashboard_graph_creator.scatter_matplot_returner(frame[dataSelectX], frame[dataSelectY], nodeSelectX, nodeSelectY, dataSelectX, dataSelectY)
        st.pyplot(plot)
