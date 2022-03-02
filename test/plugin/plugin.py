import pytest


def pytest_addoption(parser):
    group = parser.getgroup("regressions")
    group.addoption(
        "--rebase",
        action="store_true",
        default=False,
        help="Rebase all regression fixture data files."
    )

@pytest.fixture
def data_regression(baseline_datadir, obtained_datadir, request):
    from .regression.data_regression import DataRegressionFixture
    return DataRegressionFixture(baseline_datadir, obtained_datadir, request)

@pytest.fixture
def dataframe_regression(baseline_datadir, obtained_datadir, request):
    from .regression.dataframe_regression import DataFrameRegressionFixture
    return DataFrameRegressionFixture(baseline_datadir, obtained_datadir, request)

@pytest.fixture
def file_regression(baseline_datadir, obtained_datadir, request):
    from .regression.file_regression import FileRegressionFixture
    return FileRegressionFixture(baseline_datadir, obtained_datadir, request)

@pytest.fixture
def ndarray_regression(baseline_datadir, obtained_datadir, request):
    from .regression.ndarray_regression import NDArrayRegressionFixture
    return NDArrayRegressionFixture(baseline_datadir, obtained_datadir, request)

@pytest.fixture
def value_regression(baseline_datadir, obtained_datadir, request):
    from .regression.value_regression import ValueRegression
    return ValueRegression(baseline_datadir, obtained_datadir, request)
