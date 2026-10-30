import re

_REPEATED_SLASHES = re.compile(r'/{2,}')


class CollapseSlashesMiddleware:
    """
    Treat "//api/start/" as "/api/start/".

    The mobile app requests https://www.ischool.ng//api/... ; without this the
    doubled slash misses every API route and the site's index.html is returned
    instead of JSON.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if '//' in request.path_info:
            request.path_info = _REPEATED_SLASHES.sub('/', request.path_info)
            request.path = _REPEATED_SLASHES.sub('/', request.path)
        return self.get_response(request)
