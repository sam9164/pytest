# -*- coding: utf-8 -*-
"""
Created on Sat May 16 14:07:23 2020

@author: Sen
"""
import pytest
import time

@pytest.mark.parametrize("e", [5,6,7])
@pytest.mark.parametrize("d", [1,2,3])
def test_request(data_regression, d, e):
    data_regression.check({"value": d + e})


def test_file_regression(file_regression):
    file_regression.check("123\nabc\n123\n")
