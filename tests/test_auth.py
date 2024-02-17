# Path: projects/nbia-toolkit/src/nbiatoolkit/tests/test_auth.py
# this is a file that will test the auth.py file
# to run this test file use the following command from the src directory :
# pytest -v -s

import pytest
from src.nbiatoolkit import OAuth2
import time
import requests


@pytest.fixture
def oauth() -> OAuth2:
    return OAuth2()


def test_oauth2(oauth: OAuth2) -> None:
    assert oauth.client_id == "NBIA"
    assert oauth.username != "nbia_guest"
    assert oauth.password != ""
    assert oauth.access_token is not None
    assert oauth.api_headers is not None
    assert oauth.expiry_time is not None
    assert oauth.refresh_token is not None
    assert oauth.refresh_expiry is not None
    assert oauth.scope is not None


def test_is_token_expired(oauth: OAuth2) -> None:
    assert oauth.is_token_expired() == False
    oauth.expiry_time = time.time() - 100
    assert oauth.is_token_expired() == True


def test_refresh_token_or_request_new(oauth: OAuth2) -> None:
    oauth.refresh_token_or_request_new()
    assert oauth.access_token is not None
    assert oauth.refresh_token is not None
    assert oauth.refresh_expiry is not None
    assert oauth.expiry_time is not None


def test_refresh_after_expiry(oauth: OAuth2) -> None:
    access_token_before = oauth.access_token

    oauth.expiry_time = time.time() - 100
    oauth.refresh_token_or_request_new()
    assert oauth.access_token is not None
    assert oauth.access_token != access_token_before

    assert oauth.refresh_token is not None
    assert oauth.refresh_expiry is not None
    assert oauth.expiry_time is not None
    assert oauth.is_token_expired() == False


def test_failed_refresh(oauth: OAuth2) -> None:
    oauth.refresh_token = ""
    with pytest.raises(AssertionError):
        oauth._refresh_access_token()

    oauth.refresh_token = "invalid_refresh_token"

    with pytest.raises(requests.exceptions.HTTPError):
        oauth._refresh_access_token()


def test_request_new_access_token(oauth: OAuth2) -> None:
    oauth.refresh_token = ""
    oauth.request_new_access_token()
    assert oauth.access_token is not None
    assert oauth.refresh_token is not None
    assert oauth.refresh_expiry is not None
    assert oauth.expiry_time is not None
    assert oauth.is_token_expired() == False


def test_logout(oauth: OAuth2) -> None:
    oauth.logout()
    assert oauth.access_token is None
    assert oauth.refresh_token is ""
    assert oauth.refresh_expiry is None
    assert oauth.expiry_time is None
    assert oauth.api_headers == {
        "Authorization": "Bearer None",
        "Content-Type": "application/json",
    }
    assert oauth.token_expiration_time == None
    assert oauth.refresh_expiration_time == None
    assert oauth.token_scope == None
    assert oauth.__repr__() == ""
    assert oauth.__str__() == ""
    assert oauth.username == ""
    assert oauth.client_id == ""
    assert oauth.password == ""
    assert oauth.base_url == ""
