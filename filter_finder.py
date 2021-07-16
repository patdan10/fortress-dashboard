import psycopg2
import pandas as pd
import streamlit as st

tables = {'Region 1 Wind': 'rfrz_actual', 'Region 2 Wind': 'rfrz_actual', 'Region 3 Wind': 'rfrz_actual',
          'Region 4 Wind': 'rfrz_actual', 'Region 5 Wind': 'rfrz_actual', 'DALMP': 'prices'}

dps = {'Region 1 Wind': 'rfrz_actual.value', 'Region 2 Wind': 'rfrz_actual.value', 'Region 3 Wind': 'rfrz_actual.value',
          'Region 4 Wind': 'rfrz_actual.value', 'Region 5 Wind': 'rfrz_actual.value', 'DALMP': 'DALMP'}

endings = {'Region 1 Wind': " AND rfrz_actual.reserve_zone=1 AND rfrz_actual.resource='wind' AND rfrz_actual.pricedate >= '2020-01-01'",
            'Region 2 Wind': " AND rfrz_actual.reserve_zone=2 AND rfrz_actual.resource='wind' AND rfrz_actual.pricedate >= '2020-01-01'",
            'Region 3 Wind': " AND rfrz_actual.reserve_zone=3 AND rfrz_actual.resource='wind' AND rfrz_actual.pricedate >= '2020-01-01'",
            'Region 4 Wind': " AND rfrz_actual.reserve_zone=4 AND rfrz_actual.resource='wind' AND rfrz_actual.pricedate >= '2020-01-01'",
            'Region 5 Wind': " AND rfrz_actual.reserve_zone=5 AND rfrz_actual.resource='wind' AND rfrz_actual.pricedate >= '2020-01-01'",
           'DALMP': ''}

# Station Temp, Station Wind, Sum of Winds


def filter_helper(datapoint, direct, limit, iem):
    if direct == "Less Than":
        direct = "<"
    elif direct == "Greater Than":
        direct = ">"
    elif direct == "Equal To":
        direct = "="

    # Set up connection
    cols = ['PriceDate', 'Hour']
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")


    comm = commMaker(datapoint, direct, limit, iem)

    cur.execute(comm)
    out = cur.fetchall()
    conn.close()
    df = pd.DataFrame(data=out)
    if len(df) != 0:
        df.columns = cols
        df.dropna(axis=0, how='any', inplace=True)
        if datapoint == 'DALMP':
            df['PriceDate'] = df['PriceDate'].map(lambda x: x.date())
    return df


def commMaker(datapoint, direct, limit, iem):
    if 'Station' in datapoint:
        if 'Temperature' in datapoint:
            weath = 'temp'
        else:
            weath = 'wind_speed'
        comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp
                    FROM weather.actual
                    JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                    WHERE iso_utc.pricedate_spp >= '2020-01-01' AND iem_id='""" + iem + """'
                    GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp, actual.iem_id, actual.""" + weath + """
                    HAVING actual.""" + weath + str(direct) + str(limit)
    elif 'Sum' in datapoint:
        comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2020-01-01'
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp
                HAVING SUM(actual.wind_speed)""" + str(direct) + str(limit)
    elif 'Load' in datapoint:
        comm = """SELECT pricedate, hour FROM genmix
                WHERE genmix.pricedate >= '2020-01-01'
                GROUP BY pricedate, hour
                HAVING AVG(genmix.average_actual_load)""" + str(direct) + str(limit)
    elif 'DALMP' in datapoint:
        comm = """SELECT prices.pricedate, prices.hour
                FROM prices
                JOIN nodes ON nodes.node_id = prices.node_id
                WHERE DALMP""" + str(direct) + str(limit) + """
                AND nodes.nodename = '""" + iem + """'
                AND prices.pricedate >= '2020-01-01'"""
    else:
        comm = """SELECT pricedate, hour FROM """ + str(tables[datapoint]) + """
                WHERE """ + str(dps[datapoint]) + str(direct) + str(limit) + str(endings[datapoint])

    return comm
