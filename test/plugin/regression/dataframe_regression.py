from functools import partial
from pathlib import Path
import numpy as np
import pandas as pd

from .regression_base import RegressionMixIn


class DataFrameRegressionFixture(RegressionMixIn):

    DISPLAY_PRECISION = 17     # Decimal places
    DISPLAY_WIDTH = 1000       # Max. Chars on outputs
    DISPLAY_MAX_COLUMNS = 1000 # Max. Number of columns

    def __init__(self, baseline_datadir, obtained_datadir, request):
        """
        :type baseline_datadir: Path
        :type obtained_datadir: Path
        :type request: FixtureRequest
        """
        super().__init__(baseline_datadir, obtained_datadir, request)

        self._tolerances_dict = {}
        self._default_tolerance = {}

        self._pandas_display_option = (
            "display.precision", DataFrameRegressionFixture.DISPLAY_PRECISION,
            "display.width", DataFrameRegressionFixture.DISPLAY_WIDTH,
            "display.max_columns", DataFrameRegressionFixture.DISPLAY_MAX_COLUMNS
        )

    @staticmethod
    def dump_fn(filename: Path, data_frame: pd.DataFrame):
        data_frame.to_csv(
            filename,
            float_format=fr"%.{DataFrameRegressionFixture.DISPLAY_PRECISION}g"
        )

    @staticmethod
    def _check_data_types(k, obtained_column, baseline_column):
        obtained_data_type = obtained_column.values.dtype
        baseline_data_type = baseline_column.values.dtype
        if obtained_data_type != baseline_data_type:
            if np.issubdtype(obtained_data_type, np.number) and np.issubdtype(baseline_data_type, np.numeric):
                return

            error_msg = (
                f"Data type for data {k} are not the same between obtained and baseline.\n"
                f"Obtained: {obtained_data_type}\n"
                f"Baseline: {baseline_data_type}\n"
            )
            raise AssertionError(error_msg)

    @staticmethod
    def _check_data_shape(obtained_column, baseline_column):
        obtained_data_shape = obtained_column.values.shape
        baseline_data_shape = baseline_column.values.shape
        if obtained_data_shape != baseline_data_shape:
            error_msg = (
                f"Obtained and baseline data shape are not the same.\n"
                f"Obtained: {obtained_data_shape}\n"
                f"Baseline: {baseline_data_shape}\n"
            )
            raise AssertionError(error_msg)


    def check_fn(self, obtained_fn, baseline_fn):
        # __tracebackhide__ = True

        obtained_df = pd.read_csv(obtained_fn)
        baseline_df = pd.read_csv(baseline_fn)

        diff_dict = {}
        for k in set.union(set(obtained_df.keys()), set(baseline_df.keys())):
            obtained_column = obtained_df.get(k, None)
            baseline_column = baseline_df.get(k, None)

            if baseline_column is None:
                raise AssertionError(f"Could not find key '{k}' in baseline results.\n")

            if obtained_column is None:
                raise AssertionError(f"Could not find key '{k}' in obtained results.\n")

            self._check_data_types(k, obtained_column, baseline_column)
            self._check_data_shape(obtained_column, baseline_column)

            tolerance_args = self._tolerances_dict.get(k, self._default_tolerance)


            if np.issubdtype(obtained_column.values.dtype, np.inexact):
                not_close_mask = ~np.isclose(
                    obtained_column.values,
                    baseline_column.values,
                    equal_nan=True,
                    **tolerance_args
                )
            else:
                not_close_mask = obtained_column.values != baseline_column.values
                not_close_mask[np.logical_and(pd.isna(obtained_column.values), pd.isna(baseline_column.values))] = False

            if np.any(not_close_mask):
                diff_ids = np.where(not_close_mask)[0]
                diff_obtained_data = obtained_column[diff_ids]
                diff_baseline_data = baseline_column[diff_ids]
                if obtained_column.values.dtype == bool:
                    diffs = np.logical_xor(obtained_column, baseline_column)[diff_ids]
                elif obtained_column.values.dtype == object:
                    diffs = diff_obtained_data.copy()
                    diffs[:] = "?"
                else:
                    diffs = np.abs(obtained_column - baseline_column)[diff_ids]

                diff_table = pd.concat([diff_obtained_data, diff_baseline_data, diffs], axis=1)
                diff_table.columns = [f"obtained_{k}", f"baseline_{k}", "diff"]
                diff_dict[k] = diff_table

        if len(diff_dict) > 0:
            error_msg = "Values are not close within tolerance.\n"
            for k, diff_table in diff_dict.items():
                error_msg += f"{k}:\n{diff_table}\n\n"
            raise AssertionError(error_msg)


    def check(self, data_frame: pd.DataFrame, basename=None, tolerances=None, default_tolerance=None):
        # __tracebackhide__ = True

        for column in data_frame.columns:
            array = data_frame[column]

            # accept string
            if array.dtype == "O" and type(array[0]) is str:
                continue

            # reject objects and timedelta
            assert array.dtype not in ["O", "S", "a", "U", "V"], (
                f"Only numeric/string/datetime data is supported on dataframe_regression fixture.\n"
                f"Array with type {str(array.dtype)} was given."
            )

        self._tolerances_dict = {} if tolerances is None else tolerances
        self._default_tolerance = dict(atol=1e-8, rtol=1e-8) if default_tolerance is None else default_tolerance

        with pd.option_context(*self._pandas_display_option):
            self.perform_regression_check(
                dump_fn=partial(self.dump_fn, data_frame=data_frame),
                extension='.csv',
                basename=basename
            )