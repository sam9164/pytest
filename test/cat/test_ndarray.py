import pytest
import numpy as np

def test_ndarray_regression(ndarray_regression):
    ndarray_regression.check({
        'arr0d': np.array(1.0),
        'arr1d': np.array(['321', '1234']),
        'arr2d': np.array([[1, 2], [3, 4], [5, 6]]),
        'arr3d': np.array([[[1,2],[3,4]],[[5,6],[7,8]]])
    })


def test_scalar_value(value_regression):
    value_regression.check(10)

def test_str_scalar_value(value_regression):
    value_regression.check('123')

def test_numeric_list(value_regression):
    value_regression.check([1,2,3,4,5])

def test_np_value_list(value_regression):
    value_regression.check(np.array([1.0, 2.0, 3.0]))

def test_mix_list(value_regression):
    value_regression.check([1, False, '123', np.nan])