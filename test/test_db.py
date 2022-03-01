# -*- coding: utf-8 -*-
"""
Created on Sat May 16 14:40:13 2020

@author: Sen
"""

import pytest
@pytest.fixture
def db():
    print('Connection successful')
    
    yield
    
    print('Connection closed')

def search_user(user_id):
    d = {
        '001': 'xiaoming'
    }
    return d[user_id]


def test_search(db):
    assert search_user('001') == 'xiaoming'