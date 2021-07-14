import pandas as pd, streamlit as st
import congestion_database_pull, nodes_database_pull, dashboard_graph_creator, weather_temperature_pull

def compile():
    nodeOptions = ['Load', 'Temperature', 'Region 1 Wind', 'Region 2 Wind', 'Region 3 Wind', 'Region 4 Wind', 'Region 5 Wind', 'Sum of All Wind', 'DALMP', 'DAMCC', 'DAMCL', 'RTLMP', 'RTMCC', 'RTMCL']
    nodeExclusive = ['DALMP', 'DAMCC', 'DAMCL', 'RTLMP', 'RTMCC', 'RTMCL']

    # If password, enter the dataframe
    password = st.text_input("Password: ")
    if password == "constraint123":
        cons = congestion_database_pull.get_constraints()
        nodes = nodes_database_pull.get_node_names()

        st.title("Constraints Data Visualizer")

        st.header("Constraint Selector")

        # Choose based on regex
        conSelect = st.selectbox(
            "Which Constraint?",
            cons['Cons_name']
        )
        row = cons.loc[cons['Cons_name'] == conSelect]
        st.write(row.iloc[:, [2,7,8]])

        st.header("X Selectors")
        
        # Choose based on regex
        dataSelectX = st.selectbox(
            "Which Info On X?",
            nodeOptions
        )

        if dataSelectX == 'Temperature':
            nodeSelectX = st.selectbox(
                "Which IEM for Temperature?",
                weather_temperature_pull.get_iems()
            )
            dataX = weather_temperature_pull.get_temperature(nodeSelectX)
        elif dataSelectX in nodeExclusive:
            nodeSelectX = st.selectbox(
                "Which Node On X?",
                list(nodes['NodeName'])
            )
            dataX = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectX].iloc[0]['Node_ID'], dataSelectX)
        else:
            nodeSelectX = "All"
            dataX = weather_temperature_pull.get_information(dataSelectX)
        
        st.header("Y Selectors")

        # Choose based on regex
        dataSelectY = st.selectbox(
            "Which Info On Y?",
            nodeOptions
        )

        if dataSelectY == 'Temperature':
            nodeSelectY = st.selectbox(
                "Which IEM for Temperature?",
                weather_temperature_pull.get_iems()
            )
            dataY = weather_temperature_pull.get_temperature(nodeSelectY)
        elif dataSelectY in nodeExclusive:
            nodeSelectY = st.selectbox(
                "Which Node On Y?",
                list(nodes['NodeName'])
            )
            dataY = nodes_database_pull.get_node_info(nodes.loc[nodes['NodeName'] == nodeSelectY].iloc[0]['Node_ID'], dataSelectY)
        else:
            nodeSelectY = "All"
            dataY = weather_temperature_pull.get_information(dataSelectY)

        dataX.sort_values(by=['PriceDate', 'Hour'], inplace=True)
        dataY.sort_values(by=['PriceDate', 'Hour'], inplace=True)

        frame = pd.merge(dataX, dataY, how='left', on=['PriceDate', 'Hour'])
        frame.dropna(axis=0, how='any', inplace=True)

        if dataSelectX == dataSelectY:
            dataSelectX += '_x'
            dataSelectY += '_y'

        plot = dashboard_graph_creator.scatter_matplot_returner(frame[dataSelectX], frame[dataSelectY], nodeSelectX, nodeSelectY, dataSelectX, dataSelectY)
        st.pyplot(plot)

def mapper():
    return
