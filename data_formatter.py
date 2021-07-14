import pandas as pd
import numpy as np
import random
random.seed(4000)

def format(df):
    df = remove_blanks(df)
    df = cons_seperator(df)
    return df

# Format dataframe for further calculations
def remove_blanks(noBlanks):
    # Remove zero shadow prices
    df = noBlanks[noBlanks.Shadow != 0].copy()
    # Copy PriceDate
    df['PDCopy'] = df['PriceDate']

    # Map PriceDate and Hour Together for Later Use
    df['PDCopy'] = df['PDCopy'].map(lambda x: x.strftime("Day: %d/%m/%y Hour: "))
    df['PDCopy'] = df['PDCopy'] + df['Hour'].map(lambda x: str(x))

    # Drop Duplicates
    df = df.drop_duplicates('PDCopy', keep=False)
    df['PDCopy'] = df['Cons_name'] + " " + df['PDCopy']

    # Recopy Pricedate Back and Drop Copy
    df.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df

# Seperate constraints and make it into a dictionary
def cons_seperator(df):
    df['Cons_name'] = df['Cons_name'].map(lambda x: x.replace(" ", ""))
    return df
