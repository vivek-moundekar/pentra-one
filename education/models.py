from django.conf import settings
from django.db import models


# ============================================================
# EDUCATION PROFILE
# ============================================================

class EducationProfile(models.Model):

    STUDENT = "student"
    TEACHER = "teacher"

    ROLE_CHOICES = [
        (STUDENT, "Student"),
        (TEACHER, "Teacher"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="education_profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


# ============================================================
# CLASS
# ============================================================

class Class(models.Model):

    name = models.CharField(max_length=50)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


# ============================================================
# SUBJECT
# ============================================================

class Subject(models.Model):

    name = models.CharField(max_length=100)

    class_level = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    def __str__(self):
        return f"{self.class_level.name} - {self.name}"


# ============================================================
# CHAPTER
# ============================================================

class Chapter(models.Model):

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="chapters"
    )

    name = models.CharField(max_length=200)

    chapter_number = models.PositiveIntegerField(default=1)

    description = models.TextField(blank=True)

    class Meta:
        ordering = ["chapter_number"]

    def __str__(self):
        return (
            f"{self.subject.name} - "
            f"Chapter {self.chapter_number}: "
            f"{self.name}"
        )


# ============================================================
# LESSON
# ============================================================

class Lesson(models.Model):

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(max_length=200)

    lesson_number = models.PositiveIntegerField(default=1)

    description = models.TextField(blank=True)

    # --------------------------------------------------------
    # LOCAL VIDEO FILE
    # --------------------------------------------------------
    # Teacher uploads an MP4/video file.
    # File will be stored inside:
    # media/videos/
    # --------------------------------------------------------

    video = models.FileField(
        upload_to="videos/",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["lesson_number"]

    def __str__(self):
        return (
            f"{self.chapter.name} - "
            f"Lesson {self.lesson_number}: "
            f"{self.title}"
        )


# ============================================================
# TEST
# ============================================================

class Test(models.Model):

    title = models.CharField(max_length=200)

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name="tests"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_education_tests"
    )

    total_marks = models.PositiveIntegerField(default=0)

    # --------------------------------------------------------
    # TEST AVAILABILITY
    # --------------------------------------------------------
    #
    # Students can start the test only between these times.
    #

    available_from = models.DateTimeField()

    available_until = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.title} - "
            f"{self.chapter.name}"
        )

    @property
    def is_available(self):
        from django.utils import timezone

        now = timezone.now()

        return (
            self.available_from <= now
            <= self.available_until
        )

    @property
    def is_upcoming(self):
        from django.utils import timezone

        return timezone.now() < self.available_from

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.available_until


# ============================================================
# QUESTION
# ============================================================

class Question(models.Model):

    MCQ = "mcq"
    DESCRIPTIVE = "descriptive"

    QUESTION_TYPE_CHOICES = [
        (MCQ, "Multiple Choice Question"),
        (DESCRIPTIVE, "Descriptive"),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions"
    )

    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES
    )

    question_text = models.TextField()

    options = models.JSONField(
        default=dict,
        blank=True
    )

    correct_answer = models.TextField(
        blank=True
    )

    marks = models.PositiveIntegerField(default=1)

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return (
            f"{self.test.title} - "
            f"Question {self.order}"
        )


# ============================================================
# STUDENT ANSWER
# ============================================================

class StudentAnswer(models.Model):

    result = models.ForeignKey(
        "TestResult",
        on_delete=models.CASCADE,
        related_name="answers"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="student_answers"
    )

    answer_text = models.TextField(blank=True)

    marks_awarded = models.FloatField(default=0)

    class Meta:
        ordering = ["question__order"]

    def __str__(self):
        return (
            f"{self.result.student.username} - "
            f"Question {self.question.order}"
        )


# ============================================================
# TEST ATTEMPT
# ============================================================

