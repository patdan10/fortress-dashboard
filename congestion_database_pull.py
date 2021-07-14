import psycopg2
import pandas as pd
import data_formatter

def get_constraints():
    cols = ['PriceDate', 'Hour', 'Cons_name', 'Shadow']
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
    formatted = pd.DataFrame(data=out)
    formatted.columns = cols

    formatted = data_formatter.format(formatted)

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

# Make string for use with sql statements
def make_string_prices_hours(dates, table):
    string = "("

    # For each date, make it an available option
    for d in dates:
        string += "(" + table + ".pricedate = '" + d[0].strftime("%Y-%m-%d") + "' AND " + table + ".hour = " + str(d[1]) +") OR "
    string = string[:-4] + ")"
    return string
