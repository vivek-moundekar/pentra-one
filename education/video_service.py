import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path


class VideoCompressionError(Exception):
    """Raised when FFmpeg cannot compress a lesson video."""


def get_ffmpeg_path():
    """
    Return the FFmpeg executable installed on the computer.
    """
    ffmpeg = shutil.which("ffmpeg")

    if not ffmpeg:
        raise VideoCompressionError(
            "FFmpeg was not found in PATH."
        )

    return ffmpeg


def _run_ffmpeg(input_path, output_path):
    """
    Udaan low-data lesson-video profile.

    Output:
    - MP4
    - H.264 / libx264
    - maximum height 480p
    - 24 FPS
    - CRF 32
    - AAC mono 48 kbps
    - yuv420p
    - fast-start MP4 for browser playback
    """

    ffmpeg = get_ffmpeg_path()

    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_path),

        "-vf",
        "scale=-2:min(480\\,ih)",

        "-r",
        "24",

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "32",

        "-profile:v",
        "main",

        "-pix_fmt",
        "yuv420p",

        "-c:a",
        "aac",

        "-b:a",
        "48k",

        "-ac",
        "1",

        "-movflags",
        "+faststart",

        str(output_path),
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        error = (
            result.stderr.strip()
            or "Unknown FFmpeg error."
        )

        raise VideoCompressionError(
            f"FFmpeg compression failed: {error}"
        )

    if (
        not os.path.exists(output_path)
        or os.path.getsize(output_path) <= 0
    ):
        raise VideoCompressionError(
            "FFmpeg did not create a valid compressed video."
        )


def _clean_filename(filename):
    stem = Path(
        filename or "lesson_video"
    ).stem

    cleaned = "".join(
        character
        if (
            character.isalnum()
            or character in ("-", "_")
        )
        else "_"
        for character in stem
    ).strip("_")

    return cleaned or "lesson_video"


def compress_uploaded_video(uploaded_file):
    """
    Compress a new Django UploadedFile.

    Returns:
    {
        output_path,
        output_name,
        original_size,
        compressed_size,
        use_original
    }

    If FFmpeg creates a larger file, use_original=True.
    """

    suffix = (
        Path(
            getattr(
                uploaded_file,
                "name",
                "video.mp4"
            )
        ).suffix
        or ".mp4"
    )

    input_fd, input_path = tempfile.mkstemp(
        prefix="udaan_upload_",
        suffix=suffix,
    )
    os.close(input_fd)

    output_fd, output_path = tempfile.mkstemp(
        prefix="udaan_480p_",
        suffix=".mp4",
    )
    os.close(output_fd)

    try:
        with open(
            input_path,
            "wb"
        ) as destination:

            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        original_size = os.path.getsize(
            input_path
        )

        _run_ffmpeg(
            input_path,
            output_path
        )

        compressed_size = os.path.getsize(
            output_path
        )

        clean_name = _clean_filename(
            getattr(
                uploaded_file,
                "name",
                "lesson_video"
            )
        )

        output_name = (
            f"{clean_name}_optimized_480p_"
            f"{uuid.uuid4().hex[:8]}.mp4"
        )

        return {
            "output_path": output_path,
            "output_name": output_name,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "use_original": (
                compressed_size >= original_size
            ),
        }

    finally:
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except OSError:
            pass


def compress_existing_video(source_path):
    """
    Compress an existing Lesson.video file.

    This function NEVER deletes or replaces the source.
    The management command decides whether replacement is safe.
    """

    source_path = Path(source_path)

    if not source_path.exists():
        raise VideoCompressionError(
            f"Video file does not exist: {source_path}"
        )

    output_fd, output_path = tempfile.mkstemp(
        prefix="udaan_existing_480p_",
        suffix=".mp4",
    )
    os.close(output_fd)

    try:
        original_size = source_path.stat().st_size

        _run_ffmpeg(
            source_path,
            output_path
        )

        compressed_size = os.path.getsize(
            output_path
        )

        return {
            "output_path": output_path,
            "original_size": original_size,
            "compressed_size": compressed_size,
        }

    except Exception:
        cleanup_temp_video(
            output_path
        )
        raise


def cleanup_temp_video(path):
    """
    Safely delete a temporary video created by FFmpeg.
    """
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
