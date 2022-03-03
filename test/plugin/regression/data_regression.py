import json
from functools import partial
from pathlib import Path

from .regression_base import RegressionMixIn

def dict_compare_return_error(baseline: dict, obtained: dict):
    diff = []
    for key in set.union(set(baseline.keys()), set(obtained.keys())):
        if key not in baseline.keys() or key not in obtained.keys():
            diff += [f"Key diff: {str(key)}"]
        elif baseline[key] != obtained[key]:
            diff += [f"Value diff on {str(key)}: expect {baseline[key]}, obtained {obtained[key]}"]
    if diff:
        raise AssertionError("\n".join(diff))


class DataRegressionFixture(RegressionMixIn):
    def __init__(self, baseline_datadir, obtained_datadir, request):
        """
        :type baseline_datadir: Path
        :type obtained_datadir: Path
        :type request: FixtureRequest
        """
        super().__init__(baseline_datadir, obtained_datadir, request)

    def check_fn(self, obtained_fn, baseline_fn):
        __tracebackhide__ = True

        obtained_fn = Path(obtained_fn)
        baseline_fn = Path(baseline_fn)

        obtained_result = json.loads(obtained_fn.read_text())
        baseline_result = json.loads(baseline_fn.read_text())

        dict_compare_return_error(baseline_result, obtained_result)

    @staticmethod
    def _dump_fn(filepath: Path, data_dict):
        import json
        js = json.dumps(data_dict, indent="\t", sort_keys=True)
        filepath.write_text(js)

    def check(self, data_dict, basename=None, suffix=None, obtained_filepath=None):
        __tracebackhide__ = True

        self.perform_regression_check(
            dump_fn=partial(self._dump_fn, data_dict=data_dict),
            extension=".json",
            basename=basename,
            suffix=suffix,
            obtained_filepath=obtained_filepath
        )
