import psycopg2
import pandas as pd
import time
import datetime
import random
import openpyxl
import streamlit as st

#random.seed(22)

cols = ['PriceDate', 'Hour', 'Cons_name', 'Shadow']

# WRAPPERS

# Get old data to generate buckets from
def get_con_data():
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT pricedate, hour, cons_name, shadow
            FROM rtbinds
            WHERE pricedate >= '2021-07-05'
            """
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df

def get_more_nodes_data(formatted):
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    formatted.drop_duplicates(subset=['Cons_name'], inplace=True)
    formatted.reset_index(inplace=True, drop=True)
    formatted = get_min_max_congestion(formatted, cur)
    formatted = get_min_max_nodes(formatted, cur)
    return formatted


# GETTERS


def get_min_max_congestion(formatted, cur):
    temps = ['PriceDate', 'Hour', 'MaximumMCC', 'MinimumMCC']
    dates = zip(formatted['PriceDate'].tolist(), formatted['Hour'].tolist())
    string = make_string_prices_hours(dates, "p")

    print(string)

    comm = """SELECT p.pricedate, p.hour, MAX(p.rtmcc), MIN(p.rtmcc)
                        FROM prices p
                        WHERE """ + string + """
                        GROUP BY p.pricedate, p.hour"""

    cur.execute(comm)
    out = cur.fetchall()
    temp = pd.DataFrame(data=out)
    temp.columns = temps
    temp.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    df = pd.merge(formatted, temp, how='left', on=['PriceDate', 'Hour'])
    return df


def get_min_max_nodes(formatted, cur):
    nodes = pd.DataFrame(columns=['MaximumNode', 'MinimumNode'])
    for index, row in formatted.iterrows():
        comm = """SELECT n.nodename
                    FROM nodes n
                    WHERE n.node_id = (SELECT p.node_id FROM prices p 
                    WHERE (p.pricedate='""" + str(row['PriceDate']).split(' ')[0] + """' AND p.hour=""" + str(row['Hour']) + """ AND p.rtmcc=""" + str(row['MaximumMCC'])+ """)
                    LIMIT 1)"""
        cur.execute(comm)
        max = cur.fetchall()[0][0]
        comm = """SELECT n.nodename
                    FROM nodes n
                    WHERE n.node_id = (SELECT p.node_id FROM prices p 
                    WHERE (p.pricedate='""" + str(row['PriceDate']).split(' ')[0] + """' AND p.hour=""" + str(row['Hour']) + """ AND p.rtmcc=""" + str(row['MinimumMCC'])+ """)
                    LIMIT 1)"""
        cur.execute(comm)
        min = cur.fetchall()[0][0]
        temp = pd.DataFrame(data={'MaximumNode': max, 'MinimumNode': min}, index=[0])
        nodes = nodes.append(temp, ignore_index=True)
    formatted = formatted.join(nodes, how='outer')
    return formatted



def get_nodes_all():
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['PriceDate', 'Hour', 'DALMP', 'DAMCC', 'DAMCL', 'RTLMP', 'RTMCC', 'RTMCL', 'NODE']

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT p.pricedate, p.hour, p.dalmp, p.damcc, p.damcl, p.rtlmp, p.rtmcc, p.rtmcl, n.nodename
            FROM prices p
            LEFT OUTER JOIN nodes n ON (n.node_id = p.node_id)
            WHERE pricedate >= '2021-01-01'
            """
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df

def get_weather():
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['PriceDate', 'Hour', 'IEM', 'Temperature', 'Wind']

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp, actual.iem_id, actual.temp, actual.wind_speed
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2021-01-01'
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp, actual.iem_id, actual.temp, actual.wind_speed"""
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df


# Get the loads at the nodes for the constraints0-p[o0
def get_loads():
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    # Loads columns
    colnames = ['PriceDate', 'Hour', 'AverageLoad']

    # Get average loads at pricedate and hour for comparison
    comm = """SELECT g.pricedate, g.hour, AVG(g.average_actual_load)
                FROM genmix g
                WHERE g.pricedate >= '2021-01-01'
                GROUP BY g.pricedate, g.hour"""
    cur.execute(comm)
    out = cur.fetchall()
    df2 = pd.DataFrame(data=out)
    df2.columns = colnames

    # Same thing, but for renewables. Get resources
    colnames2 = ['PriceDate', 'Hour', 'Region 1', 'Region 2', 'Region 3', 'Region 4', 'Region 5']

    # Get the renewables
    comm = """SELECT r.pricedate, r.hour, r.value, v2.value, v3.value, v4.value, v5.value
                FROM rfrz_actual r
                LEFT OUTER JOIN rfrz_actual v2 ON (r.pricedate=v2.pricedate) AND (r.hour=v2.hour) AND (v2.reserve_zone=2) AND v2.resource='wind'
                LEFT OUTER JOIN rfrz_actual v3 ON (r.pricedate=v3.pricedate) AND (r.hour=v3.hour) AND (v3.reserve_zone=3) AND v3.resource='wind'
                LEFT OUTER JOIN rfrz_actual v4 ON (r.pricedate=v4.pricedate) AND (r.hour=v4.hour) AND (v4.reserve_zone=4) AND v4.resource='wind'
                LEFT OUTER JOIN rfrz_actual v5 ON (r.pricedate=v5.pricedate) AND (r.hour=v5.hour) AND (v5.reserve_zone=5) AND v5.resource='wind'
                WHERE r.pricedate >= '2021-01-01'
                AND r.reserve_zone=1 AND r.resource='wind'"""
    cur.execute(comm)
    out = cur.fetchall()
    df3 = pd.DataFrame(data=out)
    df3.columns = colnames2
    weather = pd.merge(df2, df3, how='left', on=['PriceDate', 'Hour'])
    return weather

# AUXILERY

# Make string for use with sql statements
def make_string_nodes_congestion(dates, cons, table):
    string = "("

    # For each date, make it an available option
    counter = 0
    for i in range(len(dates)):
        break
    string = string[:-4] + ")"
    return string


# Make string for use with sql statements
def make_string_prices_hours(dates, table):
    string = "("

    # For each date, make it an available option
    for d in dates:
        string += "(" + table + ".pricedate = '" + d[0].strftime("%Y-%m-%d") + "' AND " + table + ".hour = " + str(d[1]) +") OR "
    string = string[:-4] + ")"
    return string