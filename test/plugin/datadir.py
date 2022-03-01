import os
import shutil
import sys

from pathlib import Path

import pytest

test_root_dir = Path(__file__).parent.parent
data_root_dir = test_root_dir / 'data'
input_root_datadir = data_root_dir / 'input'
baseline_root_datadir = data_root_dir / 'baseline'
obtained_root_datadir = data_root_dir / 'obtained'

def make_datadir(request, root_dir: Path):
    test_dir = request.fspath.dirname
    rel_path = Path(test_dir).relative_to(test_root_dir)
    test_file_name = Path(request.fspath).stem

    test_datadir = root_dir / rel_path / test_file_name
    test_datadir.mkdir(parents=True, exist_ok=True)
    return test_datadir

@pytest.fixture
def input_datadir(request):
    return make_datadir(request, root_dir=input_root_datadir)

@pytest.fixture
def baseline_datadir(request):
    return make_datadir(request, root_dir=baseline_root_datadir)

@pytest.fixture
def obtained_data_dir(request):
    return make_datadir(request, root_dir=obtained_root_datadir)