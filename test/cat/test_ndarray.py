import pytest
import numpy as np

def test_ndarray_regression(ndarray_regression):
    ndarray_regression.check({
        'arr0d': np.array(1.0),
        'arr1d': np.array(['321', '1234']),
        'arr2d': np.array([[1, 2], [3, 4], [5, 6]]),
        'arr3d': np.array([[[1,2],[3,4]],[[5,6],[7,8]]])
    })

