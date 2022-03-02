from pathlib import Path

import pytest

from abc import ABC, abstractmethod

class RegressionMixIn(ABC):
    def __init__(self, baseline_datadir, obtained_datadir, request):
        """
        :param Path baseline_datadir: Fixture baseline_datadir.
        :param Path obtained_datadir: Fixture obtained_datadir.
        :param SubRequest request: Pytest request object.
        """
        self.request = request
        self.baseline_datadir = baseline_datadir
        self.obtained_datadir = obtained_datadir
        self.rebase = False # if true it will regenerate expected file.

    @abstractmethod
    def check_fn(self, obtained_fn, baseline_fn):
        """
        Compare two files contents and assert if the files differ. Function can safely assume that obtained
        file is already dumped and only care about comparison.

        :param Path obtained_fn: path to the obtained file during current testing
        :param Path baseline_fn: path to the baseline file
        """
        raise NotImplementedError()

    @abstractmethod
    def check(self, **kwargs):
        raise NotImplementedError()

    def perform_regression_check(
        self,
        dump_fn,
        extension,
        basename=None,
        obtained_filepath=None
    ):
        """
        First run will generate the baseline result. Following attempts will compare the obtained result with the baseline.
        If baseline result needs to be rebased, just enable `force_regen` argument.

        :param callable dump_fn: A function that receive an absolute file path as argument. Implementor
            must dump file in this path.
        :param str extension: Extension of files compared by this check.
        :param str obtained_filepath: complete path to use to write the obtained file. By
            default will prepend `.obtained` before the file extension.
        ..see: `data_regression.check` for `basename` arguments.
        """
        import re

        __tracebackhide__ = True

        if basename is None:
            if self.request.node.cls is not None:
                basename = re.sub(r"[\W]", "_", self.request.node.cls.__name__) + "_"
            else:
                basename = ""
            basename += re.sub(r"[\W]", "_", self.request.node.name)
            if basename.endswith('_'):
                basename = basename[:-1]
        basename = basename.lower()
        baseline_filepath = (self.baseline_datadir / basename).with_suffix(".baseline" + extension)
        generated_baseline_filepath = (self.obtained_datadir / basename).with_suffix(".baseline" + extension)

        def make_location_message(banner, filename):
            msg = [banner, f"- {filename}"]
            return "\n".join(msg)

        rebase = self.rebase or self.request.config.getoption("rebase")
        if not baseline_filepath.is_file():
            generated_baseline_filepath.parent.mkdir(parents=True, exist_ok=True)
            dump_fn(generated_baseline_filepath)
            msg = make_location_message("File not found in data directory, created:", generated_baseline_filepath)
            pytest.fail(msg)
        else:
            if obtained_filepath is None:
                obtained_filepath = (self.obtained_datadir / basename).with_suffix(".obtained" + extension)
            dump_fn(obtained_filepath)

            try:
                self.check_fn(obtained_filepath, baseline_filepath)
            except AssertionError:
                if rebase:
                    dump_fn(generated_baseline_filepath)
                    msg = make_location_message(
                        "Files differ and --rebase, regenerating file at:",
                        generated_baseline_filepath
                    )
                    pytest.xfail(msg)
                else:
                    raise
