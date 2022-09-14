from typing import Any
from typing import List
from oauth_userdb.client import Credentials
from oauth_userdb.client import OAuthUserDBClient


class DynamoDBOAuthUserDBClient(OAuthUserDBClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        redirect_url: str,
        scope: List[str],
        dynamodb_table: Any,
    ):
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            authorization_url=authorization_url,
            token_url=token_url,
            redirect_url=redirect_url,
            scope=scope,
        )

        self.table = dynamodb_table

    def get_saved_credentials(self, user_id: str) -> Credentials:
        resp = self.table.get_item(Key={'user_id': user_id})

        creds = resp['Item']
        return Credentials(
            access_token=creds['access_token'],
            expires_at=creds['expires_at'],
            id_token=creds['id_token'],
            refresh_token=creds['refresh_token'],
            scope=creds['scope'],
        )

    def save_credentials(self, user_id: str, creds: Credentials) -> None:
        creds_dict = dict(
            user_id=user_id,
            **creds._asdict()
        )
        self.table.put_item(Item=creds_dict)
