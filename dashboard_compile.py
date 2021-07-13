import streamlit as st
import numpy as np
import pandas as pd
import sys
sys.path.append('/Users/patrick/PycharmProjects/FortressWork/DashboardData')
import dashboard_factors

# All nodenames
#nodes = ['06D', '19S', '1F0', '2D5', '3AU', '7L2', '7N0', '9V9', 'ABI', 'ABQ', 'ABR', 'AGC', 'AIO', 'AMA', 'AMN', 'AMW', 'ANW', 'APY', 'ATT', 'ATY', 'AUM', 'AXN', 'AXS', 'BAC', 'BBW', 'BFL', 'BHK', 'BHM', 'BIE', 'BIS', 'BJC', 'BKN', 'BKX', 'BLH', 'BMI', 'BNA', 'BNW', 'BOI', 'BPG', 'BRO', 'BTR', 'BVN', 'BVO', 'C09', 'C75', 'CAO', 'CFS', 'CIN', 'CLT', 'CMH', 'COD', 'CPS', 'CQT', 'CRG', 'CRW', 'CSQ', 'CVS', 'CZZ', 'D50', 'D55', 'D57', 'D60', 'DAG', 'DBQ', 'DCA', 'DDC', 'DEC', 'DET', 'DFI', 'DFW', 'DIK', 'DKB', 'DLL', 'DMH', 'DNV', 'DOV', 'DRT', 'DSM', 'DUA', 'EBG', 'ECS', 'ECU', 'EED', 'ELK', 'ELP', 'ESN', 'ETB', 'EZZ', 'F05', 'FLD', 'FOD', 'FSI', 'FSM', 'FST', 'FXY', 'GAG', 'GCK', 'GDV', 'GED', 'GFK', 'GGW', 'GLD', 'GOK', 'GRR', 'GTF', 'GUR', 'GUY', 'GZL', 'HBR', 'HBV', 'HEI', 'HHR', 'HLC', 'HPT', 'HRL', 'HRX', 'HUM', 'HYS', 'HYX', 'HZE', 'IAB', 'IBM', 'ICL', 'IFA', 'IKK', 'IND', 'INL', 'ISW', 'JAN', 'JDN', 'JHN', 'JLN', 'JMS', 'JWG', 'JZI', 'LAF', 'LAW', 'LBB', 'LBF', 'LCG', 'LEX', 'LFT', 'LIC', 'LOU', 'LRD', 'LRF', 'LUK', 'LYV', 'MBG', 'MCX', 'MDD', 'MEM', 'MFE', 'MIE', 'MIV', 'MIW', 'MKC', 'MKE', 'MLI', 'MLS', 'MOT', 'MSP', 'MXO', 'MYZ', 'NXP', 'NYC', 'ODO', 'OGA', 'OJA', 'OKC', 'OKK', 'OMA', 'ONL', 'ORD', 'OTG', 'OWI', 'OZA', 'P28', 'PDK', 'PDX', 'PHL', 'PHX', 'PIL', 'PLD', 'PNA', 'PNC', 'PNT', 'PPA', 'PQN', 'PSP', 'PTT', 'PVB', 'PVW', 'RCE', 'RFD', 'RHI', 'RIV', 'RIW', 'RKS', 'RNO', 'RPH', 'RQO', 'RRT', 'RSL', 'RUG', 'RVS', 'RZL', 'SAN', 'SAT', 'SAW', 'SBD', 'SCK', 'SDY', 'SFO', 'SGF', 'SHL', 'SJT', 'SLB', 'SLC', 'SLN', 'SMF', 'SNK', 'SNS', 'SNY', 'SOA', 'SPS', 'SQI', 'SQL', 'STJ', 'STK', 'SWW', 'TEB', 'TFP', 'TIP', 'TOR', 'TPA', 'TRM', 'TSP', 'TYR', 'UIN', 'UKL', 'UNU', 'UVA', 'VGT', 'WWR', 'YKN']

