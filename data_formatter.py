import datetime

def format(df):
    names, df = remove_blanks(df)
    return names, df

# Format dataframe for further calculations
def remove_blanks(df):
    oldday = datetime.datetime.today()-datetime.timedelta(days=14)
    # Remove zero shadow prices
    df2 = df[df.Shadow != 0].copy()
    df2 = df2[df2['PriceDate'] >= oldday.strftime("%Y-%m-%d")]
    df2 = df2.Cons_name.unique()
    df2.sort()
    # Recopy Pricedate Back and Drop Copy
    df['Percentage'] = df['Shadow'] / df.groupby(['PriceDate', 'Hour'])['Shadow'].transform('sum')

    df.sort_values(by=['PriceDate', 'Hour'], inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df2, df
