# Path: projects/nbia-toolkit/src/nbiatoolkit/tests/test_auth.py
# this is a file that will test the auth.py file
# to run this test file use the following command from the src directory :
# pytest -v -s 

import pytest
from nbiatoolkit import OAuth2
import time 


@pytest.fixture(scope="session")
def oauth2():
    oauth = OAuth2()
    oauth.getToken()
    return oauth

@pytest.fixture(scope="session")
def failed_oauth2():
    oauth = OAuth2(username="bad_username", password="bad_password")
    oauth.getToken()
    return oauth

def test_getToken(oauth2):
    assert oauth2.access_token is not None

def test_expiry(oauth2):
    # expiry should be in the form of :'Tue Jun 29 13:58:57 2077'
    # and test for roughly 2 hours from now
    print(oauth2.expiry_time)
    assert oauth2.expiry_time <= time.ctime(time.time() + 7200)

def test_failed_oauth(failed_oauth2,capsys):
    # Answer should be Failed to get access token. Status code: 401
    # because the username and password are incorrect 
    # assert Status code 401
    captured = capsys.readouterr()
    assert failed_oauth2.access_token == 401

def test_failed_oauth_retried(failed_oauth2,capsys):
    failed_oauth2.getToken()
    captured = capsys.readouterr()
    assert failed_oauth2.access_token == 401

def test_getToken_valid_token(oauth2):
    # Test if the access token is valid and not expired
    assert oauth2.getToken() == oauth2.access_token

def test_getToken_failed_token(failed_oauth2, capsys):
    # Test if the access token retrieval fails with incorrect credentials
    assert failed_oauth2.getToken() == 401
    captured = capsys.readouterr()
