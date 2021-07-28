import psycopg2
import pandas as pd

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

# With the given datapoint, create a sql command that will get the dates that apply
def filter_helper(datapoint, direct, limit, iem):
    # Change the direction to one SQL can interpret
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

    # Generate the correct SQL command
    comm = commMaker(datapoint, direct, limit, iem)

    # Execute the command
    cur.execute(comm)
    out = cur.fetchall()
    conn.close()
    df = pd.DataFrame(data=out)

    # If not zero length, then it was filtered
    if len(df) != 0:
        # Format the DF and return
        df.columns = cols
        df.dropna(axis=0, how='any', inplace=True)
        if datapoint == 'DALMP':
            df['PriceDate'] = df['PriceDate'].map(lambda x: x.date())
    return df


# Create the SQL command
def commMaker(datapoint, direct, limit, iem):
    # If its one of the stations, then create it with the correct datapoint
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
    # If its the sum, make that datapoint
    elif 'Sum' in datapoint:
        comm = """SELECT iso_utc.pricedate_spp, iso_utc.hour_spp
                FROM weather.actual
                JOIN weather.iso_utc ON iso_utc.dt = actual.dt
                WHERE iso_utc.pricedate_spp >= '2020-01-01'
                GROUP BY iso_utc.pricedate_spp, iso_utc.hour_spp
                HAVING SUM(actual.wind_speed)""" + str(direct) + str(limit)
    # If its the average load, geet that
    elif 'Load' in datapoint:
        comm = """SELECT pricedate, hour FROM genmix
                WHERE genmix.pricedate >= '2020-01-01'
                GROUP BY pricedate, hour
                HAVING AVG(genmix.average_actual_load)""" + str(direct) + str(limit)
    # IF its DALMP, get that
    elif 'DALMP' in datapoint:
        comm = """SELECT prices.pricedate, prices.hour
                FROM prices
                JOIN nodes ON nodes.node_id = prices.node_id
                WHERE DALMP""" + str(direct) + str(limit) + """
                AND nodes.nodename = '""" + iem + """'
                AND prices.pricedate >= '2020-01-01'"""
    # Get the rest
    else:
        comm = """SELECT pricedate, hour FROM """ + str(tables[datapoint]) + """
                WHERE """ + str(dps[datapoint]) + str(direct) + str(limit) + str(endings[datapoint])

    # Return them
    return comm
