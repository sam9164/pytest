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
def data_regression(baseline_datadir, obtained_data_dir, request):
    from .regression.data_regression import DataRegressionFixture
    return DataRegressionFixture(baseline_datadir, obtained_data_dir, request)