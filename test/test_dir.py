# -*- coding: utf-8 -*-
"""
Created on Sat May 16 15:12:10 2020

@author: Sen
"""

def test_tmpdir(tmpdir):
    a_dir = tmpdir.mkdir('mytmpdir')
    a_file = a_dir.join('tmpfile.txt')
    a_file.write('pytest')
    assert a_file.read() == 'pytest'