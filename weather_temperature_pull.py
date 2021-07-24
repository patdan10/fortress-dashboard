import psycopg2
import pandas as pd
import streamlit as st

# Get the specified information, depending on what is selected.
def get_information(nodeSelect):
    if nodeSelect == 'Net Demand':
        # Net demand is load minus wind, so get both and subtract
        load = get_load()
        wind = get_wind_sum()
        demand = pd.merge(load, wind, how='left', on=['PriceDate', 'Hour'])
        demand.dropna(axis=0, how='any', inplace=True)
        demand['Net Demand'] = demand['Load'] - demand['Sum of All Wind']
        demand.drop('Load', axis=1, inplace=True)
        demand.drop('Sum of All Wind', axis=1, inplace=True)
        return demand
    elif nodeSelect == 'Load':
        # Get load
        return get_load()
    elif 'Sum' in nodeSelect:
        # Get wind
        return get_wind_sum()
    else:
        # Get a regional wind or temperature
        return get_region(nodeSelect.split(" ")[1])

    # Get the load
def get_load():
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    # Loads columns
    cols = ['PriceDate', 'Hour', 'Load']

    # Get average loads at pricedate and hour for comparison
    comm = """SELECT g.pricedate, g.hour, AVG(g.average_actual_load)
                FROM genmix g
                WHERE g.pricedate >= '2020-01-01'
                GROUP BY g.pricedate, g.hour"""
    
    # Get and return
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    return df

# Get the loads at the nodes for the constraints
def get_region(region):
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    # Columns for a wind
    cols = ['PriceDate', 'Hour', 'Region ' + region + ' Wind']

    # Get the wind information
    comm = """SELECT r.pricedate, r.hour, r.value
                FROM rfrz_actual r
                WHERE r.pricedate >= '2020-01-01'
                AND r.reserve_zone=""" + region + """ AND r.resource='wind'"""
    
    # Get and return
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    return df

# Get the wind at an IEM
def get_wind(iem):
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['PriceDate', 'Hour', 'Station Wind']

    # Execute SQL statement to get wind information at an IEM
    comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp, actual.wind_speed
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2020-01-01' AND iem_id='""" + iem + """'
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp, actual.iem_id, actual.wind_speed"""
    
    # Get and return
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df

# Get the wind sum with all IEMS
def get_wind_sum():
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['PriceDate', 'Hour', 'Sum of All Wind']

    # Execute SQL statement to get sum of IEMS
    comm = """SELECT r.pricedate, r.hour, SUM(r.value)
                FROM rfrz_actual r
                WHERE r.pricedate >= '2020-01-01'
                AND r.resource='wind'
                GROUP BY r.pricedate, r.hour"""
    
    # Get and return
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df

def get_temperature(iem):
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['PriceDate', 'Hour', 'Station Temperature']

    # Execute SQL statement to get temperature at IEMS
    comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp, actual.temp
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2020-01-01' AND iem_id='""" + iem + """'
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp, actual.iem_id, actual.temp"""
    
    # Get and return
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df

# Get all IEMS. Cache is for consistent use
@st.cache(suppress_st_warning=True)
def get_iems():
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['IEMs']

    # Execute SQL statement to get IEMS
    comm = """SELECT DISTINCT iem_id
              FROM weather.actual"""
    
    # Get and return
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df
