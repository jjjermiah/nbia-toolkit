# Path: projects/nbia-toolkit/src/nbiatoolkit/tests/test_auth.py
# this is a file that will test the auth.py file
# to run this test file use the following command from the src directory :
# pytest -v -s 

import pytest
from nbiatoolkit import OAuth2
import time 
import requests

@pytest.fixture(scope="session")
def oauth2():
    oauth = OAuth2()
    oauth.getToken()
    return oauth

@pytest.fixture(scope="session")
def failed_oauth2():
    oauth = OAuth2(username="bad_username", password="bad_password")
    return oauth

def test_getToken(oauth2):
    assert oauth2.access_token is not None
    assert oauth2.token is not None

def test_expiry(oauth2):
    # expiry should be in the form of :'Tue Jun 29 13:58:57 2077'
    # and test for roughly 2 hours from now
    print(oauth2.expiry_time)
    assert oauth2.expiry_time <= time.ctime(time.time() + 7200)

def test_failed_oauth(failed_oauth2):
    # should raise requests.exceptions.RequestException
    with pytest.raises(requests.exceptions.RequestException):
        failed_oauth2.getToken()
        assert failed_oauth2.getToken() == 401
    assert failed_oauth2.access_token == -1
    assert failed_oauth2.token == -1
    assert failed_oauth2.getToken() == 401
    assert failed_oauth2.headers is None
    assert failed_oauth2.api_headers is None
    assert failed_oauth2.expiry_time is None
    assert failed_oauth2.refresh_token is None
    assert failed_oauth2.refresh_expiry is None
    assert failed_oauth2.scope is None


def test_getToken_valid_token(oauth2):
    # Test if the access token is valid and not expired
    assert oauth2.getToken() == oauth2.access_token
    assert oauth2.getToken() != 401
    assert oauth2.access_token != -1
    assert oauth2.token != -1
    assert oauth2.api_headers is not None
    assert oauth2.headers is not None
    assert oauth2.expiry_time is not None
    assert oauth2.refresh_token is not None
    assert oauth2.refresh_expiry is not None
    assert oauth2.scope is not None


