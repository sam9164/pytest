import pandas as pd
import pytest

def test_data_frame(dataframe_regression):
    from datetime import datetime
    df = pd.DataFrame.from_dict(dict(
        key=['a', 'b', 'c'],
        float_value=[1.0, 2.0, 3.0],
        int_value=[1,2,3],
        date_value=[datetime(2022, 1, 20), datetime(2021, 2, 5, 15), datetime(2024, 3,15, 9, 30)]
    ))

    dataframe_regression.check(df)
