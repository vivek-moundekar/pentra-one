from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock

from faster_whisper import WhisperModel


# ------------------------------------------------------------
# MODEL CONFIG
# ------------------------------------------------------------

WHISPER_MODEL_SIZE = "base"

_model = None
_model_lock = Lock()


def get_whisper_model():
    """
    Load Whisper only once and keep it in memory.

    CPU + int8 is a good starting point for an 8 GB RAM laptop.
    """
    global _model

    if _model is None:
        with _model_lock:
            if _model is None:
                _model = WhisperModel(
                    WHISPER_MODEL_SIZE,
                    device="cpu",
                    compute_type="int8",
                )

    return _model


def transcribe_audio(uploaded_file, language=None):
    """
    Convert a Django UploadedFile into text using faster-whisper.

    language:
        None -> auto detect
        "en" -> English
        "hi" -> Hindi
        "mr" -> Marathi
    """

    suffix = Path(
        getattr(uploaded_file, "name", "voice.webm")
    ).suffix or ".webm"

    temp_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)

            temp_path = temp_file.name

        model = get_whisper_model()

        segments, info = model.transcribe(
            temp_path,
            language=language or None,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        transcript_parts = []

        for segment in segments:
            text = (segment.text or "").strip()

            if text:
                transcript_parts.append(text)

        transcript = " ".join(transcript_parts).strip()

        detected_language = getattr(
            info,
            "language",
            None,
        )

        return {
            "text": transcript,
            "language": detected_language,
        }

    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass
