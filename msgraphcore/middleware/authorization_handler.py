from ._base_auth import AuthProviderBase
from ..constants import AUTH_MIDDLEWARE_OPTIONS
from ._middleware import BaseMiddleware


class AuthorizationHandler(BaseMiddleware):
    def __init__(self, auth_provider: AuthProviderBase, auth_provider_options=None):
        super().__init__()
        self.auth_provider = auth_provider
        self.auth_provider_options = auth_provider_options
        self.retry_count = 0

    def send(self, request, **kwargs):
        options = self._get_middleware_options(request)
        if options:
            self.auth_provider.scopes = options.scopes

        token = self.auth_provider.get_access_token()
        request.headers.update({'Authorization': 'Bearer {}'.format(token)})
        response = super().send(request, **kwargs)

        if response.status_code == 401 and self.retry_count < 2:
            self.retry_count += 1
            return self.send(request, **kwargs)

        return response

    def _get_middleware_options(self, request):
        return request.middleware_control.get(AUTH_MIDDLEWARE_OPTIONS)