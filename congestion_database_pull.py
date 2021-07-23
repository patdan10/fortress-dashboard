import psycopg2
import pandas as pd
import data_formatter
import streamlit as st
import datetime

@st.cache(suppress_st_warning=True)
def get_constraints():
    oldday = datetime.datetime.today()-datetime.timedelta(days=14)
    cols = ['PriceDate', 'Hour', 'Cons_name', 'Shadow']
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT pricedate, hour, cons_name, shadow
            FROM rtbinds
            WHERE pricedate >= '""" + oldday.strftime("%Y-%m-%d") + "'"
    cur.execute(comm)
    out = cur.fetchall()
    formatted = pd.DataFrame(data=out)
    formatted.columns = cols

    formatted = data_formatter.format(formatted)

    formatted.drop_duplicates(subset=['Cons_name'], inplace=True)
    formatted.sort_values(inplace=True, by='Cons_name')
    formatted.reset_index(inplace=True, drop=True)
    return formatted

# GETTERS
def get_minimaxes(date, hour):
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    nodes = get_min_max_congestion(date, hour, cur)
    for i in range(len(nodes)):
        nodes[i] = get_min_max_nodes(nodes[i], cur)

    return nodes

def get_min_max_congestion(date, hour, cur):
    maxTemps = ['PriceDate', 'Hour', 'MaximumMCC']
    comm = """SELECT p.pricedate, p.hour, p.rtmcc
                        FROM prices p
                        WHERE (p.pricedate='""" + date.strftime("%Y-%m-%d") + """' AND p.hour=""" + str(hour) + """)
                        GROUP BY p.pricedate, p.hour, p.rtmcc
                        ORDER BY p.rtmcc DESC
                        LIMIT 5"""

    cur.execute(comm)
    out = cur.fetchall()
    maxes = pd.DataFrame(data=out)
    maxes.columns = maxTemps
    maxes.sort_values(by=['PriceDate', 'Hour'], inplace=True)


    minTemps = ['PriceDate', 'Hour', 'MinimumMCC']

    comm = """SELECT p.pricedate, p.hour, p.rtmcc
                        FROM prices p
                        WHERE (p.pricedate='""" + date.strftime("%Y-%m-%d") + """' AND p.hour=""" + str(hour) + """)
                        GROUP BY p.pricedate, p.hour, p.rtmcc
                        ORDER BY p.rtmcc ASC
                        LIMIT 5"""

    cur.execute(comm)
    out = cur.fetchall()
    mins = pd.DataFrame(data=out)
    mins.columns = minTemps
    mins.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    return [maxes, mins]

def get_min_max_nodes(formatted, cur):
    mc = formatted.columns[-1]
    allExtremes = pd.DataFrame(columns=['PriceDate', 'Hour', mc, 'Node'])
    for index, row in formatted.iterrows():
        comm = """SELECT n.nodename
                    FROM nodes n
                    WHERE n.node_id = (SELECT p.node_id FROM prices p 
                    WHERE (p.pricedate='""" + str(row['PriceDate']).split(' ')[0] + """' AND p.hour=""" + str(row['Hour']) + """ AND p.rtmcc=""" + str(row[mc])+ """)
                    LIMIT 1)"""
        cur.execute(comm)
        extreme = cur.fetchall()[0][0]
        temp = pd.DataFrame(data={'PriceDate': row['PriceDate'], 'Hour': row['Hour'], mc: row[mc], 'Node': extreme}, index=[index])
        if index == 0:
            allExtremes = temp
        else:
            allExtremes = pd.concat([allExtremes, temp])

    return allExtremes
