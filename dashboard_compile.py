import streamlit as st
import numpy as np
import pandas as pd
import sys
sys.path.append('/Users/patrick/PycharmProjects/FortressWork/ConstraintsReportBuilder')
import constraints_factors

# Dicrtionary to get table row from regex
colsDict = {
    "Shadow Price": "Shadow",
    "Highest MCC For Constraint": "HiCongestRT",
    "Lowest MCC For Constraint": "LoCongestRT",
    "Price at High MCC Real-Time": "HiPriceRT",
    "Price at Low MCC Real-Time": "LoPriceRT",
    "Price at High MCC Day-Ahead": "HiPriceDA",
    "Price at Low MCC Day-Ahead": "LoPriceDA",
    "Price Spread": "Spread",
    "Region 1 Wind": "Region 1",
    "Region 2 Wind": "Region 2",
    "Region 3 Wind": "Region 3",
    "Region 4 Wind": "Region 4",
    "Region 5 Wind": "Region 5",
    "Sum of All Winds": "WindSum",
    "Shift Factor For High MCC": "LoShift",
    "Shift Factor For Low MCC": "HiShift",
    "Average Load": "AverageLoad",
    "Net Load": "NetLoad",
    "Temperature at a Node": "temp",
    "Wind Speed at a Node": "wind"
}

# All nodenames
nodes = ['06D', '19S', '1F0', '2D5', '3AU', '7L2', '7N0', '9V9', 'ABI', 'ABQ', 'ABR', 'AGC', 'AIO', 'AMA', 'AMN', 'AMW', 'ANW', 'APY', 'ATT', 'ATY', 'AUM', 'AXN', 'AXS', 'BAC', 'BBW', 'BFL', 'BHK', 'BHM', 'BIE', 'BIS', 'BJC', 'BKN', 'BKX', 'BLH', 'BMI', 'BNA', 'BNW', 'BOI', 'BPG', 'BRO', 'BTR', 'BVN', 'BVO', 'C09', 'C75', 'CAO', 'CFS', 'CIN', 'CLT', 'CMH', 'COD', 'CPS', 'CQT', 'CRG', 'CRW', 'CSQ', 'CVS', 'CZZ', 'D50', 'D55', 'D57', 'D60', 'DAG', 'DBQ', 'DCA', 'DDC', 'DEC', 'DET', 'DFI', 'DFW', 'DIK', 'DKB', 'DLL', 'DMH', 'DNV', 'DOV', 'DRT', 'DSM', 'DUA', 'EBG', 'ECS', 'ECU', 'EED', 'ELK', 'ELP', 'ESN', 'ETB', 'EZZ', 'F05', 'FLD', 'FOD', 'FSI', 'FSM', 'FST', 'FXY', 'GAG', 'GCK', 'GDV', 'GED', 'GFK', 'GGW', 'GLD', 'GOK', 'GRR', 'GTF', 'GUR', 'GUY', 'GZL', 'HBR', 'HBV', 'HEI', 'HHR', 'HLC', 'HPT', 'HRL', 'HRX', 'HUM', 'HYS', 'HYX', 'HZE', 'IAB', 'IBM', 'ICL', 'IFA', 'IKK', 'IND', 'INL', 'ISW', 'JAN', 'JDN', 'JHN', 'JLN', 'JMS', 'JWG', 'JZI', 'LAF', 'LAW', 'LBB', 'LBF', 'LCG', 'LEX', 'LFT', 'LIC', 'LOU', 'LRD', 'LRF', 'LUK', 'LYV', 'MBG', 'MCX', 'MDD', 'MEM', 'MFE', 'MIE', 'MIV', 'MIW', 'MKC', 'MKE', 'MLI', 'MLS', 'MOT', 'MSP', 'MXO', 'MYZ', 'NXP', 'NYC', 'ODO', 'OGA', 'OJA', 'OKC', 'OKK', 'OMA', 'ONL', 'ORD', 'OTG', 'OWI', 'OZA', 'P28', 'PDK', 'PDX', 'PHL', 'PHX', 'PIL', 'PLD', 'PNA', 'PNC', 'PNT', 'PPA', 'PQN', 'PSP', 'PTT', 'PVB', 'PVW', 'RCE', 'RFD', 'RHI', 'RIV', 'RIW', 'RKS', 'RNO', 'RPH', 'RQO', 'RRT', 'RSL', 'RUG', 'RVS', 'RZL', 'SAN', 'SAT', 'SAW', 'SBD', 'SCK', 'SDY', 'SFO', 'SGF', 'SHL', 'SJT', 'SLB', 'SLC', 'SLN', 'SMF', 'SNK', 'SNS', 'SNY', 'SOA', 'SPS', 'SQI', 'SQL', 'STJ', 'STK', 'SWW', 'TEB', 'TFP', 'TIP', 'TOR', 'TPA', 'TRM', 'TSP', 'TYR', 'UIN', 'UKL', 'UNU', 'UVA', 'VGT', 'WWR', 'YKN']

