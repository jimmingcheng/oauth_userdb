import jwt
import requests
import time
from abc import ABCMeta
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import NamedTuple
from oauthlib.oauth2 import WebApplicationClient


class Credentials(NamedTuple):
    access_token: str
    expires_at: int
    id_token: Optional[str]
    refresh_token: Optional[str]
    scope: List[str]


class OAuthUserDBClient(WebApplicationClient, metaclass=ABCMeta):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        redirect_url: str,
        scope: List[str],
    ):
        super().__init__(
            client_id=client_id,
            scope=scope,
            redirect_url=redirect_url,
        )
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url

    def _fetch_credentials_from_provider(self, url: str, headers: dict, body: str) -> Credentials:
        resp = requests.post(self.token_url, headers=headers, data=body)

        token_data = self.parse_request_body_response(resp.text)

        print(token_data)
        return Credentials(
            access_token=token_data['access_token'],
            expires_at=int(time.time() + token_data['expires_at']),
            id_token=token_data.get('id_token'),
            refresh_token=token_data.get('refresh_token'),
            scope=token_data['scope'],
        )

    def _fetch_refreshed_credentials_from_provider(self) -> Credentials:
        url, headers, body = self.prepare_refresh_token_request(self.token_url)
        return self._fetch_credentials_from_provider(url, headers, body)

    def get_authorization_url(self, url_path: Optional[str] = None, **kwargs) -> str:
        url, _, _ = self.prepare_authorization_request(
            url_path if url_path else self.authorization_url,
            **kwargs
        )
        return url

    def exchange_code_for_tokens(self, code: str, **kwargs) -> Credentials:
        url, headers, body = self.prepare_token_request(
            self.token_url,
            code=code,
            client_secret=self.client_secret,
            **kwargs
        )

        return self._fetch_credentials_from_provider(url, headers, body)

    def get_credentials(self, user_id: str) -> Credentials:
        creds = self.get_saved_credentials(user_id)
        if int(time.time()) > creds.expires_at:
            creds = self._fetch_refreshed_credentials_from_provider()
            self.save_credentials(user_id, creds)
        return creds

    def save_user_and_credentials(self, code: str, user_id: Optional[str] = None, **kwargs) -> str:
        creds = self.exchange_code_for_tokens(code, **kwargs)

        if not user_id and creds.id_token:
            id_token_payload = jwt.decode(creds.id_token, options={'verify_signature': False})
            user_id = id_token_payload['sub']
            assert user_id, 'Unable to get user_id from OpenID token'

        assert user_id, 'user_id not provided'

        self.save_credentials(user_id, creds)
        return user_id

    @abstractmethod
    def get_saved_credentials(self, user_id: str) -> Credentials:
        pass

    @abstractmethod
    def save_credentials(self, user_id: str, creds: Credentials) -> None:
        pass
