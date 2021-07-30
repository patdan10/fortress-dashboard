import psycopg2
import pandas as pd
import data_formatter
import streamlit as st
import datetime

# Get list of all constraints, cache for consistent use
@st.cache(suppress_st_warning=True)
def get_constraints():
    # We only want from last two weeks
    oldday = datetime.datetime.today()-datetime.timedelta(days=365)
    cols = ['PriceDate', 'Hour', 'Cons_name', 'Shadow']
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    # Execute SQL statement to get constraints from RT Binds
    comm = """SELECT pricedate, hour, cons_name, shadow
            FROM rtbinds
            WHERE pricedate >= '""" + oldday.strftime("%Y-%m-%d") + "'"
    
    # Get and format
    cur.execute(comm)
    out = cur.fetchall()
    formatted = pd.DataFrame(data=out)
    formatted.columns = cols
    
    # Formatting of data. Drop duplicate days, and isolate days and timees of binding
    names, formatted = data_formatter.names_and_format(formatted)
    return names, formatted

# Get 5 min and 5 max of a given date and time, which is when it will be binding
def get_minimaxes(row):
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    
    # Get congestions
    nodes = get_min_max_congestion(row['PriceDate'], row['Hour'], cur)
    
    # Match to node names
    for i in range(len(nodes)):
        nodes[i] = get_min_max_nodes(nodes[i], cur)

    return nodes

# Get top 5 and bottom 5 congestions
def get_min_max_congestion(date, hour, cur):
    # Get maximums
    maxTemps = ['PriceDate', 'Hour', 'MaximumMCC']
    
    # Select maximums on date and time of binding
    comm = """SELECT p.pricedate, p.hour, p.rtmcc
                        FROM prices p
                        WHERE (p.pricedate='""" + date.strftime("%Y-%m-%d") + """' AND p.hour=""" + str(hour) + """)
                        GROUP BY p.pricedate, p.hour, p.rtmcc
                        ORDER BY p.rtmcc DESC
                        LIMIT 5"""
    
    # Select and format
    cur.execute(comm)
    out = cur.fetchall()
    maxes = pd.DataFrame(data=out)
    maxes.columns = maxTemps
    maxes.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    
    # Get minimums
    minTemps = ['PriceDate', 'Hour', 'MinimumMCC']
    
    # Select minimums on date and time of binding
    comm = """SELECT p.pricedate, p.hour, p.rtmcc
                        FROM prices p
                        WHERE (p.pricedate='""" + date.strftime("%Y-%m-%d") + """' AND p.hour=""" + str(hour) + """)
                        GROUP BY p.pricedate, p.hour, p.rtmcc
                        ORDER BY p.rtmcc ASC
                        LIMIT 5"""
    
    # Select and format
    cur.execute(comm)
    out = cur.fetchall()
    mins = pd.DataFrame(data=out)
    mins.columns = minTemps
    mins.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    return [maxes, mins]

# Gete nodes and names of the congestions
def get_min_max_nodes(formatted, cur):
    # Makes columns
    mc = formatted.columns[-1]
    allExtremes = pd.DataFrame(columns=['PriceDate', 'Hour', mc, 'Node'])
    
    # For the minimums or maximums, get the nodename of the day, time, and congestion of each
    for index, row in formatted.iterrows():
        comm = """SELECT n.nodename
                    FROM nodes n
                    WHERE n.node_id = (SELECT p.node_id FROM prices p 
                    WHERE (p.pricedate='""" + str(row['PriceDate']).split(' ')[0] + """' AND p.hour=""" + str(row['Hour']) + """ AND p.rtmcc=""" + str(row[mc])+ """)
                    LIMIT 1)"""
        
        # Get and format
        cur.execute(comm)
        
        # This is the formatting
        extreme = cur.fetchall()[0][0]
        temp = pd.DataFrame(data={'PriceDate': row['PriceDate'], 'Hour': row['Hour'], mc: row[mc], 'Node': extreme}, index=[index])
        
        # If its the first, make it the first. Otherwise, append it to the end
        if index == 0:
            allExtremes = temp
        else:
            allExtremes = pd.concat([allExtremes, temp])

    return allExtremes
