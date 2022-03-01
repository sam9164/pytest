# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pytest

def test_passing():
    assert (1, 2, 3) == (1, 2, 3)

@pytest.mark.parametrize("d", [1,2,3])
def test_request(data_regression, d):
    data_regression.check({"value": d})
