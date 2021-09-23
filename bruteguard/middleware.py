from typing import Dict

from django.http import HttpResponse


def brute_guard(get_response):
    def get_body(request) -> Dict[str, str]:
        body = request.body.decode()
        result: Dict[str, str] = {}
        if len(body):
            for item in body.split("&"):
                param = item.split("=")
                result[param[0]] = param[1]
        return result

    def middleware(request) -> HttpResponse:
        response = get_response(request)
        result = get_body(request)
        print(result)
        print(response.status_code)
        return response

    return middleware
