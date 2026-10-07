from django.utils.translation import get_language

from .translations import AGRICULTURE_UI


SUPPORTED_LANGUAGES = {
    "en",
    "hi",
    "mr",
    "gu",
    "bn",
    "ta",
    "te",
    "kn",
    "pa",
}


def agriculture_context(request):

    language = get_language() or "en"

    language = language.lower().split("-")[0]

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    return {
        "agriculture_language": language,
        "agriculture_ui": AGRICULTURE_UI.get(
            language,
            AGRICULTURE_UI["en"]
        ),
    }