import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics

def line_fit(df, fcs):
    result = ("NAN", float("inf"))
    for iem in df['IEM'].unique():
        dfTemp = df[df['IEM'] == iem]
        inputs = np.asarray(dfTemp[['Station Wind', 'Station Temperature']])
        outputs = np.asarray(dfTemp['RTLMP'])
        absolute, regress = random_forest(inputs, outputs, fcs)
        if absolute < result[1]:
            result = (iem, absolute)


    return result

# The Random Forest regreessor
def random_forest(inputs, outputs, fcs):
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(inputs, outputs, test_size=0.33, shuffle=True)

    # Create regressor, with 1000 estimators
    regressor = RandomForestRegressor(n_estimators=10, random_state=42)

    # Fit data, predict with inputs to get outputs, get importances
    regressor.fit(X_train, y_train)
    y_pred = regressor.predict(inputs)
    importances = regressor.feature_importances_

    # Calculate metrics
    absolute = metrics.mean_absolute_error(outputs, y_pred)
    squared = metrics.mean_squared_error(outputs, y_pred)
    root = np.sqrt(squared)

    # Return
    return absolute, regressor
