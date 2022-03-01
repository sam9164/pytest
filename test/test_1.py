# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pytest

db_list = [('redis', '1111'), ('elas', '2222')]
@pytest.fixture(params=db_list)
def param(request):
    return request.param


@pytest.fixture(autouse=True)
def db(param):
    print('\nSucceed to connect %s:%s' % param)

    yield

    print('\nSucceed to close %s:%s' % param)



def test_passing():
    assert (1, 2, 3) == (1, 2, 3)

@pytest.mark.skip(reason='skip')
def test_111():
    assert 1 != 1
    
user_list = ['1', '2', '3']
passwd_list = ['asfi123rooh', 'dsfjefhahfdhgkjahfkh', '123211']
@pytest.mark.parametrize('user, passwd', [*zip(user_list, passwd_list)])
def test_passwd_len(user, passwd):
    assert len(passwd) >= 8
    
