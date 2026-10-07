import os
from pathlib import Path

from django.core.files import File
from django.core.management.base import (
    BaseCommand,
)

from education.models import Lesson
from education.video_service import (
    VideoCompressionError,
    cleanup_temp_video,
    compress_existing_video,
)


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".mkv",
    ".avi",
    ".m4v",
    ".webm",
}


def to_mb(size):
    return size / 1024 / 1024


class Command(BaseCommand):

    help = (
        "Compress existing Lesson.video files "
        "to low-data 480p H.264 MP4."
    )

    def add_arguments(
        self,
        parser
    ):

        parser.add_argument(
            "--apply",
            action="store_true",
            help=(
                "Actually replace videos. "
                "Without this flag nothing is changed."
            ),
        )

        parser.add_argument(
            "--min-mb",
            type=float,
            default=5.0,
            help=(
                "Skip files smaller than this size. "
                "Default: 5 MB."
            ),
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help=(
                "Process only the first N videos. "
                "0 means all videos."
            ),
        )

        parser.add_argument(
            "--force",
            action="store_true",
            help=(
                "Also process files whose names already "
                "contain optimized_480p."
            ),
        )

    def handle(
        self,
        *args,
        **options
    ):

        apply_changes = options["apply"]
        min_mb = options["min_mb"]
        limit = options["limit"]
        force = options["force"]

        lessons = (
            Lesson.objects
            .exclude(video="")
            .exclude(video__isnull=True)
            .order_by("id")
        )

        if limit > 0:
            lessons = lessons[:limit]

        mode = (
            "APPLY"
            if apply_changes
            else "PREVIEW"
        )

        self.stdout.write(
            self.style.WARNING(
                f"\nUDAAN VIDEO COMPRESSION - {mode} MODE\n"
            )
        )

        if not apply_changes:
            self.stdout.write(
                "Preview mode still runs FFmpeg so you can "
                "see the real compressed size, but it does "
                "NOT change media files or database records.\n"
            )

        processed = 0
        replaced = 0
        skipped = 0
        failed = 0

        total_before = 0
        total_after = 0

        for lesson in lessons:

            temp_path = None

            try:
                if not lesson.video:
                    skipped += 1
                    continue

                relative_name = lesson.video.name

                if (
                    not force
                    and "optimized_480p" in relative_name
                ):
                    self.stdout.write(
                        f"[SKIP] Lesson {lesson.id}: "
                        "already optimized."
                    )

                    skipped += 1
                    continue

                try:
                    source_path = Path(
                        lesson.video.path
                    )

                except (
                    ValueError,
                    NotImplementedError
                ):
                    self.stdout.write(
                        self.style.ERROR(
                            f"[FAIL] Lesson {lesson.id}: "
                            "storage does not provide "
                            "a local file path."
                        )
                    )

                    failed += 1
                    continue

                if not source_path.exists():

                    self.stdout.write(
                        self.style.ERROR(
                            f"[MISSING] Lesson {lesson.id}: "
                            f"{relative_name}"
                        )
                    )

                    failed += 1
                    continue

                if (
                    source_path.suffix.lower()
                    not in VIDEO_EXTENSIONS
                ):

                    self.stdout.write(
                        f"[SKIP] Lesson {lesson.id}: "
                        "unsupported video extension."
                    )

                    skipped += 1
                    continue

                original_size = (
                    source_path.stat().st_size
                )

                if (
                    original_size
                    < min_mb * 1024 * 1024
                ):

                    self.stdout.write(
                        f"[SKIP] Lesson {lesson.id}: "
                        f"{to_mb(original_size):.1f} MB "
                        "(already small)."
                    )

                    skipped += 1
                    continue

                self.stdout.write(
                    (
                        f"\n[PROCESS] Lesson {lesson.id} | "
                        f"{lesson.title}\n"
                        f"          {relative_name}\n"
                        f"          Original: "
                        f"{to_mb(original_size):.1f} MB"
                    )
                )

                result = compress_existing_video(
                    source_path
                )

                temp_path = result[
                    "output_path"
                ]

                compressed_size = result[
                    "compressed_size"
                ]

                processed += 1

                reduction = (
                    (
                        original_size
                        - compressed_size
                    )
                    / original_size
                    * 100
                )

                self.stdout.write(
                    (
                        f"          Compressed: "
                        f"{to_mb(compressed_size):.1f} MB "
                        f"({reduction:.1f}% smaller)"
                    )
                )

                # Never replace a file with a larger one.
                if compressed_size >= original_size:

                    self.stdout.write(
                        self.style.WARNING(
                            "          KEEP: original file "
                            "is already smaller."
                        )
                    )

                    skipped += 1
                    continue

                total_before += original_size
                total_after += compressed_size

                if not apply_changes:

                    self.stdout.write(
                        self.style.WARNING(
                            "          PREVIEW ONLY: "
                            "nothing changed."
                        )
                    )

                    continue

                old_name = lesson.video.name

                clean_stem = "".join(
                    character
                    if (
                        character.isalnum()
                        or character in ("-", "_")
                    )
                    else "_"
                    for character
                    in source_path.stem
                ).strip("_")

                new_name = (
                    f"{clean_stem}_"
                    f"optimized_480p_"
                    f"lesson{lesson.id}.mp4"
                )

                # Save the compressed replacement first.
                with open(
                    temp_path,
                    "rb"
                ) as compressed_file:

                    lesson.video.save(
                        new_name,
                        File(
                            compressed_file,
                            name=new_name
                        ),
                        save=False
                    )

                    lesson.save(
                        update_fields=["video"]
                    )

                # Only after DB + new file succeed,
                # delete the old media file.
                try:
                    lesson.video.storage.delete(
                        old_name
                    )
                except Exception as error:

                    self.stdout.write(
                        self.style.WARNING(
                            "          WARNING: compressed "
                            "video was saved, but the old "
                            f"file could not be removed: {error}"
                        )
                    )

                replaced += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        "          DONE: media file and "
                        "Lesson.video reference updated."
                    )
                )

            except VideoCompressionError as error:

                failed += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"          FAILED: {error}"
                    )
                )

            except Exception as error:

                failed += 1

                self.stdout.write(
                    self.style.ERROR(
                        "          FAILED: "
                        f"{type(error).__name__}: "
                        f"{error}"
                    )
                )

            finally:

                if temp_path:
                    cleanup_temp_video(
                        temp_path
                    )

        self.stdout.write(
            "\n" + "=" * 65
        )

        self.stdout.write(
            "SUMMARY"
        )

        self.stdout.write(
            "=" * 65
        )

        self.stdout.write(
            f"Processed: {processed}"
        )

        self.stdout.write(
            f"Replaced:  {replaced}"
        )

        self.stdout.write(
            f"Skipped:   {skipped}"
        )

        self.stdout.write(
            f"Failed:    {failed}"
        )

        if total_before > 0:

            self.stdout.write(
                (
                    f"Size:      "
                    f"{to_mb(total_before):.1f} MB "
                    f"→ {to_mb(total_after):.1f} MB"
                )
            )

            self.stdout.write(
                (
                    f"Saved:     "
                    f"{to_mb(total_before - total_after):.1f} MB"
                )
            )

        if not apply_changes:

            self.stdout.write(
                self.style.WARNING(
                    "\nNothing was changed. "
                    "Add --apply when you are ready."
                )
            )
