import numpy as np
from datetime import datetime

def calculations(df):
    # Turn congestions to floats
    df['LoCongestRT'] = to_float(df['LoCongestRT'])
    df['HiCongestRT'] = to_float(df['HiCongestRT'])

    # Calculate shift factors
    df['LoShift'] = df['LoCongestRT'] / df['Shadow']
    df['HiShift'] = df['HiCongestRT'] / df['Shadow']

    # Calculate spreads
    df['Spread'] = df['HiPriceDA'] - df['HiPriceRT'] + df['LoPriceRT'] - df['LoPriceDA']

    # Calculate sum of winds
    df['WindSum'] = df['Region 1'] + df['Region 2'] + df['Region 3'] + df['Region 4'] + df['Region 5']

    # Calculate net loads
    df['NetLoad'] = df['AverageLoad'] - df['WindSum']
    
    # Build the name for the constraint
    name_builder = "BROKEN"
    
    # Get the supply name
    for potential_supply in df['NodeNameSupply']:
        if len(potential_supply) > 0:
            name_builder = ""
            name_builder += potential_supply
            name_builder += " - "
            break
    
    # Get the demand name
    for potential_demand in df['NodeNameDemand']:
        if len(potential_demand) > 0:
            name_builder += potential_demand
            break
    
    # Set the nodename in the dataframe
    df['NodesNames'] = name_builder

    df.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    df.reset_index(inplace=True, drop=True)

# Convert array to floats
def to_float(array):
    def f(x):
        return np.float(x)

    f2 = np.vectorize(f)
    return f2(array)

# Get seasons based on range
spring = range(80, 172)
summer = range(172, 264)
fall = range(264, 355)

# Set the seasons based on the day of the year
def seasons(df):
    df['Season'] = df['PriceDate'].map(lambda x: 1 if x.timetuple().tm_yday in spring else (2 if x.timetuple().tm_yday in summer else (3 if x.timetuple().tm_yday in fall else 4)))
    return df
