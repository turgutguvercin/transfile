from django.utils import translation


class SubdomainInLanguageMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0] #considering the local host not need it in production
        subdomain = host.split(".")[0]
        lang_map = {
            "en": "en",
            "tr": "tr",
            "de": "de",
            "fr": "fr",
            "es": "es",
            "it": "it",
            "ru": "ru",
            "zh": "zh",
            "ja": "ja",
        }

        lang_code = lang_map.get(subdomain, "en")
        translation.activate(lang_code)

        request.LANGUAGE_CODE = lang_code #kinda optional just for request

        response = self.get_response(request)
        translation.deactivate()
        return response