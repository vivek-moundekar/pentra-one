import mimetypes
import os
import re

from django.http import (
    Http404,
    HttpResponse,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404, redirect

from .models import Lesson


# ============================================================
# VIDEO CHUNK GENERATOR
# ============================================================

def _file_iterator(file_path, start=0, length=None, chunk_size=8192):

    with open(file_path, "rb") as video_file:

        video_file.seek(start)

        remaining = length

        while True:

            if remaining is None:

                data = video_file.read(chunk_size)

            else:

                if remaining <= 0:
                    break

                data = video_file.read(
                    min(chunk_size, remaining)
                )

            if not data:
                break

            yield data

            if remaining is not None:
                remaining -= len(data)


# ============================================================
# STUDENT LESSON VIDEO STREAM
# ============================================================

def lesson_video(request, lesson_id):

    # --------------------------------------------------------
    # EDUCATION LOGIN CHECK
    # --------------------------------------------------------

    if (
        not request.session.get("education_logged_in")
        or not request.user.is_authenticated
    ):
        return redirect("education:login")

    if request.session.get("education_role") != "student":
        return redirect("education:teacher_dashboard")


    # --------------------------------------------------------
    # GET LESSON
    # --------------------------------------------------------

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )


    # --------------------------------------------------------
    # CHECK VIDEO
    # --------------------------------------------------------

    if not lesson.video:

        raise Http404(
            "Video not available."
        )


    try:

        file_path = lesson.video.path

    except (ValueError, NotImplementedError):

        raise Http404(
            "Video file could not be accessed."
        )


    if not os.path.exists(file_path):

        raise Http404(
            "Video file does not exist."
        )


    # --------------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------------

    file_size = os.path.getsize(
        file_path
    )

    content_type, _ = mimetypes.guess_type(
        file_path
    )

    if not content_type:

        content_type = "video/mp4"


    # --------------------------------------------------------
    # RANGE HEADER
    # --------------------------------------------------------

    range_header = request.headers.get(
        "Range",
        ""
    ).strip()


    # --------------------------------------------------------
    # RANGE REQUEST
    # --------------------------------------------------------

    if range_header:

        range_match = re.match(
            r"bytes=(\d*)-(\d*)",
            range_header
        )

        if not range_match:

            response = HttpResponse(
                status=416
            )

            response[
                "Content-Range"
            ] = f"bytes */{file_size}"

            return response


        start_text = range_match.group(1)

        end_text = range_match.group(2)


        # ----------------------------------------------------
        # NORMAL RANGE
        # bytes=1000-2000
        # ----------------------------------------------------

        if start_text:

            start = int(start_text)

            if end_text:

                end = int(end_text)

            else:

                end = file_size - 1


        # ----------------------------------------------------
        # SUFFIX RANGE
        # bytes=-500
        # ----------------------------------------------------

        elif end_text:

            suffix_length = int(end_text)

            if suffix_length <= 0:

                response = HttpResponse(
                    status=416
                )

                response[
                    "Content-Range"
                ] = f"bytes */{file_size}"

                return response


            start = max(
                file_size - suffix_length,
                0
            )

            end = file_size - 1


        else:

            start = 0
            end = file_size - 1


        # ----------------------------------------------------
        # VALIDATE RANGE
        # ----------------------------------------------------

        if start >= file_size:

            response = HttpResponse(
                status=416
            )

            response[
                "Content-Range"
            ] = f"bytes */{file_size}"

            return response


        end = min(
            end,
            file_size - 1
        )


        if end < start:

            response = HttpResponse(
                status=416
            )

            response[
                "Content-Range"
            ] = f"bytes */{file_size}"

            return response


        content_length = (
            end - start + 1
        )


        # ----------------------------------------------------
        # HEAD REQUEST
        # ----------------------------------------------------

        if request.method == "HEAD":

            response = HttpResponse(
                status=206,
                content_type=content_type
            )

        else:

            response = StreamingHttpResponse(
                _file_iterator(
                    file_path,
                    start=start,
                    length=content_length
                ),
                status=206,
                content_type=content_type
            )


        response[
            "Content-Length"
        ] = str(content_length)

        response[
            "Content-Range"
        ] = (
            f"bytes {start}-{end}/{file_size}"
        )

        response[
            "Accept-Ranges"
        ] = "bytes"

        response[
            "Content-Disposition"
        ] = (
            f'inline; filename="{os.path.basename(file_path)}"'
        )

        response[
            "Cache-Control"
        ] = "no-cache"

        return response


    # --------------------------------------------------------
    # FULL FILE REQUEST
    # --------------------------------------------------------

    if request.method == "HEAD":

        response = HttpResponse(
            content_type=content_type
        )

    else:

        response = StreamingHttpResponse(
            _file_iterator(
                file_path
            ),
            content_type=content_type
        )


    response[
        "Content-Length"
    ] = str(file_size)

    response[
        "Accept-Ranges"
    ] = "bytes"

    response[
        "Content-Disposition"
    ] = (
        f'inline; filename="{os.path.basename(file_path)}"'
    )

    response[
        "Cache-Control"
    ] = "no-cache"

    return response