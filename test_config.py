# -*- coding: utf-8 -*-
"""
Created on Sat May 16 15:22:33 2020

@author: Sen
"""

import pytest

def test_option1(pytestconfig):
    print('host: %s' % pytestconfig.getoption('host'))
    print('port: %s' % pytestconfig.getoption('port'))

def test_option2(config):
    print('host: %s' % config.getoption('host'))
    print('port: %s' % config.getoption('port'))