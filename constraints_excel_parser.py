import pandas as pd

# Read the excel
def get_excel(fp, fp2, fp3):
    maxes = pd.read_excel(fp2, sheet_name=None)
    mins = pd.read_excel(fp3, sheet_name=None)
    return pd.read_excel(fp, sheet_name=None), maxes, mins
