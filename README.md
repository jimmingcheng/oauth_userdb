# oauth_userdb
OAuth User Database


## Versions

### 1.0.4

- include client_id/client_secret in refresh request

### 1.0.3

- avoid writing null refresh_token if server does not include refresh_token in refresh request

### 1.0.2

- fix refresh token flow

### 1.0.1

- make scope an optional return type, make redirect_url an optional param (kwarg)

