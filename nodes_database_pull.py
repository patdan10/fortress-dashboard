import psycopg2
import pandas as pd
import streamlit as st

# Get nodes
@st.cache(suppress_st_warning=True)
def get_node_names():
    cols = ['Node_ID', 'NodeName']
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    # Get nodenames
    comm = """SELECT DISTINCT p.node_id, n.nodename
            FROM prices p
            LEFT OUTER JOIN nodes n ON (n.node_id = p.node_id)
            WHERE pricedate >= '2020-01-01'
            """
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()
    return df

# Get piece of information for a node
def get_node_info(node, datapoint, name):
    cols = ['PriceDate', 'Hour', name]
    # Set up connection
    conn = psycopg2.connect(dbname='ISO', user='pdanielson', password='davidson456', host='fortdash.xyz')
    cur = conn.cursor()
    cur.execute("SET search_path TO spp;")

    # Get the piece of information for a specific node
    comm = """SELECT p.pricedate, p.hour, p.""" + datapoint + """
                FROM prices p
                WHERE p.node_id=""" + str(node)
    cur.execute(comm)
    out = cur.fetchall()
    df = pd.DataFrame(data=out)
    df.columns = cols
    conn.close()

    # Map the date for formatting purposes
    df['PriceDate'] = df['PriceDate'].map(lambda x: x.date())

    return df
