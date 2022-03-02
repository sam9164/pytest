from functools import partial
from pathlib import Path
import difflib

from .regression_base import RegressionMixIn


class FileRegressionFixture(RegressionMixIn):
    def __init__(self, baseline_datadir, obtained_datadir, request):
        """
        :type baseline_datadir: Path
        :type obtained_datadir: Path
        :type request: FixtureRequest
        """
        super().__init__(baseline_datadir, obtained_datadir, request)
        self._encoding = None
        self._binary = False

    @staticmethod
    def _check_fn_binary(obtained_fn: Path, baseline_fn: Path):
        __tracebackhide__ = True
        if obtained_fn.read_bytes() != baseline_fn.read_bytes():
            raise AssertionError(f"Binary files {obtained_fn} and {baseline_fn} differ.")

    def _check_fn_str(self, obtained_fn: Path, baseline_fn: Path):
        __tracebackhide__ = True
        obtained_lines = obtained_fn.read_text(encoding=self._encoding).splitlines()
        baseline_lines = baseline_fn.read_text(encoding=self._encoding).splitlines()

        if obtained_lines != baseline_lines:
            diff_lines = list(difflib.unified_diff(baseline_lines, obtained_lines))
            diff = f"Files Differ: {obtained_fn} and {baseline_fn}\n\n"
            if len(diff_lines) <= 500:
                diff += "\n".join(diff_lines)
                diff += "\n\n"
                try:
                    differ = difflib.HtmlDiff()
                    table_diff = differ.make_table(
                        fromlines=baseline_lines,
                        fromdesc=str(baseline_fn),
                        tolines=obtained_lines,
                        todesc=str(obtained_fn)
                    )
                    diff += table_diff
                except Exception as e:
                    diff += f"(Failed to generate html diff: {e})"
            else:
                diff += f"Files diff is too big ({len(diff_lines)} lines)."

            raise AssertionError(diff)

    def check_fn(self, obtained_fn, baseline_fn):
        __tracebackhide__ = True
        check_fn = self._check_fn_binary if self._binary else self._check_fn_str

        obtained_fn = Path(obtained_fn)
        baseline_fn = Path(baseline_fn)
        check_fn(obtained_fn, baseline_fn)

    def _dump_fn(self, filepath, contents, newline=None):
        mode = "wb" if self._binary else "w"
        with open(str(filepath), mode, encoding=self._encoding, newline=newline) as f:
            f.write(contents)

    def check(self, contents, encoding=None, extension=".txt", newline=None,
              binary=False, basename=None, obtained_filepath=None):
        """
        Checks the file contents against baseline version.
        :param str contents: content to be verified.
        :param str|None encoding: Encoding used to write file, if any.
        :param str extension: Extension of file.
        :param str|None newline: See `io.open` docs.
        :param bool binary: If the file is binary or text.
        :param obtained_filepath: ..see:: RegressionMixIn
        """
        __tracebackhide__ = True

        if binary and encoding:
            raise ValueError(f"Cannot have both binary ({binary}) or encoding ({encoding}) parameter at the same time.")

        if binary:
            assert isinstance(contents, bytes), f"Expected bytes contents but received {type(contents).__name__}."
        else:
            assert isinstance(contents, str), f"Expected text contents but received type {type(contents).__name__}."

        self._encoding = encoding
        self._binary = binary

        self.perform_regression_check(
            dump_fn=partial(self._dump_fn, contents=contents, newline=newline),
            extension=extension,
            basename=basename,
            obtained_filepath=obtained_filepath
        )