# Compile the dashboard
def compile(items):
    for i in range(len(items)):
        items[i] = items[i].head(15)
    cons_info = items[0]
    nodes_info = items[1]
    weather = items[2]
    loads = items[3]

    cons = cons_info['Cons_name']
    nodes = nodes_info['NODE'].drop_duplicates()
    print(nodes)
    print("DUBYA")
    
    # If password, enter the dataframe
    password = st.text_input("Password: ")
    if password == "constraint123":
        listOfNodes = []
        consDict = {}
        
        
        st.title("Constraints Data Visualizer")

        st.header("Constraint Selector")




        # Choose based on regex
        conSelect = st.selectbox(
            "Which Constraint?",
            cons
        )


        row = cons_info.loc[cons_info['Cons_name'] == conSelect]
        st.write(row.iloc[:, [2,7,8]])
        st.header("Data Selectors")




        st.subheader("Select X Value")
        
        # Which values on X
        nodeOptionX = st.selectbox(
            "Which Node On X?",
            nodes
        )
        nodeX = nodes_info.loc[nodes_info['NODE'] == nodeOptionX]
        #st.write(nodeX)

        # Which values on X
        dataOptionX = st.selectbox(
            "Which Data On X?",
            nodes_info.columns
        )
        dataX = nodeX[dataOptionX]
        #st.write(dataX)





        st.subheader("Select Y Value")

        # Which values on Y
        nodeOptionY = st.selectbox(
            "Which Node On Y?",
            nodes
        )
        nodeY = nodes_info.loc[nodes_info['NODE'] == nodeOptionY]
        # st.write(nodeX)



        # Which values on X
        dataOptionY = st.selectbox(
            "Which Data On Y?",
            nodes_info.columns
        )
        dataY = nodeY[dataOptionY]
        # st.write(dataX)

        st.markdown('##')







        st.header("Filter Selector On X")

        emptiesX = [st.empty(),st.empty(),st.empty(),st.empty()]

        qwX = {
            "One": ["Which Data To Filter On X?", "Which Direction On X?", "Limit On X: ", "Do you want to filter again On X?"],
            "Two": ["Which Data To Filter Again On X?", "Which Direction Again On X?", "Limit Again On X: ", "Do you want to filter a third time On X?"],
            "Three": ["Which Data To Filter A Third Time On X?", "Which Direction A Third Time On X?", "Limit A Third Time On X: ", "Do you want to filter a fourth time On X?", ],
            "Four": ["Which Data To Filter A Fourth Time On X?", "Which Direction A Fourth Time On X?", "Limit A Fourth Time On X: ", "GG"]
        }
        
        # Filters, Limits, Directions, Agrees
        fisX = []
        lisX = []
        disX = []
        counterX = 0
        
        # Do you want to filter
        emptiesX[counterX] = st.checkbox("Do you want to filter X?")
        # If the first filter is active
        if emptiesX[counterX]:
            for x in qwX.keys():
                dataOptionFilterBefore = st.selectbox(
                    qwX[x][0],
                    list(colsDict.keys())
                )

                dataOptionFilter = colsDict[dataOptionFilterBefore]

                st.write(df[conOptionX][dataOptionFilter].sort_values())
            
                # Pick the direction
                direction = st.selectbox(
                    qwX[x][1],
                    ("Greater Than", "Less Than", "Equal To")
                )

                # Choose the limit
                limit = st.number_input(qwX[x][2])
        
                # Add them all
                fisX.append(dataOptionFilter)
                lisX.append(limit)
                disX.append(direction)

                df[conOptionX] = filter_handler(df[conOptionX], fisX, lisX, disX)

                if qwX[x][3] == "GG":
                    break

                filterAgain = st.checkbox(qwX[x][3])

                if not filterAgain:
                    break

        # FILTER FOR Y
        st.header("Filter Selector On Y")

        emptiesY = [st.empty(), st.empty(), st.empty(), st.empty()]

        qwY = {
            "One": ["Which Data To Filter On Y?", "Which Direction On Y?", "Limit On Y: ",
                    "Do you want to filter again On Y?"],
            "Two": ["Which Data To Filter Again On Y?", "Which Direction Again On Y?", "Limit Again On Y: ",
                    "Do you want to filter a third time On Y?"],
            "Three": ["Which Data To Filter A Third Time On Y?", "Which Direction A Third Time On Y?",
                      "Limit A Third Time On Y: ", "Do you want to filter a fourth time On Y?", ],
            "Four": ["Which Data To Filter A Fourth Time On Y?", "Which Direction A Fourth Time On Y?",
                     "Limit A Fourth Time On Y: ", "GG"]
        }

        # Filters, Limits, Directions, Agrees
        fisY = []
        lisY = []
        disY = []
        counterY = 0

        # Do you want to filter
        emptiesY[counterY] = st.checkbox("Do you want to filter Y?")
        # If the first filter is active
        if emptiesY[counterY]:
            for x in qwY.keys():
                dataOptionFilterBefore = st.selectbox(
                    qwY[x][0],
                    list(colsDict.keys())
                )

                dataOptionFilter = colsDict[dataOptionFilterBefore]

                st.write(df[conOptionX][dataOptionFilter].sort_values())

                # Pick the direction
                direction = st.selectbox(
                    qwY[x][1],
                    ("Greater Than", "Less Than", "Equal To")
                )

                # Choose the limit
                limit = st.number_input(qwY[x][2])

                # Add them all
                fisY.append(dataOptionFilter)
                lisY.append(limit)
                disY.append(direction)

                df[conOptionX] = filter_handler(df[conOptionX], fisY, lisY, disY)

                if qwY[x][3] == "GG":
                    break

                filterAgain = st.checkbox(qwY[x][3])

                if not filterAgain:
                    break





        # Get the scatter plot
        plot = dashboard_factors.scatter_matplot_returner(dataX, dataY, nodeOptionX, nodeOptionY, dataOptionX, dataOptionY)
        st.markdown('##')
        st.pyplot(plot)

        return


        # Setup for Seaborn
        df[conOptionX] = tdfX
        df[conOptionX].rename(columns=reverse_dict, inplace=True)

        # If data, then get seaborb
        if len(df[conOptionX]) > 1:
            print("SCATTER")
            #plot2 = constraints_factors.scatter_seaborn_returner(df, conOptionX, reverse_dict)
            st.markdown('##')
            #st.pyplot(plot2)

        df = dfCopy.copy()

# Get filters
def filter_handler(df, fis, lis, dis):
    # For filters, filter each and reset index
    if fis is not None:
        for i in range(len(fis)):
            df, reg = filter_return(df, fis[i], lis[i], dis[i])
            df.reset_index(inplace=True, drop=True)
    return df

# Filter an individual filter
def filter_return(df, dataF, limit, dir):
    filter = pd.Series(df[dataF].values)
    tdf = ""
    
    # Do the correct operation according to the limit
    if dir == "Greater Than":
        tdf = df[filter > limit]
    elif dir == "Less Than":
        tdf = df[filter < limit]
    elif dir == "Equal To":
        tdf = df[filter == limit]
    else:
        print("BUSTED")
    
    # If filters are successful or not
    if len(tdf) > 0:
        return tdf, "Successfully Filtered"

    return df, "Failure to Filter"
