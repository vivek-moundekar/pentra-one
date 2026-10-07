import os
import base64
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST

from sarvamai import SarvamAI


# =========================================================
# AGRICULTURE VOICE AGENT
# =========================================================

SUPPORTED_LANGUAGES = {
    "en": "en-IN",
    "hi": "hi-IN",
    "mr": "mr-IN",
    "gu": "gu-IN",
    "bn": "bn-IN",
    "ta": "ta-IN",
    "te": "te-IN",
    "kn": "kn-IN",
    "pa": "pa-IN",
}


# Production voices chosen from Sarvam's current
# Bulbul v3 language/speaker support.
VOICE_MAP = {
    "en": "priya",
    "hi": "priya",
    "mr": "priya",
    "gu": "priya",
    "bn": "roopa",
    "ta": "ishita",
    "te": "priya",
    "kn": "ishita",
    "pa": "roopa",
}


MODEL = "bulbul:v3"

# Tuned for clear but natural agricultural guidance.
PACE = 0.98
TEMPERATURE = 0.7
SAMPLE_RATE = 24000


def normalize_language(language):
    """
    Convert Agriculture language codes/names
    into our internal 2-letter code.
    """

    if not language:
        return "en"

    language = str(language).strip().lower()

    language_names = {
        "english": "en",
        "hindi": "hi",
        "marathi": "mr",
        "gujarati": "gu",
        "bengali": "bn",
        "tamil": "ta",
        "telugu": "te",
        "kannada": "kn",
        "punjabi": "pa",
    }

    if language in language_names:
        return language_names[language]

    if "-" in language:
        language = language.split("-")[0]

    if language in SUPPORTED_LANGUAGES:
        return language

    return "en"


def extract_audio(response):
    """
    Extract the first base64 audio item from Sarvam's response.
    Works with both SDK objects and dictionary responses.
    """

    audios = None

    if hasattr(response, "audios"):
        audios = response.audios

    elif isinstance(response, dict):
        audios = response.get("audios")

    if not audios:
        raise RuntimeError("Sarvam returned no audio data.")

    audio_data = audios[0]

    if not audio_data:
        raise RuntimeError("Sarvam returned empty audio data.")

    return base64.b64decode(audio_data)


@require_POST
def voice_tts(request):
    """
    Agriculture Voice Agent endpoint.

    Receives:
        text
        language

    Returns:
        audio/mpeg
    """

    try:
        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------

        text = ""

        if request.content_type == "application/json":
            try:
                body = json.loads(
                    request.body.decode("utf-8")
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = {}

            text = str(
                body.get("text", "")
            ).strip()

            language = body.get(
                "language",
                "en",
            )

        else:
            text = request.POST.get(
                "text",
                "",
            ).strip()

            language = request.POST.get(
                "language",
                "en",
            )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not text:
            return JsonResponse(
                {
                    "error": "No text was provided."
                },
                status=400,
            )

        # Keep requests within Bulbul v3 REST limits.
        if len(text) > 2500:
            text = text[:2500]

        language = normalize_language(
            language
        )

        language_code = SUPPORTED_LANGUAGES[
            language
        ]

        speaker = VOICE_MAP[
            language
        ]

        # -------------------------------------------------
        # API KEY
        # -------------------------------------------------

        api_key = os.getenv(
            "SARVAM_API_KEY"
        )

        if not api_key:
            return JsonResponse(
                {
                    "error":
                        "SARVAM_API_KEY is not configured."
                },
                status=500,
            )

        # -------------------------------------------------
        # SARVAM CLIENT
        # -------------------------------------------------

        client = SarvamAI(
            api_subscription_key=api_key
        )

        # -------------------------------------------------
        # TEXT TO SPEECH
        # -------------------------------------------------

        response = client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            model=MODEL,
            speaker=speaker,
            pace=PACE,
            temperature=TEMPERATURE,
            speech_sample_rate=SAMPLE_RATE,
            output_audio_codec="mp3",
        )

        # -------------------------------------------------
        # AUDIO
        # -------------------------------------------------

        audio_bytes = extract_audio(
            response
        )

        if not audio_bytes:
            raise RuntimeError(
                "Generated audio is empty."
            )

        result = HttpResponse(
            audio_bytes,
            content_type="audio/mpeg",
        )

        result["Content-Length"] = str(
            len(audio_bytes)
        )

        result["Cache-Control"] = (
            "no-store, no-cache, must-revalidate"
        )

        return result

    except Exception as error:

        print(
            "AGRICULTURE VOICE ERROR:",
            error
        )

        return JsonResponse(
            {
                "error":
                    "Voice generation failed."
            },
            status=500,
        )