class TestAttempt(models.Model):

    # --------------------------------------------------------
    # PROCTORING STATUS
    # --------------------------------------------------------

    ACTIVE = "active"
    SUBMITTED = "submitted"
    TERMINATED = "terminated"

    PROCTORING_STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (SUBMITTED, "Submitted"),
        (TERMINATED, "Terminated"),
    ]

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="attempts"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="education_test_attempts"
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_submitted = models.BooleanField(
        default=False
    )

    # --------------------------------------------------------
    # PROCTORING STATUS
    # --------------------------------------------------------

    proctoring_status = models.CharField(
        max_length=20,
        choices=PROCTORING_STATUS_CHOICES,
        default=ACTIVE
    )

    # Number of AI/object-detection warnings.
    warning_count = models.PositiveIntegerField(
        default=0
    )

    # If the teacher/system terminates the test,
    # this stores the reason.
    termination_reason = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    # Last time the student's proctoring connection
    # reported that it was active.
    last_proctoring_update = models.DateTimeField(
        null=True,
        blank=True
    )

    # --------------------------------------------------------
    # ANTI-CHEATING COUNTERS
    # --------------------------------------------------------

    tab_switch_count = models.PositiveIntegerField(
        default=0
    )

    copy_count = models.PositiveIntegerField(
        default=0
    )

    paste_count = models.PositiveIntegerField(
        default=0
    )

    fullscreen_exit_count = models.PositiveIntegerField(
        default=0
    )

    focus_loss_count = models.PositiveIntegerField(
        default=0
    )

    # Keyboard restriction events.
    keyboard_violation_count = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=["test", "student"],
                name="unique_test_attempt_per_student"
            )
        ]

        ordering = ["-started_at"]

    def __str__(self):

        return (
            f"{self.student.username} - "
            f"{self.test.title} - Attempt"
        )


# ============================================================
# PROCTORING EVENT
# ============================================================

class ProctoringEvent(models.Model):

    # --------------------------------------------------------
    # EVENT TYPES
    # --------------------------------------------------------

    CAMERA_STARTED = "camera_started"
    CAMERA_STOPPED = "camera_stopped"

    PHONE_DETECTED = "phone_detected"
    LAPTOP_DETECTED = "laptop_detected"
    BOOK_DETECTED = "book_detected"

    MULTIPLE_PERSONS = "multiple_persons"

    COPY_ATTEMPT = "copy_attempt"
    PASTE_ATTEMPT = "paste_attempt"
    CUT_ATTEMPT = "cut_attempt"

    TAB_SWITCH = "tab_switch"
    FOCUS_LOSS = "focus_loss"
    FULLSCREEN_EXIT = "fullscreen_exit"

    KEYBOARD_VIOLATION = "keyboard_violation"

    WARNING = "warning"

    TEST_TERMINATED = "test_terminated"

    EVENT_TYPE_CHOICES = [
        (CAMERA_STARTED, "Camera Started"),
        (CAMERA_STOPPED, "Camera Stopped"),

        (PHONE_DETECTED, "Phone Detected"),
        (LAPTOP_DETECTED, "Laptop Detected"),
        (BOOK_DETECTED, "Book Detected"),

        (MULTIPLE_PERSONS, "Multiple Persons"),

        (COPY_ATTEMPT, "Copy Attempt"),
        (PASTE_ATTEMPT, "Paste Attempt"),
        (CUT_ATTEMPT, "Cut Attempt"),

        (TAB_SWITCH, "Tab Switch"),
        (FOCUS_LOSS, "Focus Loss"),
        (FULLSCREEN_EXIT, "Fullscreen Exit"),

        (KEYBOARD_VIOLATION, "Keyboard Violation"),

        (WARNING, "Warning"),

        (TEST_TERMINATED, "Test Terminated"),
    ]

    # --------------------------------------------------------
    # RELATION TO ATTEMPT
    # --------------------------------------------------------

    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name="proctoring_events"
    )

    # Student who generated the event.
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="education_proctoring_events"
    )

    # Type of event.
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES
    )

    # Human-readable explanation.
    message = models.CharField(
        max_length=500,
        blank=True,
        default=""
    )

    # AI confidence score if available.
    # Example:
    # 0.91 = 91% confidence
    confidence = models.FloatField(
        null=True,
        blank=True
    )

    # Optional extra information from OpenCV/YOLO.
    #
    # Example:
    # {
    #     "object": "cell phone",
    #     "confidence": 0.91
    # }

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):

        return (
            f"{self.student.username} - "
            f"{self.get_event_type_display()} - "
            f"{self.created_at}"
        )


# ============================================================
# TEST RESULT
# ============================================================

class TestResult(models.Model):

    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="results"
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="education_test_results"
    )

    score = models.FloatField(default=0)

    total_marks = models.PositiveIntegerField(default=0)

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):

        return (
            f"{self.student.username} - "
            f"{self.test.title} - "
            f"{self.score}/{self.total_marks}"
        )