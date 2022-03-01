# -*- coding: utf-8 -*-
"""
Created on Sat May 16 15:21:36 2020

@author: Sen
"""
import pytest

def pytest_addoption(parser):
    parser.addoption('--host', action='store', help='host of db')
    parser.addoption('--port', action='store', default='8888', help='port of db')
    
@pytest.fixture
def config(request):
    return request.config