import psycopg2
import pandas as pd
import time
import datetime
import random
import openpyxl
import streamlit as st

#random.seed(22)

cols = ['PriceDate', 'Hour', 'Cons_name', 'Shadow']

# Get old data to generate buckets from
def get_data():
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT pricedate, hour, cons_name, shadow
            FROM rtbinds
            WHERE pricedate >= '2020-01-01'
            """
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df


def get_more_data(formatted):
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    formatted = get_congestion(formatted, cur)
    formatted = get_prices(formatted)
    formatted = get_loads(formatted)
    return formatted

def get_congestion(formatted, cur):
    # Set up connection

    # Get string for dates
    dates = zip(formatted['PriceDate'].tolist(), formatted['Hour'].tolist())
    string = make_string(dates, "p")

    # Get columns for high congestion for constraint and low congestion for constraint
    maxes = ['PriceDate', 'Hour', 'HiCongestRT', 'Node']
    mins = ['PriceDate', 'Hour', 'LoCongestRT', 'Node']
    temps = ['PriceDate', 'Hour', 'Congest', 'Node']

    print("FIRST")

    # Get high congestion points
    comm = """SELECT p.pricedate, p.hour, MAX(p.rtmcc)
                        FROM prices p
                        WHERE (""" + string + """
                        GROUP BY p.pricedate, p.hour"""

    cur.execute(comm)
    out = cur.fetchall()
    dfMax = pd.DataFrame(data=out)
    dfMax.columns = maxes[:-1]

    # Sort high congestion
    dfMax.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    dfMax.reset_index(inplace=True, drop=True)


    print("THIRD")

    # Get low congestion points
    comm = """SELECT p.pricedate, p.hour, MIN(p.rtmcc)
                            FROM prices p
                            WHERE (""" + string + """
                            GROUP BY p.pricedate, p.hour"""


    cur.execute(comm)
    out = cur.fetchall()
    dfMin = pd.DataFrame(data=out)
    dfMin.columns = mins[:-1]


    print("FOURTH")


    comm = """SELECT p.pricedate, p.hour, p.rtmcc, n.nodename
                        FROM prices p
                        LEFT OUTER JOIN nodes n ON (p.node_id=n.node_id)
                        WHERE (""" + string + """
                        GROUP BY p.rtmcc, p.pricedate, p.hour, n.nodename"""
    cur.execute(comm)
    out = cur.fetchall()
    temp = pd.DataFrame(data=out)
    temp.columns = temps

    temp.sort_values(by=['Congest'], ascending=False, inplace=True)
    tempMax = temp.drop_duplicates('Node').head(5)
    tempMax.rename(columns={"Congest": "HiCongestRT"}, inplace=True)
    temp.sort_values(by=['Congest'], ascending=True, inplace=True)
    tempMin = temp.drop_duplicates('Node').head(5)
    tempMin.rename(columns={"Congest": "LoCongestRT"}, inplace=True)



    # Sort high congestion values
    dfMin.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    dfMin.reset_index(inplace=True, drop=True)

    # Merge congestions and prices together
    df = dfMax
    df = pd.merge(df, dfMin, how='left', on=['PriceDate', 'Hour'])

    formatted = pd.merge(formatted, df, how='left', on=['PriceDate', 'Hour'])

    return formatted, tempMax, tempMin

# Get the nodes congestions
def get_nodes(df, cur, hi, lo):
    
    # Get the high congestion
    nmaxes = ['PriceDate', 'Hour', 'HiCongestRT', 'NodeNameSupply']
    comm = """SELECT p.pricedate, p.hour, p.rtmcc, n.nodename
                FROM prices p
                LEFT OUTER JOIN nodes n ON (p.node_id=n.node_id)
                WHERE """ + hi + """
                GROUP BY p.pricedate, p.hour, p.rtmcc, n.nodename
                LIMIT 1"""
    cur.execute(comm)
    out = cur.fetchall()
    nodesMax = pd.DataFrame(data=out)
    nodesMax.columns = nmaxes
    
    # Get the low congestion
    nmins = ['PriceDate', 'Hour', 'LoCongestRT', 'NodeNameDemand']
    comm = """SELECT p.pricedate, p.hour, p.rtmcc, n.nodename
                FROM prices p
                LEFT OUTER JOIN nodes n ON (p.node_id=n.node_id)
                WHERE """ + lo + """
                GROUP BY p.pricedate, p.hour, p.rtmcc, n.nodename
                LIMIT 1"""
    cur.execute(comm)
    out = cur.fetchall()
    nodesMin = pd.DataFrame(data=out)
    nodesMin.columns = nmins

    # Merge all of the congestions to the original
    df = pd.merge(df, nodesMax, how='left', on=['PriceDate', 'Hour', 'HiCongestRT'])
    df = pd.merge(df, nodesMin, how='left', on=['PriceDate', 'Hour', 'LoCongestRT'])


    return df

# Get prices
def get_prices(df, cur):

    # Column labels for high and low day-ahead and real-time prices where the congestion is highest and lowest
    maxes2 = ['PriceDate', 'Hour', 'HiPriceDA', 'HiPriceRT']
    mins2 = ['PriceDate', 'Hour', 'LoPriceDA', 'LoPriceRT']

    # Make string that will match high congestion to the day-ahead and real-time coinciding points
    stringDARTHI = make_string_da_rt(df['PriceDate'].tolist(), df['Hour'].tolist(), df['HiCongestRT'])
    stringDARTLO = make_string_da_rt(df['PriceDate'].tolist(), df['Hour'].tolist(), df['LoCongestRT'])

    # Match congestion to prices at that point
    comm = """SELECT DISTINCT p.pricedate, p.hour, p.dalmp, p.rtlmp
                FROM prices p
                WHERE """ + stringDARTHI + """
                GROUP BY p.pricedate, p.hour, p.dalmp, p.rtlmp"""

    cur.execute(comm)
    out = cur.fetchall()
    secondMaxes = pd.DataFrame(data=out)
    secondMaxes.columns = maxes2

    # Format prices at max congestion
    secondMaxes.drop_duplicates(subset=['PriceDate', 'Hour'], inplace=True, keep='first')
    secondMaxes.reset_index(inplace=True, drop=True)




    # Same thing for minimum congestion
    stringDART = make_string_da_rt(df['PriceDate'].tolist(), df['Hour'].tolist(), df['LoCongestRT'])

    comm = """SELECT p.pricedate, p.hour, p.dalmp, p.rtlmp
                    FROM prices p
                    WHERE""" + stringDART + """
                    GROUP BY p.pricedate, p.hour, p.dalmp, p.rtlmp"""

    cur.execute(comm)
    out = cur.fetchall()
    secondMins = pd.DataFrame(data=out)
    secondMins.columns = mins2

    # Format miniumum congestion
    secondMins.drop_duplicates(subset=['PriceDate', 'Hour'], inplace=True, keep='first')
    secondMins.reset_index(inplace=True, drop=True)

    # Merge all of the frames
    df = pd.merge(df, secondMaxes, how='left', on=['PriceDate', 'Hour'])
    df = pd.merge(df, secondMins, how='left', on=['PriceDate', 'Hour'])

    return df, stringDARTHI, stringDARTLO

# Get the loads at the nodes for the constraints0-p[o0
def get_loads(formatted, cur):
    # Set up connection

    # Make list of dates again in order to get loads
    dates = zip(formatted['PriceDate'].tolist(), formatted['Hour'].tolist())
    string = make_string(dates, "g")

    # Loads columns
    colnames = ['PriceDate', 'Hour', 'AverageLoad']

    # Get average loads at pricedate and hour for comparison
    comm = """SELECT g.pricedate, g.hour, AVG(g.average_actual_load)
                FROM genmix g WHERE (""" + string + """
                GROUP BY g.pricedate, g.hour"""
    cur.execute(comm)
    out = cur.fetchall()
    if len(out) <= 1:
        return "BROKE"
    df2 = pd.DataFrame(data=out)
    df2.columns = colnames

    # Same thing, but for renewables. Get resources
    dates = zip(formatted['PriceDate'].tolist(), formatted['Hour'].tolist())
    string = make_string(dates, "r")
    colnames2 = ['PriceDate', 'Hour', 'Region 1', 'Region 2', 'Region 3', 'Region 4', 'Region 5']

    # Get the renewables
    comm = """SELECT r.pricedate, r.hour, r.value, v2.value, v3.value, v4.value, v5.value
                FROM rfrz_actual r
                LEFT OUTER JOIN rfrz_actual v2 ON (r.pricedate=v2.pricedate) AND (r.hour=v2.hour) AND (v2.reserve_zone=2) AND v2.resource='wind'
                LEFT OUTER JOIN rfrz_actual v3 ON (r.pricedate=v3.pricedate) AND (r.hour=v3.hour) AND (v3.reserve_zone=3) AND v3.resource='wind'
                LEFT OUTER JOIN rfrz_actual v4 ON (r.pricedate=v4.pricedate) AND (r.hour=v4.hour) AND (v4.reserve_zone=4) AND v4.resource='wind'
                LEFT OUTER JOIN rfrz_actual v5 ON (r.pricedate=v5.pricedate) AND (r.hour=v5.hour) AND (v5.reserve_zone=5) AND v5.resource='wind'
                WHERE (""" +  string + """
                AND r.reserve_zone=1 AND r.resource='wind'"""
    cur.execute(comm)
    out = cur.fetchall()
    df3 = pd.DataFrame(data=out)
    df3.columns = colnames2

    # Map Datetimes to Timestamps
    df2['PriceDate'] = df2['PriceDate'].map(lambda x: pd.Timestamp(x))
    df3['PriceDate'] = df3['PriceDate'].map(lambda x: pd.Timestamp(x))

    # Merge it all together
    formatted = pd.merge(formatted, df2, how='left', on=['PriceDate', 'Hour'])
    formatted = pd.merge(formatted, df3, how='left', on=['PriceDate', 'Hour'])

    return formatted

# Get the weather and temperature and wind
def get_weather(formatted, cur):

    #print("START")
    #start = time.time()

    # Get the temperature and windspeed at each IEM location
    w_cols = ['PriceDate', 'Hour', 'IEMID', 'Temperature', 'WindSpeed']
    dates = zip(formatted['PriceDate'].tolist(), formatted['Hour'].tolist())
    string = make_string_weathers(dates, "iso_utc")
    comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp, actual.iem_id, actual.temp, actual.wind_speed
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE (""" + string + """
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp, actual.iem_id, actual.temp, actual.wind_speed"""
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(out)
    df.columns = w_cols
    df.groupby(by=['PriceDate', 'Hour'], axis=1)


    #start2 = time.time()
    #print("SELECTED:", start2-start)
    
    # The final dataframe
    finalDFArr = []

    current = ""
    # Run through dataframe and get all IEMs per pricedate and hour on same axis
    for index, row in df.iterrows():
        temp = str(row['PriceDate']) + str(row['Hour'])
        
        # If its the first one, start the process
        if current == "":
            current = temp
            tempDF = pd.DataFrame(columns=['PriceDate', 'Hour', str(row['IEMID'])])
            newRow = {'PriceDate': row['PriceDate'], 'Hour': row['Hour'], str(row['IEMID']) + "temp": row['Temperature'], str(row['IEMID']) + "wind": row['WindSpeed']}
            tempDF = tempDF.append(newRow, ignore_index=True)
        
        # Otherwise, add the temperature and wind to the row
        elif current == temp:
            tempDF[str(row['IEMID']) + "temp"] = row['Temperature']
            tempDF[str(row['IEMID']) + "wind"] = row['WindSpeed']
        
        # If its the next pricedate-hour, start the process over again
        elif current != temp:
            finalDFArr.append(tempDF)
            tempDF = pd.DataFrame()
            current = temp
            newRow = {'PriceDate': row['PriceDate'], 'Hour': row['Hour'], str(row['IEMID']) + "temp": row['Temperature'], str(row['IEMID']) + "wind": row['WindSpeed']}
            tempDF = tempDF.append(newRow, ignore_index=True)

    #start3 = time.time()
    #print("LOOPED:", start3-start2)

    # append the last pricedate df to the whole df
    finalDFArr.append(tempDF)
    
    # Concatonate all of them to the final dataframe
    finalDF = finalDFArr[0]
    for r in finalDFArr[1:]:
        finalDF = pd.concat([finalDF, r], ignore_index=True, sort=False)
    
    # Merge them and return them
    finalDF['PriceDate'] = finalDF['PriceDate'].map(lambda x: pd.Timestamp(x))
    formatted = pd.merge(formatted, finalDF, how='left', on=['PriceDate', 'Hour'])

    #start4 = time.time()
    #print("MERGED", start4-start3)

    return formatted


# Make string for use with sql statements
def make_string(dates, table):
    string = ""

    # For each date, make it an available option
    for d in dates:
        string += "(" + table + ".pricedate = '" + d[0].strftime("%Y-%m-%d") + "' AND " + table + ".hour = " + str(d[1]) +") OR "
    string = string[:-4] + ")"
    return string

# Make string which will be used to match congestions to prices
def make_string_da_rt(dates, hours, congests):
    string = " ("

    # For each day, time, and congestion, make it an option
    for i in range(len(dates)):
        d = dates[i]
        h = hours[i]
        gest = congests[i]
        string += "(p.rtmcc = " + str(gest) + " AND p.pricedate = '" + d.strftime("%Y-%m-%d") + "' AND p.hour = " + str(h) +") OR "
    string = string[:-4] + ")"
    return string


# Make string for use with sql statements
def make_string_weathers(dates, table):
    string = ""

    # For each date, make it an available option
    for d in dates:
        string += "(" + table + ".pricedate_spp = '" + d[0].strftime("%Y-%m-%d") + "' AND " + table + ".hour_spp = " + str(d[1]) +") OR "
    string = string[:-4] + ")"
    return string

# Get more data based on the dictionary of constraints
def dict_get_more_data(df):
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    listo = list(df.keys())

    size = 0

    for k in listo:
        size += len(df[k])
    print(size)

    counter = 0.0

    progress = st.empty()
    final_maxes = pd.DataFrame()
    final_mins = pd.DataFrame()
    
    # For each constraint
    for k in listo:
        # Get all of these
        one, maxes, mins = get_congestion(df[k], cur)
        two, hi, lo = get_prices(one, cur)
        three = get_nodes(two, cur, hi, lo)
        maxes['Constraint'] = k
        mins['Constraint'] = k
        if counter == 0.0:
            final_maxes = maxes
            final_mins = mins
        else:
            final_maxes = final_maxes.append(maxes, sort=False)
            final_mins = final_mins.append(mins, sort=False)
        four = get_loads(three, cur)
        if type(four) == type("BROKE"):
            df.pop(k)
        five = get_weather(four, cur)
        df[k] = five
        df[k]['PriceDate'] = df[k]['PriceDate'].map(lambda x: x.strftime("%d/%m/%y "))
        counter += len(df[k])
        progress.text(str(round((counter/size)*100,2)) + "% Complete")

    progress.empty()
    # Return
    conn.close()
    return df, listo, final_maxes, final_mins
