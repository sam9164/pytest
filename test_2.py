# -*- coding: utf-8 -*-
"""
Created on Sat May 16 14:07:23 2020

@author: Sen
"""
import pytest
import time

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

@pytest.fixture(scope='session', autouse=True)
def timer_session_scope():
    start = time.time()
    print('\nstart: {}'.format(time.strftime(DATE_FORMAT, time.localtime(start))))

    yield

    finished = time.time()
    print('finished: {}'.format(time.strftime(DATE_FORMAT, time.localtime(finished))))
    print('Total time cost: {:.3f}s'.format(finished - start))


@pytest.fixture(autouse=True)
def timer_function_scope():
    start = time.time()
    yield
    print(' Time cost: {:.3f}s'.format(time.time() - start))

@pytest.fixture
def postcode():
    return '010'

def test_failing():
    assert 1 == 2
    
@pytest.mark.skip
def test_func1():
    assert 1 == 1
    
def test_postcode(postcode):
    assert postcode == '010'