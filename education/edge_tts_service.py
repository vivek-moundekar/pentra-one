"""Edge TTS helper for Udaan Education chatbot.

Uses Microsoft Edge online neural voices through the ``edge-tts`` package.
No API key is required. Internet access is required when speech is generated.
"""

import asyncio
import edge_tts


VOICE_MAP = {
    "en-IN": "en-IN-NeerjaNeural",
    "hi-IN": "hi-IN-SwaraNeural",
    "mr-IN": "mr-IN-AarohiNeural",
    "gu-IN": "gu-IN-DhwaniNeural",
    "bn-IN": "bn-IN-TanishaaNeural",
    "ta-IN": "ta-IN-PallaviNeural",
    "te-IN": "te-IN-ShrutiNeural",
    "kn-IN": "kn-IN-SapnaNeural",
    "ml-IN": "ml-IN-SobhanaNeural",
    "pa-IN": "pa-IN-VaaniNeural",
    "ur-IN": "ur-IN-GulNeural",
}


def normalize_language(language):
    value = str(language or "en-IN").strip()
    if not value:
        return "en-IN"

    lower = value.lower()
    aliases = {
        "en": "en-IN",
        "en-in": "en-IN",
        "hi": "hi-IN",
        "hi-in": "hi-IN",
        "mr": "mr-IN",
        "mr-in": "mr-IN",
        "gu": "gu-IN",
        "gu-in": "gu-IN",
        "bn": "bn-IN",
        "bn-in": "bn-IN",
        "ta": "ta-IN",
        "ta-in": "ta-IN",
        "te": "te-IN",
        "te-in": "te-IN",
        "kn": "kn-IN",
        "kn-in": "kn-IN",
        "ml": "ml-IN",
        "ml-in": "ml-IN",
        "pa": "pa-IN",
        "pa-in": "pa-IN",
        "ur": "ur-IN",
        "ur-in": "ur-IN",
    }
    return aliases.get(lower, "en-IN")


async def _synthesize(text, language):
    language = normalize_language(language)
    voice = VOICE_MAP[language]

    communicator = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="+18%",
        volume="+0%",
        pitch="+0Hz",
    )

    audio_parts = []
    async for chunk in communicator.stream():
        if chunk.get("type") == "audio" and chunk.get("data"):
            audio_parts.append(chunk["data"])

    audio = b"".join(audio_parts)
    if not audio:
        raise RuntimeError("The voice service returned no audio.")
    return audio


def synthesize_speech(text, language):
    """Return MP3 bytes for the supplied text and language."""
    clean_text = str(text or "").strip()
    if not clean_text:
        raise ValueError("No text provided for speech synthesis.")

    return asyncio.run(_synthesize(clean_text, language))
