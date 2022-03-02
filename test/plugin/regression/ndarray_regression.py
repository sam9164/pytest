import zipfile
from functools import partial
from pathlib import Path
import numpy as np

from .regression_base import RegressionMixIn
from .helper import DictCheckMixIn

class NDArrayRegressionFixture(RegressionMixIn, DictCheckMixIn):
    THRESHOLD = 100
    ROWFORMAT = "{:>15s} {:>20s} {:>20s} {:>20s}\n"

    def __init__(self, baseline_datadir, obtained_datadir, request):
        """
        :type baseline_datadir: Path
        :type obtained_datadir: Path
        :type request: FixtureRequest
        """
        super().__init__(baseline_datadir, obtained_datadir, request)

        self._tolerance_dict = {}
        self._default_tolerance = dict(atol=1e-10, rtol=1e-10)

    @staticmethod
    def _load_fn(filepath: Path):
        try:
            with open(filepath, "rb") as f:
                result = dict(np.load(f))
        except (zipfile.BadZipfile, ValueError) as e:
            raise IOError(f"NPZ file {filepath} could not be loaded. Corrupt?") from e
        return result

    @staticmethod
    def _dump_fn(filepath, data_dict: dict):
        np.savez_compressed(str(filepath), **data_dict)


    def check_fn(self, obtained_fn, baseline_fn):
        __tracebackhide__ = True
        obtained_fn = Path(obtained_fn)
        baseline_fn = Path(baseline_fn)

        obtained_data = self._load_fn(obtained_fn)
        baseline_data = self._load_fn(baseline_fn)

        keys_matched, error_msg_key = self.check_dict_key_mismatch(obtained_data, baseline_data)
        keys_dtype_matched, error_msg_dtype = self.check_dict_data_types(obtained_data, baseline_data, type_getter=lambda x: (x.dtype, x.dtype.name))
        keys_shape_matched, error_msg_shape = self.check_dict_data_shapes(obtained_data, baseline_data)

        error_msg = error_msg_key + error_msg_dtype + error_msg_shape

        diff_dict = {}
        for k in keys_matched & keys_dtype_matched & keys_shape_matched:
            obtained_arr = obtained_data[k]
            baseline_arr = baseline_data[k]
            tolerance_args = self._tolerance_dict.get(k, self._default_tolerance)

            if np.issubdtype(obtained_arr.dtype, np.inexact):
                not_close_mask = ~np.isclose(obtained_arr, baseline_arr, equal_nan=True, **tolerance_args)
            else:
                not_close_mask = obtained_arr != baseline_arr

            if np.any(not_close_mask):
                diff_ids = [()] if not_close_mask.ndim == 0 else np.array(np.nonzero(not_close_mask)).T
                diff_dict[k] = (baseline_arr.size, baseline_arr.shape, diff_ids,
                                obtained_arr[not_close_mask], baseline_arr[not_close_mask])

        if len(diff_dict) > 0:
            error_msg += "Values are not sufficiently close.\n"
            for k, (size, shape, diff_ids, obtained_arr, baseline_arr) in diff_dict.items():
                error_msg += f"{k}: \n  Shape: {shape}\n"
                pct = 100 * len(diff_ids) / size
                error_msg += f"  Number of differences: {len(diff_ids)} / {size} ({pct:.1f}%)\n"
                if np.issubdtype(obtained_arr.dtype, np.number) and len(diff_ids) > 1:
                    abs_errors = abs(obtained_arr - baseline_arr)
                    error_msg += f"  Statistics are computed for differing elements only.\n" \
                                 f"  Stats for abs(obtained - baseline):\n" \
                                 f"    Max:    {abs_errors.max()}\n" \
                                 f"    Mean:   {abs_errors.mean()}\n" \
                                 f"    Median: {np.median(abs_errors)}\n"

                    idx_nonzero = np.array(np.nonzero(baseline_arr)).T
                    rel_errors = abs((obtained_arr[idx_nonzero]-baseline_arr[idx_nonzero])/baseline_arr[idx_nonzero])
                    if len(rel_errors) == 0:
                        error_msg += "  Relative errors are not reported since all baseline values are zero.\n"
                    else:
                        error_msg += f"  Stats for abs(obtained - baseline) / abs(baseline):\n"
                        if len(rel_errors) != len(abs_errors):
                            pct = 100 * len(rel_errors) / len(abs_errors)
                            error_msg += f"    Number of differing non-zero baseline results: {len(rel_errors)} / {len(abs_errors)} ({pct:.1f}%)\n" \
                                         f"    Relative errors are computed for the non-zero baseline results.\n"
                        else:
                            rel_errors = abs((obtained_arr - baseline_arr) / baseline_arr)
                        error_msg += f"    Max:    {rel_errors.max()}\n" \
                                     f"    Mean:   {rel_errors.mean()}\n" \
                                     f"    Median: {np.median(rel_errors)}\n"

                error_msg += "  Invididual errors:\n"
                if len(diff_ids) > self.THRESHOLD:
                    error_msg += f"    Only show first {self.THRESHOLD} mismatches.\n"
                    diff_ids = diff_ids[:self.THRESHOLD]
                    obtained_arr = obtained_arr[:self.THRESHOLD]
                    baseline_arr = baseline_arr[:self.THRESHOLD]
                error_msg += self.ROWFORMAT.format("Index", "Obtained", "Baseline", "Difference")
                for diff_id, obtained, baseline in zip(diff_ids, obtained_arr, baseline_arr):
                    diff_id_str = ", ".join(str(i) for i in diff_id)
                    if len(diff_id) != 1:
                        diff_id_str = f"({diff_id_str})"
                    error_msg += self.ROWFORMAT.format(
                        diff_id_str,
                        str(obtained),
                        str(baseline),
                        str(obtained - baseline) if isinstance(obtained, np.number) else ""
                    )
                    error_msg += "\n"
        
        if error_msg != "":
            raise AssertionError(error_msg)

    def check(self, data_dict, basename=None, obtained_filepath=None, tolerances=None, default_tolerance=None):
        """
        Checks a dictionary of NumPy ndarrays, containing only numeric or str data, against baseline

        :param Dict[str, np.ndarray] data_dict: dict of NumPy ndarrays or one array containing data.
        :param str basename: basename of the generated files. If not given the name of the test is used.
        :param dict tolerances: mapping for tolerance settings for specific data. Example:
                tolerances = {'key': dict(atol=1e-3)}

        :param dict default_tolerance: mapping of default tolerance setting. Example:
                default_tolerance = dict(atol=1e-10, rtol=1e-10)
            If not provided, will use the above 1e-10 for both atol and rtol.
        """
        __tracebackhide__ = True

        if not isinstance(data_dict, dict):
            raise TypeError(
                f"Only dictionaries with NumPy arrays or array-like objects"
                f"are supported in ndarray_regression fixture.\n"
                f"Object with type '{type(data_dict).__name__}' was given."
            )

        for k, arr in data_dict.items():
            assert isinstance(k, str), f"The dictionary keys must be strings. Found key with type '{type(k).__name__}'"
            arr = np.asarray(arr)
            data_dict[k] = arr

            # Accepted:
            #  - b: boolean
            #  - i: signed integer
            #  - u: unsigned integer
            #  - f: floating-point number
            #  - c: complex floating-point number
            #  - U: unicode string
            #  - M: datetime
            # Rejected:
            #  - m: timedelta
            #  - O: objects
            #  - S: zero-terminated bytes
            #  - V: void (raw data, structured arrays)

            if arr.dtype.kind not in ["b", "i", "u", "f", "c", "U", "M"]:
                raise TypeError(
                    f"Only numeric/str/datetime is supported on ndarrays_regression fixture.\n"
                    f"Array '{k}' with type '{arr.dtype}' was given."
                )

        self._tolerance_dict = tolerances if tolerances is not None else {}
        if default_tolerance is not None:
            self._default_tolerance = default_tolerance

        self.perform_regression_check(
            dump_fn=partial(self._dump_fn, data_dict=data_dict),
            extension=".npz",
            basename=basename,
            obtained_filepath=obtained_filepath
        )
