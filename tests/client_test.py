from unittest import mock
import pytest
import requests_mock
import time

from oauth_userdb.client import Credentials
from oauth_userdb.client import OAuthUserDBClient


CLIENT_ID = 'fake_client_id'
CLIENT_SECRET = 'fake_client_secret'
AUTH_URL = 'https://fake.url.com/auth'
TOKEN_URL = 'https://fake.url.com/token'
SCOPE = ['client_with_creds_scope']


class ClientWithExpiredCreds(OAuthUserDBClient):
    access_token = 'client_with_creds_access_token'
    expires_at = int(time.time()) - 3600
    id_token = 'client_with_creds_refresh_token'
    refresh_token = 'client_with_creds_refresh_token'

    def get_saved_credentials(self, user_id: str) -> Credentials:
        return Credentials(
            access_token=ClientWithExpiredCreds.access_token,
            expires_at=ClientWithExpiredCreds.expires_at,
            id_token=ClientWithExpiredCreds.id_token,
            refresh_token=ClientWithExpiredCreds.refresh_token,
            scope=SCOPE,
        )

    def save_credentials(self, user_id: str, creds: Credentials) -> None:
        pass


@pytest.fixture
def mock_client() -> OAuthUserDBClient:
    return ClientWithExpiredCreds(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        authorization_url=AUTH_URL,
        token_url=TOKEN_URL,
        scope=SCOPE,
    )


def test_save_user_and_credentials_retains_prior_refresh_token(
    mock_client: OAuthUserDBClient,
) -> None:
    new_access_token = 'new_access_token'
    new_expires_at = int(time.time()) + 7200

    with requests_mock.Mocker() as m:
        m.post(TOKEN_URL, text=f'access_token={new_access_token}&expires_at={new_expires_at}')
        creds = mock_client.get_credentials('fake_user_id')

    assert creds.refresh_token == ClientWithExpiredCreds.refresh_token


def test_token_request_has_expected_params(
    mock_client: OAuthUserDBClient,
) -> None:
    with mock.patch('oauth_userdb.client.requests.post') as mock_post:
        mock_post.return_value = mock.Mock(
            text=f'access_token=new_access_token&expires_at={int(time.time()) + 3600}'
        )
        mock_client.get_credentials('fake_user_id')
        mock_post.assert_called_once_with(
            TOKEN_URL,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=mock.ANY,
        )
        post_data = mock_post.call_args[1]['data']
        assert 'grant_type=refresh_token' in post_data
        assert f'client_id={CLIENT_ID}' in post_data
        assert f'client_secret={CLIENT_SECRET}' in post_data
        assert f'scope={" ".join(SCOPE)}' in post_data
        assert f'refresh_token={ClientWithExpiredCreds.refresh_token}' in post_data
