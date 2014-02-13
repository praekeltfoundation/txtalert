from django.contrib.auth.middleware import RemoteUserMiddleware


class HttpBasicAuthMiddleware(RemoteUserMiddleware):
    header = 'HTTP_AUTHORIZATION'
