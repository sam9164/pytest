from functools import partial
from pathlib import Path
import collections.abc
import json

import numpy as np
from fractions import Fraction

from .regression_base import RegressionMixIn


class ValueRegression(RegressionMixIn):
    """
    Sequence/Scalar of Number/String regression fixture implementation on value_regression fixture
    """
    VALUE_ROWFORMAT = "{:>15s} {:>20s} {:>20s} {:>20s}\n"

    def __init__(self, baseline_datadir, obtained_datadir, request):
        """
        :type baseline_datadir: Path
        :type obtained_datadir: Path
        :type request: FixtureRequest
        """
        super().__init__(baseline_datadir, obtained_datadir, request)

        self._default_tolerance = dict(atol=1e-10, rtol=1e-10)

    @staticmethod
    def dump_fn(filename: Path, data: list):
        with open(filename, "w") as fp:
            json.dump(data, fp)

    def check_fn(self, obtained_fn: Path, baseline_fn: Path):
        __tracebackhide__ = True

        with open(obtained_fn, "r") as fp:
            obtained_list = json.load(fp)
        with open(baseline_fn, "r") as fp:
            baseline_list = json.load(fp)

        assert len(obtained_list) == len(baseline_list), (
            f"Data shapes are not the same:"
            f"  Obtained data length {len(obtained_list)}, Baseline data length {len(baseline_list)}.\n"
            f"  Obtained data: {str(obtained_list)}\n"
            f"  Baseline data: {str(baseline_list)}\n\n"
        )

        error_msg = ""
        for idx, (obtained, baseline) in enumerate(zip(obtained_list, baseline_list)):
            diff = False
            if np.issubdtype(type(obtained), np.inexact):
                if not np.isclose(obtained, baseline, equal_nan=True, **self._default_tolerance):
                    diff = True
            elif obtained != baseline:
                diff = True

            if diff:
                if error_msg == "":
                    error_msg += self.VALUE_ROWFORMAT.format("Obtained", "Baseline", "AbsDiff", "RelDiff")
                error_msg += self.VALUE_ROWFORMAT.format(
                    str(obtained),
                    str(baseline),
                    str(abs(obtained - baseline)) if isinstance(obtained, np.number) else "",
                    str(abs((obtained - baseline) / baseline)) if isinstance(obtained, np.number) \
                        and np.isclose(obtained, baseline, **self._default_tolerance) else ""
                )

        if error_msg != "":
            raise AssertionError(error_msg)

    def check(self, data, basename=None, obtained_filepath=None, default_tolerance=None):
        if np.isscalar(data):
            data = [data]
        elif isinstance(data, np.ndarray) and data.shape == ():
            # zero-dimensional numpy arrays
            data = [data[0]]
        else:
            data_type = type(data)
            data = list(data)
            if not isinstance(data, collections.abc.Sequence):
                raise AssertionError(f"Data must be a scalar or a sequence of scalar. Got {data_type.__name__} instead.")
            for d in data:
                assert np.isscalar(d), f"Data must be a scalar or a sequence of scalar. Got {type(d).__name__} instead."

        if default_tolerance:
            self._default_tolerance = default_tolerance

        self.perform_regression_check(
            dump_fn=partial(self.dump_fn, data=data),
            extension='.json',
            basename=basename,
            obtained_filepath=obtained_filepath
        )
