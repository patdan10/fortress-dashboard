import psycopg2
import pandas as pd

def get_information(nodeSelect):
    if nodeSelect == 'Load':
        return get_load()
    elif 'Sum' in nodeSelect:
        return get_wind_sum()
    else:
        return get_region(nodeSelect.split(" ")[1])

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
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    return df

# Get the loads at the nodes for the constraints0-p[o0
def get_region(region):
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    # Same thing, but for renewables. Get resources
    cols = ['PriceDate', 'Hour', 'Region ' + region + ' Wind']

    # Get the renewables
    comm = """SELECT r.pricedate, r.hour, r.value
                FROM rfrz_actual r
                WHERE r.pricedate >= '2020-01-01'
                AND r.reserve_zone=""" + region + """ AND r.resource='wind'"""
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    return df

def get_wind(iem):
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['PriceDate', 'Hour', 'Station Wind']

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp, MAX(actual.wind_speed)
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2020-01-01' AND iem_id='""" + iem + """'
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp"""
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df

def get_wind_sum():
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['PriceDate', 'Hour', 'Sum of All Wind']

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp, actual.wind_speed
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2020-01-01'"""
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

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp, MAX(actual.temp)
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2020-01-01' AND iem_id='""" + iem + """'
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp"""
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df


def get_iems():
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")
    cols = ['IEMs']

    # Execute SQL statement to get constraints and shadows
    comm = """SELECT DISTINCT iem_id
                    FROM weather.actual"""
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df