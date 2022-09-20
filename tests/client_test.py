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