# The opposite dictionary for regex from table row
reverse_dict = {v: k for k, v in colsDict.items()}

# Compile the dashboard
def compile(df, listo, maxes, mins):
    #maxes = pd.DataFrame(maxes, columns=maxes.keys(), index=range(len(maxes.keys())))
    #mins = pd.DataFrame(mins, columns=mins.keys(), index=range(len(maxes.keys())))

    temp = pd.DataFrame()

    for k in list(maxes.keys()):
        temp[k] = maxes[k].squeeze()
    maxes = temp.copy().sort_values(by=['HiCongestRT']).reset_index(drop=True)
    maxes['PriceDate'] = maxes['PriceDate'].map(lambda x: x.strftime("%d/%m/%y "))
    maxes.columns = ['Date', 'Hour', 'MCC', 'Node', 'Constraint']

    temp = pd.DataFrame()
    for k in list(mins.keys()):
        temp[k] = mins[k].squeeze()
    mins = temp.copy().sort_values(by=['LoCongestRT']).reset_index(drop=True)
    mins['PriceDate'] = mins['PriceDate'].map(lambda x: x.strftime("%d/%m/%y "))
    mins.columns = ['Date', 'Hour', 'MCC', 'Node', 'Constraint']

    dfCopy = df.copy()
    maxesCopy = maxes.copy()
    minsCopy = mins.copy()
    
    # If password, enter the dataframe
    password = st.text_input("Password: ")
    if password == "constraint123":
        listOfNodes = []
        consDict = {}
        
        # Get list of nodenames
        for l in listo:
            listOfNodes.append(df[l]['Cons_name'].iloc[0])
            consDict[df[l]['Cons_name'].iloc[0]] = l
        
        
        st.title("Constraints Data Visualizer")

        st.header("Constraint Selector")
        
        # Choose based on regex
        conOption = st.selectbox(
            "Which Constraint?",
            listOfNodes
        )

        st.write("The Top Five MCC Values")
        maxes = maxes.loc[maxes['Constraint'] == conOption]
        st.write(maxes)

        st.write("The Bottom Five MCC Values")
        mins = mins.loc[mins['Constraint'] == conOption]
        st.write(mins)

        conOption = consDict[conOption]

        st.markdown('##')

        st.header("Data Selectors")
        st.subheader("Select X Values")
        
        # Which values on X
        dataOptionXBefore = st.selectbox(
            "Which Data On X?",
            list(colsDict.keys())
        )

        dataOptionX = colsDict[dataOptionXBefore]
        
        # Choose a node to have temperature or wind from
        if dataOptionX == "temp" or dataOptionX == "wind":
            dataOptionX = st.selectbox(
                "Which Node on X?",
                nodes) + dataOptionX

        st.write(df[conOption][dataOptionX])
        
        # Same thing on Y
        st.subheader("Select Y Values")
        dataOptionYBefore = st.selectbox(
            "Which Data On Y?",
            list(colsDict.keys())
        )

        dataOptionY = colsDict[dataOptionYBefore]
        
        # Which node for temperature or wind
        if dataOptionY == "temp" or dataOptionY == "wind":
            dataOptionY = st.selectbox(
                "Which Node on Y?",
                nodes) + dataOptionY

        st.write(df[conOption][dataOptionY])

        st.markdown('##')







        st.header("Filter Selector")
        
        # Filters, Limits, Directions, Agrees
        fis = []
        lis = []
        dis = []
        ags = []
        
        # Do you want to filter
        agree1 = st.checkbox("Do you want to filter?")
        dataOptionFilter1 = None
        direction1 = None
        limit1 = None
        
        # If the first filter is active
        if agree1:
            # Chose Filter
            dataOptionFilterBefore1 = st.selectbox(
                "Which Data To Filter?",
                list(colsDict.keys())
            )

            dataOptionFilter1 = colsDict[dataOptionFilterBefore1]

            st.write(df[conOption][dataOptionFilter1].sort_values())
            
            # Pick the direction
            direction1 = st.selectbox(
                "Which Direction?",
                ("Greater Than", "Less Than", "Equal To")
            )
            
            # Choose the limit
            limit1 = st.number_input("Limit: ")
        
        # Add them all
        if agree1:
            fis.append(dataOptionFilter1)
            lis.append(limit1)
            dis.append(direction1)
            ags.append(agree1)

        df[conOption] = filter_handler(df[conOption], fis, lis, dis)

        # If the first filter is active, ask for second filter
        agree2 = False
        if agree1:
            agree2 = st.checkbox("Do you want to filter again?")
        dataOptionFilter2 = None
        direction2 = None
        limit2 = None
        
        # Same as first
        if agree2:
            dataOptionFilterBefore2 = st.selectbox(
                "Which Data To Filter Again?",
                list(colsDict.keys())
            )

            dataOptionFilter2 = colsDict[dataOptionFilterBefore2]

            st.write(df[conOption][dataOptionFilter2].sort_values())

            direction2 = st.selectbox(
                "Which Direction Again?",
                ("Greater Than", "Less Than", "Equal To")
            )

            limit2 = st.number_input("Limit Again: ")

        if agree2:
            fis.append(dataOptionFilter2)
            lis.append(limit2)
            dis.append(direction2)
            ags.append(agree2)

        df[conOption] = filter_handler(df[conOption], fis, lis, dis)
        
        # Third Filter
        agree3 = False
        if agree2:
            agree3 = st.checkbox("Do you want to filter a third time?")
        dataOptionFilter3 = None
        direction3 = None
        limit3 = None
        if agree3:
            dataOptionFilterBefore3 = st.selectbox(
                "Which Data To Filter A Third Time?",
                list(colsDict.keys())
            )

            dataOptionFilter3 = colsDict[dataOptionFilterBefore3]

            st.write(df[conOption][dataOptionFilter3].sort_values())

            direction3 = st.selectbox(
                "Which Direction A Third Time?",
                ("Greater Than", "Less Than", "Equal To")
            )

            limit3 = st.number_input("Limit A Third Time: ")

        if agree3:
            fis.append(dataOptionFilter3)
            lis.append(limit3)
            dis.append(direction3)
            ags.append(agree3)

        df[conOption] = filter_handler(df[conOption], fis, lis, dis)
        
        # Fourth Filtere
        agree4 = False
        if agree3:
            agree4 = st.checkbox("Do you want to filter a fourth time?")
        dataOptionFilter4 = None
        direction4 = None
        limit4 = None
        if agree4:
            dataOptionFilterBefore4 = st.selectbox(
                "Which Data To Filter A Fourth Time?",
                list(colsDict.keys())
            )

            dataOptionFilter4 = colsDict[dataOptionFilterBefore4]

            st.write(df[conOption][dataOptionFilter4].sort_values())

            direction4 = st.selectbox(
                "Which Direction A Fourth Time?",
                ("Greater Than", "Less Than", "Equal To")
            )

            limit4 = st.number_input("Limit A Fourth Time: ")

        if agree4:
            fis.append(dataOptionFilter4)
            lis.append(limit4)
            dis.append(direction4)
            ags.append(agree4)

        df[conOption] = filter_handler(df[conOption], fis, lis, dis)
        
        # Get the scatter plot
        plot, reg, tdf = constraints_factors.scatter_matplot_returner(df, listo, conOption, dataOptionX, dataOptionY, fis, lis, dis)
        st.write(reg)
        st.markdown('##')
        st.pyplot(plot)

        # Setup for Seaborn
        df[conOption] = tdf
        df[conOption].rename(columns=reverse_dict, inplace=True)
        
        print("DIFF", df)
        # If data, then get seaborb
        if len(df[conOption]) > 1:
            print("SCATTER")
            #plot2 = constraints_factors.scatter_seaborn_returner(df, listo, conOption, reverse_dict)
            #st.markdown('##')
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
