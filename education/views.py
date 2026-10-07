from functools import wraps
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode

from decouple import config
import requests

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.core.cache import cache
from django.core.files import File
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.urls import reverse
from django.db.models import Q

from .models import (
    EducationProfile,
    Class,
    Subject,
    Chapter,
    Lesson,
    Test,
    Question,
    TestResult,
    TestAttempt,
    StudentAnswer,
    ProctoringEvent,
)

from .forms import EducationRegistrationForm
from .ollama_service import ask_ollama, stream_ollama
from .edge_tts_service import synthesize_speech
from .image_service import prepare_image
from .whisper_service import transcribe_audio
from .video_service import (
    VideoCompressionError,
    cleanup_temp_video,
    compress_uploaded_video,
)


# ============================================================
# EDUCATION HOME
# ============================================================

def education_home(request):
    """
    Entry point of the Education module.

    The main Udaan website is public. Authentication begins
    only when a user enters the Education module.
    """

    if request.session.get("education_logged_in"):

        role = request.session.get("education_role")

        if role == "student":
            return redirect("education:student_dashboard")

        elif role == "teacher":
            return redirect("education:teacher_dashboard")

        # Remove invalid Education session
        request.session.pop("education_logged_in", None)
        request.session.pop("education_role", None)

    return redirect("education:login")


# ============================================================
# EDUCATION LOGIN
# ============================================================

def _finish_education_login(request, user, profile, remember_me=False):
    """Finish Education authentication and route by Education role."""

    # Normal username/password login reaches this function while request.user
    # is still anonymous, so Django must create the auth session.
    # Google/allauth has already authenticated request.user before this view,
    # therefore calling login() a second time would require an explicit backend
    # and raises ValueError when multiple backends are configured.
    if (
        not request.user.is_authenticated
        or request.user.pk != user.pk
    ):
        login(request, user)

    request.session["education_logged_in"] = True
    request.session["education_role"] = profile.role

    # Remember me -> keep login for 14 days.
    # Otherwise the Education session ends when the browser session ends.
    if remember_me:
        request.session.set_expiry(60 * 60 * 24 * 14)
    else:
        request.session.set_expiry(0)

    if profile.role == EducationProfile.STUDENT:
        return redirect("education:student_dashboard")

    if profile.role == EducationProfile.TEACHER:
        return redirect("education:teacher_dashboard")

    request.session.pop("education_logged_in", None)
    request.session.pop("education_role", None)
    logout(request)

    messages.error(request, "Invalid Education role.")
    return redirect("education:login")


def education_login(request):
    """Single Education login page for password and Google authentication."""

    if request.session.get("education_logged_in"):
        role = request.session.get("education_role")

        if role == EducationProfile.STUDENT:
            return redirect("education:student_dashboard")

        if role == EducationProfile.TEACHER:
            return redirect("education:teacher_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        role = request.POST.get("role", "").strip()
        remember_me = request.POST.get("remember_me") == "on"

        valid_roles = {
            EducationProfile.STUDENT,
            EducationProfile.TEACHER,
        }

        if role not in valid_roles:
            messages.error(request, "Please select Student or Teacher.")
            return render(
                request,
                "education/auth/login.html",
                {
                    "username_value": username,
                    "remember_me": remember_me,
                    "selected_role": role,
                },
            )

        if not username or not password:
            messages.error(request, "Please enter username and password.")
            return render(
                request,
                "education/auth/login.html",
                {
                    "username_value": username,
                    "remember_me": remember_me,
                    "selected_role": role,
                },
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(
                request,
                "education/auth/login.html",
                {
                    "username_value": username,
                    "remember_me": remember_me,
                    "selected_role": role,
                },
            )

        try:
            profile = EducationProfile.objects.get(user=user)
        except EducationProfile.DoesNotExist:
            messages.error(
                request,
                "This account is not registered for Education.",
            )
            return render(
                request,
                "education/auth/login.html",
                {
                    "username_value": username,
                    "remember_me": remember_me,
                    "selected_role": role,
                },
            )

        if profile.role != role:
            messages.error(
                request,
                f"This account is registered as {profile.get_role_display()}. Please select the correct role.",
            )
            return render(
                request,
                "education/auth/login.html",
                {
                    "username_value": username,
                    "remember_me": remember_me,
                    "selected_role": role,
                },
            )

        return _finish_education_login(
            request,
            user,
            profile,
            remember_me=remember_me,
        )

    return render(
        request,
        "education/auth/login.html",
        {
            "remember_me": False,
            "selected_role": EducationProfile.STUDENT,
        },
    )


def education_google_start(request):
    """
    Start Google authentication from the single Education login page.
    Role and Remember Me are carried through the OAuth redirect.
    """

    role = request.GET.get("role", "").strip()
    remember_me = request.GET.get("remember", "0") == "1"

    valid_roles = {
        EducationProfile.STUDENT,
        EducationProfile.TEACHER,
    }

    if role not in valid_roles:
        messages.error(
            request,
            "Please select Student or Teacher before continuing with Google.",
        )
        return redirect("education:login")

    # Keep these in the session as a fallback.
    request.session["education_google_role"] = role
    request.session["education_google_remember_me"] = remember_me
    request.session.modified = True

    # Carry role + remember choice in the `next` URL as well.
    complete_url = reverse("education:google_complete")
    complete_query = urlencode({
        "role": role,
        "remember": "1" if remember_me else "0",
    })
    next_url = f"{complete_url}?{complete_query}"

    google_login_url = reverse("google_login")
    google_query = urlencode({"next": next_url})

    return redirect(f"{google_login_url}?{google_query}")


def education_google_complete(request):
    """
    Complete Google authentication and send the user directly to the
    Student or Teacher dashboard.
    """

    if not request.user.is_authenticated:
        messages.error(
            request,
            "Google sign-in was not completed. Please try again.",
        )
        return redirect("education:login")

    # Prefer values carried in the return URL. Use session as fallback.
    role = request.GET.get("role", "").strip()
    if not role:
        role = request.session.get("education_google_role", "")

    remember_value = request.GET.get("remember")
    if remember_value is not None:
        remember_me = remember_value == "1"
    else:
        remember_me = request.session.get(
            "education_google_remember_me",
            False,
        )

    valid_roles = {
        EducationProfile.STUDENT,
        EducationProfile.TEACHER,
    }

    try:
        profile = EducationProfile.objects.get(user=request.user)

        # Existing Education users keep the role already stored in database.
        # This avoids sending a valid Google user back to the login page if
        # the selected role was lost during OAuth or selected differently.
        role = profile.role

    except EducationProfile.DoesNotExist:
        # First Google login: create the Education profile using the role
        # selected on the same login page.
        if role not in valid_roles:
            messages.error(
                request,
                "Please select Student or Teacher and try Google login again.",
            )
            logout(request)
            return redirect("education:login")

        profile = EducationProfile.objects.create(
            user=request.user,
            role=role,
        )

    # Temporary OAuth values are no longer needed.
    request.session.pop("education_google_role", None)
    request.session.pop("education_google_remember_me", None)

    return _finish_education_login(
        request=request,
        user=request.user,
        profile=profile,
        remember_me=remember_me,
    )


# ============================================================
# EDUCATION REGISTER
# ============================================================

def education_register(request):
    """
    Create an Education account.

    Uses EducationRegistrationForm to create:
    1. Django User
    2. EducationProfile
    """

    if request.method == "POST":

        form = EducationRegistrationForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Education account created successfully. Please login."
            )

            return redirect(
                "education:login"
            )

    else:

        form = EducationRegistrationForm()

    return render(
        request,
        "education/auth/register.html",
        {
            "form": form
        }
    )


# ============================================================
# EDUCATION LOGOUT / BACK TO UDAAN
# ============================================================

def education_logout(request):
    """
    Log out of Education and return to the public Udaan dashboard.

    Udaan itself does not require authentication.
    """

    request.session.pop(
        "education_logged_in",
        None
    )

    request.session.pop(
        "education_role",
        None
    )

    # Education login uses Django authentication internally,
    # so close that authenticated session when leaving Education.
    if request.user.is_authenticated:
        logout(request)

    return redirect(
        "dashboard"
    )


# ============================================================
# EDUCATION AUTHENTICATION DECORATOR
# ============================================================

def education_required(view_func):
    """
    Require an active Education login.

    The main Udaan website is public. Django authentication is
    established only when the user logs into the Education module.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        education_logged_in = request.session.get(
            "education_logged_in"
        )

        # A valid Education session needs both the Education flag
        # and the Django user session created by education_login().
        if (
            not education_logged_in
            or not request.user.is_authenticated
        ):

            request.session.pop(
                "education_logged_in",
                None
            )

            request.session.pop(
                "education_role",
                None
            )

            return redirect(
                "education:login"
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# STUDENT ROLE CHECK
# ============================================================

def student_required(view_func):
    """
    Allow only students to access the view.
    """

    @wraps(view_func)
    @education_required
    def wrapper(request, *args, **kwargs):

        role = request.session.get(
            "education_role"
        )

        if role != "student":

            messages.error(
                request,
                "This page is available only to students."
            )

            return redirect(
                "education:teacher_dashboard"
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# TEACHER ROLE CHECK
# ============================================================

def teacher_required(view_func):
    """
    Allow only teachers to access the view.
    """

    @wraps(view_func)
    @education_required
    def wrapper(request, *args, **kwargs):

        role = request.session.get(
            "education_role"
        )

        if role != "teacher":

            messages.error(
                request,
                "This page is available only to teachers."
            )

            return redirect(
                "education:student_dashboard"
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@student_required
def student_dashboard(request):
    """
    Student Education dashboard.
    """

    classes = Class.objects.all()

    return render(
        request,
        "education/student/dashboard.html",
        {
            "classes": classes,
        }
    )




# ============================================================
# STUDENT - MY PROGRESS
# ============================================================

@student_required
def student_progress(request):
    """
    Show the logged-in student's saved test results and progress.

    TestResult is already created when a student submits a test,
    so this page reads the stored results instead of creating
    duplicate progress records.
    """

    results = (
        TestResult.objects.filter(student=request.user)
        .select_related(
            "test",
            "test__chapter",
            "test__chapter__subject",
            "test__chapter__subject__class_level",
        )
        .order_by("-submitted_at", "-id")
    )

    progress_rows = []
    percentage_values = []

    for result in results:
        total = float(result.total_marks or 0)
        score = float(result.score or 0)

        if total > 0:
            percentage = round((score / total) * 100, 1)
        else:
            percentage = 0.0

        percentage_values.append(percentage)

        if percentage >= 80:
            performance = "Excellent"
        elif percentage >= 60:
            performance = "Good"
        elif percentage >= 40:
            performance = "Keep Improving"
        else:
            performance = "Needs Practice"

        progress_rows.append(
            {
                "result": result,
                "percentage": percentage,
                "performance": performance,
            }
        )

    tests_completed = len(progress_rows)

    if percentage_values:
        average_percentage = round(
            sum(percentage_values) / len(percentage_values),
            1,
        )
        best_percentage = round(max(percentage_values), 1)
        latest_percentage = percentage_values[0]
    else:
        average_percentage = 0
        best_percentage = 0
        latest_percentage = 0

    return render(
        request,
        "education/student/progress.html",
        {
            "progress_rows": progress_rows,
            "tests_completed": tests_completed,
            "average_percentage": average_percentage,
            "best_percentage": best_percentage,
            "latest_percentage": latest_percentage,
        },
    )


# ============================================================
# STUDENT - ASK DOUBT AI TUTOR
# ============================================================

@student_required
def ask_doubt(request):
    """Render the Education AI Tutor chat page."""
    return render(
        request,
        "education/student/ask_doubt.html"
    )


@student_required
def ask_doubt_api(request):
    """Local text/photo tutor, streamed answers, and account-owned chat history."""
    from .chat_memory import (
        conversation_for, load_messages, clear_messages, save_exchange, prompt_memory,
        student_name, stated_name, identity_answer,
    )
    from .math_solver import solve_arithmetic
    from django.db import DatabaseError, close_old_connections

    if request.method == "GET":
        try:
            history, has_more = load_messages(request.user)
            response = JsonResponse({"success": True, "history": history, "has_more": has_more})
            response["Cache-Control"] = "no-store"
            return response
        except DatabaseError:
            return JsonResponse({"success": False, "error": "Chat history is unavailable. Ask your teacher to run database migrations."}, status=503)
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST request required."}, status=405)

    # Existing local Whisper upload flow, unchanged.
    audio_file = request.FILES.get("audio")

    if audio_file is not None:

        voice_language = (
            request.POST.get(
                "language",
                "",
            )
            .strip()
            .lower()
        )

        language_map = {
            "auto": None,
            "en": "en",
            "en-in": "en",
            "hi": "hi",
            "hi-in": "hi",
            "mr": "mr",
            "mr-in": "mr",
            "gu": "gu",
            "gu-in": "gu",
            "bn": "bn",
            "bn-in": "bn",
            "ta": "ta",
            "ta-in": "ta",
            "te": "te",
            "te-in": "te",
            "kn": "kn",
            "kn-in": "kn",
            "ml": "ml",
            "ml-in": "ml",
            "pa": "pa",
            "pa-in": "pa",
            "ur": "ur",
            "ur-in": "ur",
        }

        whisper_language = language_map.get(
            voice_language,
            None,
        )

        # Basic upload-size protection: 15 MB.
        if audio_file.size > 15 * 1024 * 1024:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Voice recording is too large.",
                },
                status=400,
            )

        try:
            result = transcribe_audio(
                audio_file,
                language=whisper_language,
            )

        except Exception as error:
            print(
                "WHISPER ERROR:",
                type(error).__name__,
                error,
            )

            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "Unable to convert voice to text. "
                        "Please try recording again."
                    ),
                },
                status=500,
            )

        transcript = str(
            result.get("text", "")
        ).strip()

        if not transcript:
            return JsonResponse(
                {
                    "success": False,
                    "error": (
                        "No speech was detected. "
                        "Please speak clearly and try again."
                    ),
                },
                status=400,
            )

        return JsonResponse(
            {
                "success": True,
                "transcript": transcript,
                "language": result.get("language"),
            }
        )



    images = []
    try:
        if request.content_type == "multipart/form-data":
            body = request.POST.dict()
            body["stream"] = body.get("stream", "false").lower() == "true"
            uploads = request.FILES.getlist("images")
            if len(uploads) != 1:
                raise ValueError("Send photos one at a time using the photo queue.")
            images = [prepare_image(uploads[0])]
        else:
            body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError("Invalid request data.")
    except (ValueError, UnicodeDecodeError) as error:
        return JsonResponse({"success": False, "error": str(error)}, status=400)

    if body.get("action") == "clear":
        try:
            clear_messages(request.user)
            return JsonResponse({"success": True})
        except DatabaseError:
            return JsonResponse({"success": False, "error": "Could not clear saved chat. Please try again."}, status=503)

    question = str(body.get("question", "")).strip()
    if not question and images:
        question = "Read the question in this photo and explain the answer."
    if not question or len(question) > 3000:
        return JsonResponse({"success": False, "error": "Enter a question up to 3000 characters, or attach a photo."}, status=400)
    mode = "detail" if body.get("mode") == "detail" else "quick"
    requested_language = str(body.get("language", "auto")).strip().lower()

    language_names = {
        "en-in": "English", "en": "English",
        "hi-in": "Hindi", "hi": "Hindi",
        "mr-in": "Marathi", "mr": "Marathi",
        "gu-in": "Gujarati", "gu": "Gujarati",
        "bn-in": "Bengali", "bn": "Bengali",
        "ta-in": "Tamil", "ta": "Tamil",
        "te-in": "Telugu", "te": "Telugu",
        "kn-in": "Kannada", "kn": "Kannada",
        "ml-in": "Malayalam", "ml": "Malayalam",
        "pa-in": "Punjabi", "pa": "Punjabi",
        "ur-in": "Urdu", "ur": "Urdu",
    }

    # Resolve Auto mode on the server instead of asking the LLM to guess.
    # This prevents previous chat history from flipping English/Hindi responses.
    if requested_language == "auto":
        if any("\u0A80" <= ch <= "\u0AFF" for ch in question):
            language = "gu-in"
        elif any("\u0980" <= ch <= "\u09FF" for ch in question):
            language = "bn-in"
        elif any("\u0B80" <= ch <= "\u0BFF" for ch in question):
            language = "ta-in"
        elif any("\u0C00" <= ch <= "\u0C7F" for ch in question):
            language = "te-in"
        elif any("\u0C80" <= ch <= "\u0CFF" for ch in question):
            language = "kn-in"
        elif any("\u0D00" <= ch <= "\u0D7F" for ch in question):
            language = "ml-in"
        elif any("\u0A00" <= ch <= "\u0A7F" for ch in question):
            language = "pa-in"
        elif any(("\u0600" <= ch <= "\u06FF") or ("\u0750" <= ch <= "\u077F") for ch in question):
            language = "ur-in"
        elif any("\u0900" <= ch <= "\u097F" for ch in question):
            marathi_markers = (
                "आहे", "आहेत", "नाही", "मला", "तुम्ही", "मध्ये",
                "म्हणजे", "कसे", "आणि", "याचा", "याची", "करा"
            )
            language = "mr-in" if any(word in question for word in marathi_markers) else "hi-in"
        else:
            # Latin-script input is treated as English in Auto mode.
            # For Roman Hindi/Hinglish, select Hindi explicitly.
            language = "en-in"
    else:
        language = requested_language if requested_language in language_names else "en-in"

    language_name = language_names.get(language, "English")
    language_rule = (
        f"OUTPUT LANGUAGE IS LOCKED TO {language_name}. "
        f"Reply ONLY in {language_name}, regardless of the language used in the student's question. "
        f"Do not translate the student's question unless needed to understand it. "
        f"Do not switch languages because of chat history. "
        f"Use the natural native script of {language_name}. "
        f"Keep technical terms in English only when that is the normal educational usage, but explain them in {language_name}. "
        f"Write naturally like a teacher speaking to an Indian student."
    )
    try:
        chat = conversation_for(request.user)
        model_history, _ = load_messages(request.user, limit=12)

        # Use previous chat only when the latest message clearly looks like a follow-up.
        # This prevents the small local model from answering an older topic instead
        # of the student's current question.
        followup_markers = (
            "this", "that", "it", "these", "those", "again", "previous",
            "above", "same", "why", "how so", "what about", "and then",
            "iska", "iske", "isne", "ye", "vo", "woh", "phir", "dubara",
            "क्यों", "कैसे", "इसका", "इसके", "यह", "वह", "फिर",
            "का?", "की?", "के?",
            "याचा", "याची", "याचे", "हे", "ते", "पुन्हा", "का", "कसे",
        )
        question_lower = question.casefold().strip()
        looks_like_followup = (
            len(question_lower.split()) <= 8
            and any(marker in question_lower for marker in followup_markers)
        ) or question_lower.startswith((
            "why ", "how ", "what about ", "and ", "then ",
            "क्यों ", "कैसे ", "फिर ", "का ", "कसे ",
        ))

        history_for_model = model_history if looks_like_followup else []
        known_name = (stated_name(question) or student_name(request.user)) if not images else None
        # Existing deterministic identity/math helpers were built for the original
        # Auto/English/Hindi/Marathi flow. For newly added languages, let Ollama
        # answer so the selected language and native script are preserved.
        direct_helper_languages = {"en", "en-in", "hi", "hi-in", "mr", "mr-in"}
        direct_answer = (
            identity_answer(question, language, known_name)
            or solve_arithmetic(question, language)
        ) if (not images and language in direct_helper_languages) else None
    except DatabaseError:
        return JsonResponse({"success": False, "error": "Chat storage is unavailable. Ask your teacher to run database migrations."}, status=503)
    system_prompt = (
        "You are Udaan AI, a friendly education tutor. " + language_rule + "\n"
        "The student's LATEST question is the main task. Answer exactly that question. "
        "Do not answer an older topic, do not continue an earlier answer unless the latest question clearly refers to it, "
        "and do not invent a different question. "
        "If the latest question is unclear, ask one short clarification instead of guessing. "
        "Respond naturally to greetings. Explain concepts clearly and show essential maths steps. "
        "For ambiguous maths notation, state your grouping. "
        + ("Keep the answer concise and directly relevant. " if mode == "quick" else "Give a detailed but directly relevant explanation with examples. ")
    )
    if known_name:
        system_prompt += "The student previously stated this name (data): " + json.dumps(known_name, ensure_ascii=False) + ". "
    if images:
        system_prompt += "Read the attached photo, state the visible question briefly, and answer it. Ask for a clearer photo if unreadable. "
    # Repeat the selected output language in the latest user message as well.
    # Small local models sometimes underweight the system message, so this makes
    # the selected language deterministic even when the question is in English.
    prompt = (
        f"Answer this question ONLY in {language_name}. "
        f"Use the natural native script of {language_name}.\n"
        f"Question: {question}"
    )
    saved_question = ("[Photo attached] " if images else "") + question

    def error_text(error):
        if isinstance(error, requests.exceptions.Timeout):
            return "AI took too long. Try a clearer crop or Quick mode."
        if isinstance(error, requests.exceptions.ConnectionError):
            return "Ollama is offline. Please start Ollama and try again."
        if isinstance(error, RuntimeError):
            return str(error)
        if isinstance(error, DatabaseError):
            return "The answer could not be saved. Please refresh and try again."
        return "Udaan AI could not finish. Please try again."

    if body.get("stream") is True:
        def event(kind, **data):
            return json.dumps({"type": kind, **data}, ensure_ascii=False) + "\n"

        def generate():
            answer_parts = []
            try:
                # Flush an initial event while Ollama loads/reads the photo.
                yield event("status", text="Reading photo…" if images else "Thinking…")
                chunks = [direct_answer] if direct_answer else stream_ollama(prompt, images=images or None, mode=mode, system=system_prompt, history=history_for_model)
                for chunk in chunks:
                    answer_parts.append(chunk)
                    yield event("chunk", text=chunk)
                answer = "".join(answer_parts).strip()
                if not answer:
                    raise RuntimeError("Udaan AI did not return an answer.")
                save_exchange(request.user, chat.pk, saved_question, answer)
                yield event("done", saved=True)
            except Exception as error:
                yield event("error", error=error_text(error))
            finally:
                close_old_connections()

        response = StreamingHttpResponse(generate(), content_type="application/x-ndjson; charset=utf-8")
        response["Cache-Control"] = "no-store"
        response["X-Accel-Buffering"] = "no"
        return response
    try:
        answer = direct_answer or ask_ollama(prompt, images=images or None, mode=mode, system=system_prompt, history=history_for_model).strip()
        if not answer:
            raise RuntimeError("Udaan AI did not return an answer.")
        save_exchange(request.user, chat.pk, saved_question, answer)
        return JsonResponse({"success": True, "answer": answer})
    except Exception as error:
        return JsonResponse({"success": False, "error": error_text(error)}, status=503)


# ============================================================
# STUDENT - AI TUTOR TEXT TO SPEECH
# ============================================================

@student_required
def text_to_speech(request):
    """Generate an MP3 voice for an AI Tutor response using Edge TTS."""
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "error": "POST request required."},
            status=405,
        )

    try:
        body = json.loads(request.body.decode("utf-8"))
        if not isinstance(body, dict):
            raise ValueError("Invalid request data.")
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse(
            {"success": False, "error": "Invalid request data."},
            status=400,
        )

    text = str(body.get("text", "")).strip()
    language = str(body.get("language", "en-IN")).strip()

    if not text:
        return JsonResponse(
            {"success": False, "error": "No text provided."},
            status=400,
        )

    # Prevent very large speech jobs from one browser request.
    if len(text) > 5000:
        return JsonResponse(
            {"success": False, "error": "This answer is too long for voice playback."},
            status=400,
        )

    supported_languages = {
        "en-IN", "hi-IN", "mr-IN", "gu-IN", "bn-IN",
        "ta-IN", "te-IN", "kn-IN", "ml-IN", "pa-IN", "ur-IN",
    }
    if language not in supported_languages:
        language = "en-IN"

    try:
        audio = synthesize_speech(text, language)
    except Exception as error:
        print("EDGE TTS ERROR:", type(error).__name__, error)
        return JsonResponse(
            {
                "success": False,
                "error": "Could not generate voice. Check your internet connection and try again.",
            },
            status=503,
        )

    response = HttpResponse(audio, content_type="audio/mpeg")
    response["Content-Disposition"] = 'inline; filename="udaan_voice.mp3"'
    response["Cache-Control"] = "no-store"
    return response


# ============================================================
# STUDENT - AVAILABLE TESTS
# ============================================================


@student_required
def student_tests(request):
    """
    Show only upcoming and currently available tests.

    Completed tests are hidden from My Tests as soon as a TestResult
    exists for the logged-in student.

    Expired tests are also hidden automatically.

    TestResult records are never deleted here, so completed results
    remain available in My Progress.
    """

    now = timezone.now()

    completed_test_ids = set(
        TestResult.objects.filter(
            student=request.user
        ).values_list(
            "test_id",
            flat=True
        )
    )

    tests = (
        Test.objects.select_related(
            "chapter",
            "chapter__subject",
            "chapter__subject__class_level",
        )
        .prefetch_related("questions")
        .exclude(id__in=completed_test_ids)
        .filter(available_until__gte=now)
        .order_by("available_from", "id")
    )

    attempts = (
        TestAttempt.objects.filter(
            student=request.user
        )
        .select_related("test")
    )

    attempt_by_test = {
        attempt.test_id: attempt
        for attempt in attempts
    }

    test_items = []

    available_count = 0
    upcoming_count = 0

    for test in tests:

        if now < test.available_from:
            status = "upcoming"
            upcoming_count += 1
        else:
            status = "available"
            available_count += 1

        test_items.append(
            {
                "test": test,
                "question_count": test.questions.count(),
                "attempt": attempt_by_test.get(test.id),
                "status": status,
            }
        )

    completed_count = TestResult.objects.filter(
        student=request.user
    ).count()

    return render(
        request,
        "education/student/tests.html",
        {
            "test_items": test_items,
            "available_count": available_count,
            "upcoming_count": upcoming_count,
            "completed_count": completed_count,
        },
    )


# ============================================================
# STUDENT - DELETE COMPLETED/EXPIRED TEST FROM MY TESTS
# ============================================================

@student_required
def delete_student_test(request, test_id):
    """
    Remove a test from the student's personal test list.

    IMPORTANT:
    - Upcoming tests cannot be deleted.
    - Currently available tests cannot be deleted.
    - A student cannot delete the teacher's Test object.
    - Only the student's own result/attempt records are removed.
    - Expired tests can be removed.
    - Completed/terminated tests can be removed.
    """

    if request.method != "POST":
        return redirect("education:student_tests")

    test = get_object_or_404(Test, id=test_id)

    now = timezone.now()

    # Upcoming test -> never allow deletion.
    if now < test.available_from:
        messages.error(
            request,
            "Upcoming tests cannot be deleted."
        )
        return redirect("education:student_tests")

    # Currently available test -> never allow deletion.
    if now <= test.available_until:
        messages.error(
            request,
            "This test is currently available and cannot be deleted."
        )
        return redirect("education:student_tests")

    # --------------------------------------------------------
    # Delete only this student's records.
    # --------------------------------------------------------

    TestResult.objects.filter(
        test=test,
        student=request.user
    ).delete()

    TestAttempt.objects.filter(
        test=test,
        student=request.user
    ).delete()

    messages.success(
        request,
        "Test removed from your test history."
    )

    return redirect("education:student_tests")



# ============================================================
# STUDENT - START TEST
# ============================================================

@student_required
def start_test(request, test_id):

    """
    Start a scheduled test.

    Authentication:
        @student_required

    Checks:
        1. Test exists.
        2. Test is currently available.
        3. Student has not attempted it before.

    First attempt:
        - Creates TestAttempt.
        - Records started_at automatically.
        - Sets expires_at to the teacher's termination time.
        - Opens the question page.
    """

    test = get_object_or_404(
        Test.objects.prefetch_related("questions"),
        id=test_id
    )

    now = timezone.now()

    # --------------------------------------------------------
    # TEST HAS NOT STARTED
    # --------------------------------------------------------

    if now < test.available_from:

        messages.error(
            request,
            "This test has not started yet."
        )

        return redirect(
            "education:student_tests"
        )

    # --------------------------------------------------------
    # TEST HAS TERMINATED
    # --------------------------------------------------------

    if now > test.available_until:

        messages.error(
            request,
            "This test has been terminated."
        )

        return redirect(
            "education:student_tests"
        )

    # --------------------------------------------------------
    # CHECK PREVIOUS ATTEMPT
    # --------------------------------------------------------

    previous_attempt = TestAttempt.objects.filter(
        test=test,
        student=request.user
    ).first()

    if previous_attempt:

        messages.error(
            request,
            "You have already attempted this test. "
            "Only one attempt is allowed."
        )

        return redirect(
            "education:student_tests"
        )

    # --------------------------------------------------------
    # CREATE FIRST ATTEMPT
    # --------------------------------------------------------

    attempt = TestAttempt.objects.create(
        test=test,
        student=request.user,
        expires_at=test.available_until,
        proctoring_status=TestAttempt.ACTIVE,
        warning_count=0,
    )

    return render(
        request,
        "education/student/take_test.html",
        {
            "test": test,
            "attempt": attempt,
            "questions": test.questions.all(),
            "server_now": now,
        }
    )


# ============================================================
# STUDENT - PROCTORING / ANTI-CHEATING EVENTS
# ============================================================

@student_required
def test_anti_cheat_event(request, test_id):
    """
    Receive proctoring events from the student's exam page.

    Browser-level events such as tab/focus/fullscreen/copy/paste
    are recorded here. AI/OpenCV events can use the same endpoint.

    Important:
    - ML detection does NOT automatically terminate the test.
    - AI warnings are counted server-side.
    - The third AI warning terminates the attempt.
    - Keyboard/copy/paste/tab events are recorded, not used as
      automatic termination triggers at this stage.
    """

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    test = get_object_or_404(Test, id=test_id)

    attempt = TestAttempt.objects.filter(
        test=test,
        student=request.user,
        is_submitted=False
    ).first()

    if not attempt:
        return JsonResponse(
            {
                "success": False,
                "message": "Active test attempt not found."
            },
            status=404
        )

    event = request.POST.get("event", "").strip()

    if not event:
        return JsonResponse(
            {
                "success": False,
                "message": "Event is required."
            },
            status=400
        )

    # --------------------------------------------------------
    # Browser event → TestAttempt counter
    # --------------------------------------------------------

    field_map = {
        "tab_switch": "tab_switch_count",
        "copy": "copy_count",
        "paste": "paste_count",
        "fullscreen_exit": "fullscreen_exit_count",
        "focus_loss": "focus_loss_count",
        "keyboard_violation": "keyboard_violation_count",
    }

    field_name = field_map.get(event)

    if field_name:
        current_value = getattr(attempt, field_name)

        setattr(
            attempt,
            field_name,
            current_value + 1
        )

        attempt.last_proctoring_update = timezone.now()

        attempt.save(
            update_fields=[
                field_name,
                "last_proctoring_update"
            ]
        )

    else:
        attempt.last_proctoring_update = timezone.now()

        attempt.save(
            update_fields=[
                "last_proctoring_update"
            ]
        )

    # --------------------------------------------------------
    # Map event name to database event type
    # --------------------------------------------------------

    event_type_map = {
        "camera_started":
            ProctoringEvent.CAMERA_STARTED,

        "camera_stopped":
            ProctoringEvent.CAMERA_STOPPED,

        "phone_detected":
            ProctoringEvent.PHONE_DETECTED,

        "cell_phone_detected":
            ProctoringEvent.PHONE_DETECTED,

        "laptop_detected":
            ProctoringEvent.LAPTOP_DETECTED,

        "book_detected":
            ProctoringEvent.BOOK_DETECTED,

        "multiple_persons":
            ProctoringEvent.MULTIPLE_PERSONS,

        "copy":
            ProctoringEvent.COPY_ATTEMPT,

        "paste":
            ProctoringEvent.PASTE_ATTEMPT,

        "cut":
            ProctoringEvent.CUT_ATTEMPT,

        "tab_switch":
            ProctoringEvent.TAB_SWITCH,

        "focus_loss":
            ProctoringEvent.FOCUS_LOSS,

        "fullscreen_exit":
            ProctoringEvent.FULLSCREEN_EXIT,

        "keyboard_violation":
            ProctoringEvent.KEYBOARD_VIOLATION,

        "test_terminated":
            ProctoringEvent.TEST_TERMINATED,
    }

    event_type = event_type_map.get(event)

    # --------------------------------------------------------
    # AI warning event
    # --------------------------------------------------------

    ai_warning_events = {
        "phone_detected",
        "cell_phone_detected",
        "laptop_detected",
        "book_detected",
        "multiple_persons",
    }

    warning_created = False
    terminated = False

    if event in ai_warning_events:

        attempt.warning_count += 1

        warning_number = attempt.warning_count

        attempt.last_proctoring_update = timezone.now()

        # Third AI warning terminates the attempt.
        if warning_number >= 3:

            attempt.proctoring_status = (
                TestAttempt.TERMINATED
            )

            attempt.termination_reason = (
                "Third AI proctoring warning: "
                + event.replace("_", " ")
            )

            attempt.is_submitted = True
            attempt.submitted_at = timezone.now()

            terminated = True

        attempt.save(
            update_fields=[
                "warning_count",
                "proctoring_status",
                "termination_reason",
                "is_submitted",
                "submitted_at",
                "last_proctoring_update",
            ]
        )

        warning_created = True

        # Save the actual AI detection event.
        ProctoringEvent.objects.create(
            attempt=attempt,
            student=request.user,
            event_type=(
                event_type
                or ProctoringEvent.WARNING
            ),
            message=(
                f"AI warning {warning_number} of 3: "
                f"{event.replace('_', ' ')}"
            ),
            confidence=None,
            metadata={}
        )

        # Save a separate termination event on warning 3.
        if terminated:

            ProctoringEvent.objects.create(
                attempt=attempt,
                student=request.user,
                event_type=ProctoringEvent.TEST_TERMINATED,
                message=(
                    "Test terminated after "
                    "3 AI proctoring warnings."
                ),
                metadata={
                    "warning_count": warning_number
                }
            )

        return JsonResponse(
            {
                "success": True,
                "warning": True,
                "warning_count": warning_number,
                "max_warnings": 3,
                "terminated": terminated,
            }
        )

    # --------------------------------------------------------
    # Normal event
    # --------------------------------------------------------

    if event_type:

        ProctoringEvent.objects.create(
            attempt=attempt,
            student=request.user,
            event_type=event_type,
            message=(
                event.replace("_", " ").capitalize()
            ),
            metadata={}
        )

    return JsonResponse(
        {
            "success": True,
            "warning": warning_created,
            "warning_count": attempt.warning_count,
            "max_warnings": 3,
            "terminated": False,
        }
    )


# ============================================================
# STUDENT - PROCTORING STATUS
# ============================================================

@student_required
def test_proctoring_status(request, test_id):
    """
    Return the current server-side proctoring state.

    The exam page can poll this endpoint to make sure that a
    teacher/system termination is reflected in the browser.
    """

    test = get_object_or_404(Test, id=test_id)

    attempt = TestAttempt.objects.filter(
        test=test,
        student=request.user
    ).first()

    if not attempt:
        return JsonResponse(
            {
                "success": False,
                "message": "Attempt not found."
            },
            status=404
        )

    return JsonResponse(
        {
            "success": True,
            "status": attempt.proctoring_status,
            "warning_count": attempt.warning_count,
            "terminated": (
                attempt.proctoring_status
                == TestAttempt.TERMINATED
            ),
            "termination_reason":
                attempt.termination_reason,
        }
    )


# ============================================================
# WEBRTC - LIVE CAMERA SIGNALING
# ============================================================
#
# Django is used only to exchange the WebRTC offer/answer.
# The actual video stream remains peer-to-peer and is not stored
# in SQLite. Django cache is used for short-lived signaling data.
#


def _webrtc_offer_key(attempt_id):
    return f"udaan:webrtc:offer:{attempt_id}"


def _webrtc_answer_key(attempt_id):
    return f"udaan:webrtc:answer:{attempt_id}"


# ============================================================
# STUDENT - SEND WEBRTC OFFER
# ============================================================

@student_required
def student_webrtc_offer(request, attempt_id):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        student=request.user,
        is_submitted=False,
    )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON."
            },
            status=400
        )

    sdp = data.get("sdp")
    offer_type = data.get("type")

    # First request initializes a fresh signaling exchange.
    if not sdp or not offer_type:
        cache.delete(
            _webrtc_offer_key(attempt.id)
        )
        cache.delete(
            _webrtc_answer_key(attempt.id)
        )

        return JsonResponse(
            {
                "success": True,
                "initialized": True
            }
        )

    cache.set(
        _webrtc_offer_key(attempt.id),
        {
            "type": offer_type,
            "sdp": sdp,
        },
        timeout=120,
    )

    cache.delete(
        _webrtc_answer_key(attempt.id)
    )

    return JsonResponse(
        {
            "success": True,
            "stored": True
        }
    )


# ============================================================
# STUDENT - GET TEACHER ANSWER
# ============================================================

@student_required
def student_webrtc_answer(request, attempt_id):
    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "GET request required."
            },
            status=405
        )

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        student=request.user,
        is_submitted=False,
    )

    answer = cache.get(
        _webrtc_answer_key(attempt.id)
    )

    if not answer:
        return JsonResponse(
            {
                "success": False,
                "message": "Teacher answer not ready."
            },
            status=404
        )

    return JsonResponse(
        {
            "success": True,
            "type": answer["type"],
            "sdp": answer["sdp"],
        }
    )


# ============================================================
# TEACHER - GET STUDENT OFFER
# ============================================================

@teacher_required
def teacher_webrtc_offer(request, attempt_id):
    if request.method != "GET":
        return JsonResponse(
            {
                "success": False,
                "message": "GET request required."
            },
            status=405
        )

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        test__created_by=request.user,
        is_submitted=False,
    )

    offer = cache.get(
        _webrtc_offer_key(attempt.id)
    )

    if not offer:
        return JsonResponse(
            {
                "success": False,
                "message": "Student camera offer not ready."
            },
            status=404
        )

    return JsonResponse(
        {
            "success": True,
            "type": offer["type"],
            "sdp": offer["sdp"],
        }
    )


# ============================================================
# TEACHER - SEND WEBRTC ANSWER
# ============================================================

@teacher_required
def teacher_webrtc_answer(request, attempt_id):
    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        test__created_by=request.user,
        is_submitted=False,
    )

    try:
        data = json.loads(
            request.body.decode("utf-8")
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {
                "success": False,
                "message": "Invalid JSON."
            },
            status=400
        )

    sdp = data.get("sdp")
    answer_type = data.get("type")

    if not sdp or not answer_type:
        return JsonResponse(
            {
                "success": False,
                "message": "SDP answer is required."
            },
            status=400
        )

    cache.set(
        _webrtc_answer_key(attempt.id),
        {
            "type": answer_type,
            "sdp": sdp,
        },
        timeout=120,
    )

    return JsonResponse(
        {
            "success": True,
            "stored": True
        }
    )




# ============================================================
# STUDENT - LIVE MONITORING HEARTBEAT
# ============================================================

@student_required
def student_monitor_heartbeat(request, attempt_id):
    """Refresh the student's active-exam presence timestamp."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "POST request required."}, status=405)

    attempt = get_object_or_404(
        TestAttempt,
        id=attempt_id,
        student=request.user,
        is_submitted=False,
    )

    now = timezone.now()
    attempt.last_proctoring_update = now
    attempt.save(update_fields=["last_proctoring_update"])

    return JsonResponse({
        "success": True,
        "online": True,
        "server_time": now.isoformat(),
    })


# ============================================================
# TEACHER - REAL-TIME MONITORING DATA
# ============================================================

@teacher_required
def teacher_live_monitor_data(request):
    """Return fresh status/events for the teacher's active attempts."""
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "GET request required."}, status=405)

    now = timezone.now()
    attempts = (
        TestAttempt.objects
        .filter(test__created_by=request.user, is_submitted=False)
        .select_related("student", "test")
        .prefetch_related("proctoring_events")
        .order_by("-started_at")
    )

    data = []
    for attempt in attempts:
        events = list(attempt.proctoring_events.all()[:10])
        online = bool(
            attempt.last_proctoring_update and
            (now - attempt.last_proctoring_update).total_seconds() <= 6
        )

        camera_status = "unknown"
        for event in events:
            if event.event_type == ProctoringEvent.CAMERA_STARTED:
                camera_status = "on"
                break
            if event.event_type == ProctoringEvent.CAMERA_STOPPED:
                camera_status = "off"
                break

        data.append({
            "attempt_id": attempt.id,
            "student_name": attempt.student.get_full_name() or attempt.student.username,
            "username": attempt.student.username,
            "test_name": attempt.test.title,
            "online": online,
            "camera_status": camera_status,
            "exam_status": "in_progress",
            "proctoring_status": attempt.proctoring_status,
            "warning_count": attempt.warning_count,
            "tab_switch_count": attempt.tab_switch_count,
            "focus_loss_count": attempt.focus_loss_count,
            "fullscreen_exit_count": attempt.fullscreen_exit_count,
            "copy_count": attempt.copy_count,
            "paste_count": attempt.paste_count,
            "cut_count": attempt.cut_count,
            "keyboard_violation_count": attempt.keyboard_violation_count,
            "last_proctoring_update": attempt.last_proctoring_update.isoformat() if attempt.last_proctoring_update else None,
            "events": [
                {
                    "type": e.event_type,
                    "message": e.message or e.event_type,
                    "created_at": e.created_at.isoformat() if getattr(e, "created_at", None) else "",
                }
                for e in events
            ],
        })

    return JsonResponse({"success": True, "server_time": now.isoformat(), "attempts": data})


# ============================================================
# TEACHER - LIVE PROCTORING MONITOR
# ============================================================

@teacher_required
def teacher_live_monitor(request):
    """
    Teacher live-proctoring dashboard data.

    The actual camera transport will be implemented separately.
    This view provides the current active attempts and their
    server-side proctoring status/events.
    """

    active_attempts = (
        TestAttempt.objects
        .filter(
            test__created_by=request.user,
            is_submitted=False
        )
        .select_related(
            "student",
            "test",
            "test__chapter",
            "test__chapter__subject",
        )
        .prefetch_related(
            "proctoring_events"
        )
        .order_by("-started_at")
    )

    attempt_data = []

    for attempt in active_attempts:

        latest_events = list(
            attempt.proctoring_events.all()[:10]
        )

        attempt_data.append(
            {
                "attempt": attempt,
                "student": attempt.student,
                "test": attempt.test,
                "warning_count": attempt.warning_count,
                "status": attempt.proctoring_status,
                "last_proctoring_update":
                    attempt.last_proctoring_update,
                "events": latest_events,
            }
        )

    return render(
        request,
        "education/teacher/live_monitor.html",
        {
            "attempts": attempt_data,
        }
    )


# ============================================================
# TEACHER - TERMINATE STUDENT TEST
# ============================================================

@teacher_required
def teacher_terminate_test(request, attempt_id):
    """
    Allow the teacher to manually terminate an active test.
    """

    if request.method != "POST":
        return JsonResponse(
            {
                "success": False,
                "message": "POST request required."
            },
            status=405
        )

    attempt = get_object_or_404(
        TestAttempt.objects.select_related(
            "test",
            "student"
        ),
        id=attempt_id,
        test__created_by=request.user
    )

    if attempt.is_submitted:

        return JsonResponse(
            {
                "success": False,
                "message": "This attempt is already closed."
            },
            status=400
        )

    reason = request.POST.get(
        "reason",
        "Terminated by teacher."
    ).strip()

    now = timezone.now()

    attempt.proctoring_status = (
        TestAttempt.TERMINATED
    )

    attempt.termination_reason = reason

    attempt.is_submitted = True

    attempt.submitted_at = now

    attempt.save(
        update_fields=[
            "proctoring_status",
            "termination_reason",
            "is_submitted",
            "submitted_at",
        ]
    )

    ProctoringEvent.objects.create(
        attempt=attempt,
        student=attempt.student,
        event_type=ProctoringEvent.TEST_TERMINATED,
        message=reason,
        metadata={
            "terminated_by": "teacher",
            "teacher_id": request.user.id,
        }
    )

    return JsonResponse(
        {
            "success": True,
            "message": "Test terminated successfully."
        }
    )


# ============================================================
# STUDENT - CLASS LIST
# ============================================================

@student_required
def student_classes(request):
    """
    Display all available classes.
    """

    classes = Class.objects.all()

    return render(
        request,
        "education/student/classes.html",
        {
            "classes": classes,
        }
    )


# ============================================================
# STUDENT - SUBJECT LIST
# ============================================================

@student_required
def student_subjects(request, class_id):
    """
    Display subjects belonging to a selected class.
    """

    selected_class = get_object_or_404(
        Class,
        id=class_id
    )

    subjects = Subject.objects.filter(
        class_level=selected_class
    )

    return render(
        request,
        "education/student/subjects.html",
        {
            "selected_class": selected_class,
            "subjects": subjects,
        }
    )


# ============================================================
# STUDENT - CHAPTER LIST
# ============================================================

@student_required
def student_chapters(request, subject_id):
    """
    Display chapters belonging to a selected subject.
    """

    selected_subject = get_object_or_404(
        Subject,
        id=subject_id
    )

    chapters = Chapter.objects.filter(
        subject=selected_subject
    )

    return render(
        request,
        "education/student/chapters.html",
        {
            "selected_subject": selected_subject,
            "chapters": chapters,
        }
    )


# ============================================================
# STUDENT - CHAPTER PAGE
# ============================================================

@student_required
def chapter_detail(request, chapter_id):
    """
    Display the selected chapter.

    Only one lesson per lesson_number is shown to students.
    If old duplicate records already exist, the newest record is used.
    """

    chapter = get_object_or_404(
        Chapter,
        id=chapter_id
    )

    all_lessons = Lesson.objects.filter(
        chapter=chapter
    ).order_by(
        "lesson_number",
        "-id"
    )

    # Keep only one lesson for each lesson number.
    # This also hides old duplicate records that may already exist.
    unique_lessons = []
    seen_lesson_numbers = set()

    for lesson in all_lessons:
        if lesson.lesson_number in seen_lesson_numbers:
            continue

        seen_lesson_numbers.add(
            lesson.lesson_number
        )

        unique_lessons.append(
            lesson
        )

    unique_lessons.sort(
        key=lambda lesson: (
            lesson.lesson_number,
            lesson.id
        )
    )

    return render(
        request,
        "education/student/chapter.html",
        {
            "chapter": chapter,
            "lessons": unique_lessons,
        }
    )


# ============================================================
# ADMIN / STAFF - DELETE LESSON FROM CHAPTER PAGE
# ============================================================

@student_required
def admin_delete_lesson(request, lesson_id):
    """
    Delete a lesson directly from the student chapter page.
    """

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    chapter_id = lesson.chapter_id

    if request.method != "POST":
        return redirect(
            "education:chapter_detail",
            chapter_id=chapter_id
        )

    try:
        if lesson.video:
            lesson.video.delete(
                save=False
            )
    except Exception:
        pass

    lesson.delete()

    messages.success(
        request,
        "Lesson deleted successfully."
    )

    return redirect(
        "education:chapter_detail",
        chapter_id=chapter_id
    )


# ============================================================
# STUDENT - LEARN
# ============================================================

@student_required
def learn(request, chapter_id):
    """
    Learning page for a chapter.

    Only teacher-uploaded lessons are shown here.
    YouTube and Wikimedia integrations have been removed.
    """

    chapter = get_object_or_404(
        Chapter,
        id=chapter_id
    )

    lessons = Lesson.objects.filter(
        chapter=chapter
    ).order_by(
        "lesson_number",
        "id"
    )

    return render(
        request,
        "education/student/learn.html",
        {
            "chapter": chapter,
            "lessons": lessons,
        }
    )


# ============================================================
# STUDENT - LESSON PAGE
# ============================================================

@student_required
def lesson_detail(request, lesson_id):
    """
    Display one teacher-uploaded lesson and its video.
    """

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    return render(
        request,
        "education/student/lesson.html",
        {
            "lesson": lesson,
        }
    )


# ============================================================
# TEACHER DASHBOARD
# ============================================================

@teacher_required
def teacher_dashboard(request):
    """
    Teacher Education dashboard.
    """

    return render(
        request,
        "education/teacher/dashboard.html"
    )


# ============================================================
# TEACHER - CREATE LESSON
# ============================================================

@teacher_required
def teacher_create_lesson(request):

    if request.method == "POST":

        chapter_id = request.POST.get("chapter")
        title = request.POST.get("title")
        lesson_number = request.POST.get("lesson_number")
        description = request.POST.get(
            "description",
            ""
        ).strip()

        video = request.FILES.get("video")

        if not chapter_id:
            messages.error(
                request,
                "Please select a chapter."
            )
            return redirect(
                "education:teacher_create_lesson"
            )

        if not title:
            messages.error(
                request,
                "Please enter the lesson title."
            )
            return redirect(
                "education:teacher_create_lesson"
            )

        if not lesson_number:
            messages.error(
                request,
                "Please enter the lesson number."
            )
            return redirect(
                "education:teacher_create_lesson"
            )

        if not video:
            messages.error(
                request,
                "Please select a video."
            )
            return redirect(
                "education:teacher_create_lesson"
            )

        chapter = get_object_or_404(
            Chapter,
            id=chapter_id
        )

        compressed_path = None

        try:
            compression = compress_uploaded_video(
                video
            )

            compressed_path = compression[
                "output_path"
            ]

            original_size = compression[
                "original_size"
            ]

            compressed_size = compression[
                "compressed_size"
            ]

            original_mb = (
                original_size
                / 1024
                / 1024
            )

            compressed_mb = (
                compressed_size
                / 1024
                / 1024
            )

            # Prevent duplicate lessons:
            # same chapter + lesson number updates
            # the existing lesson.
            existing_lessons = (
                Lesson.objects.filter(
                    chapter=chapter,
                    lesson_number=lesson_number
                )
                .order_by("-id")
            )

            existing_lesson = (
                existing_lessons.first()
            )

            # Delete older duplicate rows.
            if existing_lesson:

                duplicate_lessons = (
                    existing_lessons.exclude(
                        id=existing_lesson.id
                    )
                )

                for duplicate in duplicate_lessons:

                    try:
                        if duplicate.video:
                            duplicate.video.delete(
                                save=False
                            )
                    except Exception:
                        pass

                    duplicate.delete()

            # ------------------------------------------------
            # If compression made the file larger,
            # keep the original uploaded video instead.
            # ------------------------------------------------

            if compression["use_original"]:

                # Rewind uploaded file before Django saves it.
                try:
                    video.seek(0)
                except Exception:
                    pass

                if existing_lesson:

                    old_video_name = (
                        existing_lesson.video.name
                        if existing_lesson.video
                        else None
                    )

                    existing_lesson.title = title
                    existing_lesson.description = (
                        description
                    )
                    existing_lesson.video = video
                    existing_lesson.save()

                    # Delete old file only AFTER the new file
                    # has successfully been saved.
                    if old_video_name:
                        try:
                            existing_lesson.video.storage.delete(
                                old_video_name
                            )
                        except Exception:
                            pass

                else:

                    Lesson.objects.create(
                        chapter=chapter,
                        title=title,
                        lesson_number=lesson_number,
                        description=description,
                        video=video
                    )

                messages.success(
                    request,
                    (
                        "Lesson uploaded successfully. "
                        "The original video was already "
                        "smaller than the compressed copy, "
                        "so it was kept."
                    )
                )

            else:

                compressed_name = compression[
                    "output_name"
                ]

                with open(
                    compressed_path,
                    "rb"
                ) as compressed_file:

                    django_file = File(
                        compressed_file,
                        name=compressed_name
                    )

                    if existing_lesson:

                        old_video_name = (
                            existing_lesson.video.name
                            if existing_lesson.video
                            else None
                        )

                        existing_lesson.title = title
                        existing_lesson.description = (
                            description
                        )

                        existing_lesson.video.save(
                            compressed_name,
                            django_file,
                            save=False
                        )

                        existing_lesson.save()

                        # Delete old video only after
                        # compressed replacement is saved.
                        if old_video_name:
                            try:
                                existing_lesson.video.storage.delete(
                                    old_video_name
                                )
                            except Exception:
                                pass

                    else:

                        lesson = Lesson(
                            chapter=chapter,
                            title=title,
                            lesson_number=lesson_number,
                            description=description
                        )

                        lesson.video.save(
                            compressed_name,
                            django_file,
                            save=False
                        )

                        lesson.save()

                saved_mb = (
                    original_mb
                    - compressed_mb
                )

                messages.success(
                    request,
                    (
                        "Lesson uploaded and compressed: "
                        f"{original_mb:.1f} MB → "
                        f"{compressed_mb:.1f} MB "
                        f"(saved {saved_mb:.1f} MB)."
                    )
                )

        except VideoCompressionError as error:

            messages.error(
                request,
                str(error)
            )

            return redirect(
                "education:teacher_create_lesson"
            )

        except Exception as error:

            messages.error(
                request,
                (
                    "Video upload/compression failed: "
                    f"{error}"
                )
            )

            return redirect(
                "education:teacher_create_lesson"
            )

        finally:

            if compressed_path:
                cleanup_temp_video(
                    compressed_path
                )

        return redirect(
            "education:teacher_dashboard"
        )

    chapters = Chapter.objects.all().order_by(
        "subject",
        "chapter_number"
    )

    return render(
        request,
        "education/teacher/create_lesson.html",
        {
            "chapters": chapters
        }
    )


# ============================================================
# TEACHER - DELETE LESSON
# ============================================================

@teacher_required
def teacher_delete_lesson(request, lesson_id):
    """
    Permanently delete a lesson and its uploaded video.
    Only teachers can perform this action.
    """

    lesson = get_object_or_404(
        Lesson,
        id=lesson_id
    )

    chapter_id = lesson.chapter_id

    if request.method != "POST":
        return redirect(
            "education:teacher_dashboard"
        )

    try:
        if lesson.video:
            lesson.video.delete(
                save=False
            )
    except Exception:
        pass

    lesson.delete()

    messages.success(
        request,
        "Lesson deleted successfully."
    )

    return redirect(
        "education:teacher_dashboard"
    )


# ============================================================
# TEACHER - CREATE TEST
# ============================================================

# ============================================================
# GEMINI - AI TEST GENERATION
# ============================================================

def generate_ai_test_questions(
    chapter,
    mcq_count,
    descriptive_count
):
    """
    Generate MCQ + descriptive questions for a chapter
    using Gemini's current Interactions API.

    Gemini's Interactions API is the current recommended
    interface for new Gemini integrations.
    """

    api_key = config(
        "GEMINI_API_KEY",
        default=""
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    # Gemini 3.6 Flash is a current stable model.
    model_name = config(
        "GEMINI_MODEL",
        default="gemini-3.6-flash"
    )

    api_url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/interactions"
    )

    chapter_description = (
        chapter.description.strip()
        if chapter.description
        else "No chapter description is available."
    )

    total_questions = (
        mcq_count + descriptive_count
    )

    prompt = f"""
You are an educational test generator for a rural-learning
platform called Udaan.

Create a school-level assessment using ONLY the information
and topic represented by the chapter below.

Class: {chapter.subject.class_level.name}
Subject: {chapter.subject.name}
Chapter: {chapter.name}
Chapter description: {chapter_description}

Generate EXACTLY:
- {mcq_count} multiple-choice questions
- {descriptive_count} descriptive questions

Rules:
1. Questions must be appropriate for the selected class level.
2. Keep the language simple and student-friendly.
3. Keep every question relevant to the selected chapter.
4. Every MCQ must have exactly four options: A, B, C, D.
5. Every MCQ must have exactly one correct option.
6. Descriptive questions should require a short written answer.
7. For each descriptive question, provide a concise model answer
   or key points in correct_answer.
8. Use 1 mark for every MCQ.
9. Use 5 marks for every descriptive question.
10. Do not add explanations outside the JSON structure.

Return exactly {total_questions} questions.
"""

    # Structured output makes the response predictable JSON.
    response_schema = {
        "type": "object",

        "properties": {
            "title": {
                "type": "string"
            },

            "questions": {
                "type": "array",

                "minItems": total_questions,

                "maxItems": total_questions,

                "items": {
                    "type": "object",

                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "mcq",
                                "descriptive"
                            ]
                        },

                        "question": {
                            "type": "string"
                        },

                        "options": {
                            "type": "object",

                            "properties": {
                                "A": {
                                    "type": "string"
                                },
                                "B": {
                                    "type": "string"
                                },
                                "C": {
                                    "type": "string"
                                },
                                "D": {
                                    "type": "string"
                                }
                            },

                            "required": [
                                "A",
                                "B",
                                "C",
                                "D"
                            ]
                        },

                        "correct_answer": {
                            "type": "string"
                        },

                        "marks": {
                            "type": "integer"
                        }
                    },

                    "required": [
                        "type",
                        "question",
                        "options",
                        "correct_answer",
                        "marks"
                    ]
                }
            }
        },

        "required": [
            "title",
            "questions"
        ]
    }

    payload = {
        "model": model_name,

        "input": prompt,

        "response_format": {
            "type": "text",

            "mime_type": "application/json",

            "schema": response_schema
        },

        "generation_config": {
            "max_output_tokens": 5000
        },

        # We do not need server-side conversation history for
        # a one-time test generation request.
        "store": False
    }

    try:

        response = requests.post(
            api_url,

            headers={
                "x-goog-api-key": api_key,

                "Content-Type": "application/json"
            },

            json=payload,

            timeout=90
        )

    except requests.RequestException as exc:

        raise ValueError(
            "Unable to connect to the Gemini API."
        ) from exc

    if not response.ok:

        try:

            error_data = response.json()

            error_message = (
                error_data
                .get("error", {})
                .get("message")
            )

        except ValueError:

            error_message = None

        raise ValueError(
            error_message
            or (
                "Gemini API request failed "
                f"with status {response.status_code}."
            )
        )

    try:

        data = response.json()

    except ValueError as exc:

        raise ValueError(
            "Gemini returned an invalid API response."
        ) from exc

    if data.get("status") == "failed":

        raise ValueError(
            "Gemini interaction failed."
        )

    # REST Interactions responses contain model output
    # inside the steps timeline.
    generated_text = ""

    for step in data.get("steps", []):

        if step.get("type") != "model_output":
            continue

        for content in step.get(
            "content",
            []
        ):

            if content.get("type") == "text":

                generated_text += content.get(
                    "text",
                    ""
                )

    generated_text = generated_text.strip()

    if not generated_text:

        raise ValueError(
            "Gemini did not return a test."
        )

    try:

        result = json.loads(
            generated_text
        )

    except json.JSONDecodeError as exc:

        raise ValueError(
            "Gemini returned invalid JSON."
        ) from exc

    questions = result.get(
        "questions",
        []
    )

    if not isinstance(
        questions,
        list
    ):

        raise ValueError(
            "Gemini returned an invalid question list."
        )

    # Validate the requested counts before saving anything.
    mcqs = [
        q for q in questions
        if q.get("type") == "mcq"
    ]

    descriptive = [
        q for q in questions
        if q.get("type") == "descriptive"
    ]

    if len(mcqs) != mcq_count:

        raise ValueError(
            "Gemini generated "
            f"{len(mcqs)} MCQs instead of "
            f"{mcq_count}."
        )

    if len(descriptive) != descriptive_count:

        raise ValueError(
            "Gemini generated "
            f"{len(descriptive)} descriptive questions "
            "instead of "
            f"{descriptive_count}."
        )

    cleaned_questions = []

    for question in questions:

        question_type = question.get(
            "type"
        )

        question_text = str(
            question.get(
                "question",
                ""
            )
        ).strip()

        if not question_text:

            raise ValueError(
                "Gemini returned a question without text."
            )

        if question_type == "mcq":

            options = question.get(
                "options",
                {}
            )

            if not isinstance(
                options,
                dict
            ):

                raise ValueError(
                    "An MCQ has invalid options."
                )

            normalized_options = {
                letter: str(
                    options.get(
                        letter,
                        ""
                    )
                ).strip()

                for letter in [
                    "A",
                    "B",
                    "C",
                    "D"
                ]
            }

            if any(
                not value
                for value in normalized_options.values()
            ):

                raise ValueError(
                    "An MCQ does not contain all "
                    "four options."
                )

            correct_answer = str(
                question.get(
                    "correct_answer",
                    ""
                )
            ).strip().upper()

            if correct_answer not in [
                "A",
                "B",
                "C",
                "D"
            ]:

                raise ValueError(
                    "An MCQ has an invalid correct answer."
                )

            cleaned_questions.append(
                {
                    "type": "mcq",

                    "question": question_text,

                    "options": normalized_options,

                    "correct_answer": correct_answer,

                    "marks": 1,
                }
            )

        elif question_type == "descriptive":

            model_answer = str(
                question.get(
                    "correct_answer",
                    ""
                )
            ).strip()

            if not model_answer:

                raise ValueError(
                    "A descriptive question is missing "
                    "its model answer."
                )

            cleaned_questions.append(
                {
                    "type": "descriptive",

                    "question": question_text,

                    "options": {},

                    "correct_answer": model_answer,

                    "marks": 5,
                }
            )

        else:

            raise ValueError(
                "Gemini returned an unknown question type."
            )

    title = str(
        result.get(
            "title",
            ""
        )
    ).strip()

    if not title:

        title = (
            f"{chapter.name} - AI Generated Test"
        )

    return {
        "title": title,

        "questions": cleaned_questions,
    }


# ============================================================
# TEACHER - CREATE TEST
# ============================================================

@teacher_required
def teacher_create_test(request):
    """
    Create and schedule an AI-generated test.

    Flow:
        Class -> Subject -> Chapter -> AI generation -> Schedule

    The selected Subject must belong to the selected Class,
    and the selected Chapter must belong to the selected Subject.
    """

    # ========================================================
    # ACADEMIC DATA
    # ========================================================

    classes = Class.objects.all().order_by(
        "order",
        "id"
    )

    subjects = Subject.objects.select_related(
        "class_level"
    ).all().order_by(
        "class_level__order",
        "class_level__id",
        "name"
    )

    chapters = Chapter.objects.select_related(
        "subject",
        "subject__class_level"
    ).all().order_by(
        "subject__class_level__order",
        "subject__class_level__id",
        "subject__name",
        "chapter_number"
    )

    generated_test = None
    generated_questions = []
    generation_error = None

    form_values = {
        "class_id": "",
        "subject_id": "",
        "chapter_id": "",
        "title": "",
        "mcq_count": "5",
        "descriptive_count": "2",
        "test_datetime": "",
        "duration": "30",
    }

    if request.method == "POST":

        class_id = request.POST.get(
            "class",
            ""
        ).strip()

        subject_id = request.POST.get(
            "subject",
            ""
        ).strip()

        chapter_id = request.POST.get(
            "chapter",
            ""
        ).strip()

        title = request.POST.get(
            "title",
            ""
        ).strip()

        mcq_count_raw = request.POST.get(
            "mcq_count",
            "5"
        )

        descriptive_count_raw = request.POST.get(
            "descriptive_count",
            "2"
        )

        test_datetime_raw = request.POST.get(
            "test_datetime",
            ""
        )

        duration_raw = request.POST.get(
            "duration",
            "30"
        )

        form_values = {
            "class_id": class_id,
            "subject_id": subject_id,
            "chapter_id": chapter_id,
            "title": title,
            "mcq_count": mcq_count_raw,
            "descriptive_count": descriptive_count_raw,
            "test_datetime": test_datetime_raw,
            "duration": duration_raw,
        }

        try:

            # ====================================================
            # VALIDATE CLASS
            # ====================================================

            if not class_id:
                raise ValueError(
                    "Please select a class."
                )

            selected_class = Class.objects.filter(
                id=class_id
            ).first()

            if not selected_class:
                raise ValueError(
                    "Selected class was not found."
                )

            # ====================================================
            # VALIDATE SUBJECT
            # ====================================================

            if not subject_id:
                raise ValueError(
                    "Please select a subject."
                )

            subject = Subject.objects.filter(
                id=subject_id,
                class_level=selected_class
            ).first()

            if not subject:
                raise ValueError(
                    "The selected subject does not belong "
                    "to the selected class."
                )

            # ====================================================
            # VALIDATE CHAPTER
            # ====================================================

            if not chapter_id:
                raise ValueError(
                    "Please select a chapter."
                )

            chapter = Chapter.objects.filter(
                id=chapter_id,
                subject=subject
            ).select_related(
                "subject",
                "subject__class_level"
            ).first()

            if not chapter:
                raise ValueError(
                    "The selected chapter does not belong "
                    "to the selected subject."
                )

            # ====================================================
            # QUESTION COUNTS
            # ====================================================

            try:
                mcq_count = int(
                    mcq_count_raw
                )
            except (TypeError, ValueError):
                raise ValueError(
                    "MCQ count must be a valid number."
                )

            try:
                descriptive_count = int(
                    descriptive_count_raw
                )
            except (TypeError, ValueError):
                raise ValueError(
                    "Descriptive question count must "
                    "be a valid number."
                )

            if mcq_count < 0 or mcq_count > 20:
                raise ValueError(
                    "MCQ count must be between 0 and 20."
                )

            if (
                descriptive_count < 0
                or descriptive_count > 10
            ):
                raise ValueError(
                    "Descriptive question count must "
                    "be between 0 and 10."
                )

            if (
                mcq_count
                + descriptive_count
                == 0
            ):
                raise ValueError(
                    "Please request at least one question."
                )

            if (
                mcq_count
                + descriptive_count
                > 20
            ):
                raise ValueError(
                    "A test can contain at most 20 questions."
                )

            # ====================================================
            # DATE + TIME
            # ====================================================

            if not test_datetime_raw:
                raise ValueError(
                    "Please select the test date and time."
                )

            try:

                test_datetime = datetime.fromisoformat(
                    test_datetime_raw
                )

            except ValueError as exc:

                raise ValueError(
                    "Please provide a valid test date and time."
                ) from exc

            if timezone.is_naive(
                test_datetime
            ):

                test_datetime = timezone.make_aware(
                    test_datetime
                )

            if test_datetime <= timezone.now():

                raise ValueError(
                    "Test date and time must be in the future."
                )

            # ====================================================
            # DURATION
            # ====================================================

            if not duration_raw:

                raise ValueError(
                    "Please enter the test duration."
                )

            try:

                duration = int(
                    duration_raw
                )

            except ValueError as exc:

                raise ValueError(
                    "Test duration must be a valid number."
                ) from exc

            if duration < 1:

                raise ValueError(
                    "Test duration must be at least 1 minute."
                )

            if duration > 300:

                raise ValueError(
                    "Test duration cannot be more than "
                    "300 minutes."
                )

            available_from = test_datetime

            available_until = (
                available_from
                + timedelta(
                    minutes=duration
                )
            )

            # ====================================================
            # AI GENERATION
            # ====================================================

            generated = generate_ai_test_questions(
                chapter,
                mcq_count,
                descriptive_count
            )

            generated_title = (
                title
                or generated["title"]
            )

            total_marks = sum(
                question["marks"]
                for question in generated["questions"]
            )

            # ====================================================
            # CREATE TEST
            # ====================================================

            test = Test.objects.create(
                title=generated_title,
                chapter=chapter,
                created_by=request.user,
                total_marks=total_marks,
                available_from=available_from,
                available_until=available_until
            )

            # ====================================================
            # CREATE QUESTIONS
            # ====================================================

            for index, question_data in enumerate(
                generated["questions"],
                start=1
            ):

                Question.objects.create(
                    test=test,
                    question_type=question_data["type"],
                    question_text=question_data["question"],
                    options=question_data["options"],
                    correct_answer=question_data[
                        "correct_answer"
                    ],
                    marks=question_data["marks"],
                    order=index
                )

            generated_test = test

            generated_questions = list(
                test.questions.all()
            )

            messages.success(
                request,
                "AI test generated and scheduled successfully!"
            )

        except ValueError as exc:

            generation_error = str(
                exc
            )

        except requests.RequestException:

            generation_error = (
                "Unable to connect to Gemini right now. "
                "Please check your internet connection "
                "and try again."
            )

    return render(
        request,
        "education/teacher/create_test.html",
        {
            "classes": classes,
            "subjects": subjects,
            "chapters": chapters,
            "generated_test": generated_test,
            "generated_questions": generated_questions,
            "generation_error": generation_error,
            "form_values": form_values,
        }
    )


# ============================================================
# STUDENT - SUBMIT TEST
# ============================================================

@student_required
def submit_test(request, test_id):

    """
    Submit a student's test.

    Handles:
        - Manual submission
        - Automatic submission when timer expires
        - Saving MCQ answers
        - Saving descriptive answers
        - Automatic MCQ marking
        - Creating TestResult
        - Marking TestAttempt as submitted
    """

    if request.method != "POST":

        return redirect(
            "education:student_tests"
        )


    test = get_object_or_404(
        Test,
        id=test_id
    )


    # --------------------------------------------------------
    # FIND ACTIVE ATTEMPT
    # --------------------------------------------------------

    attempt = TestAttempt.objects.filter(
        test=test,
        student=request.user
    ).first()


    if not attempt:

        messages.error(
            request,
            "No test attempt was found."
        )

        return redirect(
            "education:student_tests"
        )


    # --------------------------------------------------------
    # ALREADY SUBMITTED
    # --------------------------------------------------------

    if attempt.is_submitted:

        messages.info(
            request,
            "This test has already been submitted."
        )

        return redirect(
            "education:student_tests"
        )


    # --------------------------------------------------------
    # CHECK TIME
    # --------------------------------------------------------

    now = timezone.now()

    # Submission can happen before or exactly at expiry.
    # If the request arrives after expiry, it is still accepted
    # as an automatic submission.
    expired = now >= attempt.expires_at


    # --------------------------------------------------------
    # GET QUESTIONS
    # --------------------------------------------------------

    questions = list(
        test.questions.all().order_by(
            "order"
        )
    )


    # --------------------------------------------------------
    # CALCULATE SCORE
    # --------------------------------------------------------

    score = 0


    # --------------------------------------------------------
    # CREATE TEST RESULT
    # --------------------------------------------------------

    result = TestResult.objects.create(

        test=test,

        student=request.user,

        score=0,

        total_marks=test.total_marks

    )


    # --------------------------------------------------------
    # SAVE EACH ANSWER
    # --------------------------------------------------------

    for question in questions:


        field_name = (
            f"question_{question.id}"
        )


        answer = request.POST.get(
            field_name,
            ""
        ).strip()


        marks_awarded = 0


        # ====================================================
        # MCQ
        # ====================================================

        if question.question_type == "mcq":


            # Automatically mark MCQ.

            if answer:

                correct_answer = (
                    question.correct_answer or ""
                ).strip()


                if (
                    answer.strip().lower()
                    ==
                    correct_answer.strip().lower()
                ):

                    marks_awarded = question.marks

                    score += question.marks


        # ====================================================
        # DESCRIPTIVE
        # ====================================================

        else:

            # Descriptive answers are saved now.
            #
            # They will be evaluated later by:
            # - teacher
            # OR
            # - AI evaluation system
            #
            # Therefore marks_awarded remains 0.

            marks_awarded = 0


        # ----------------------------------------------------
        # SAVE STUDENT ANSWER
        # ----------------------------------------------------

        StudentAnswer.objects.create(

            result=result,

            question=question,

            answer_text=answer,

            marks_awarded=marks_awarded

        )


    # --------------------------------------------------------
    # UPDATE RESULT SCORE
    # --------------------------------------------------------

    result.score = score

    result.save(
        update_fields=["score"]
    )


    # --------------------------------------------------------
    # MARK ATTEMPT AS SUBMITTED
    # --------------------------------------------------------

    attempt.is_submitted = True

    attempt.proctoring_status = (
        TestAttempt.SUBMITTED
    )

    attempt.submitted_at = now

    attempt.save(
        update_fields=[
            "is_submitted",
            "proctoring_status",
            "submitted_at"
        ]
    )


    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    if expired:

        messages.success(
            request,
            "Time ended. Your test was automatically submitted."
        )

    else:

        messages.success(
            request,
            "Test submitted successfully!"
        )


    # --------------------------------------------------------
    # SHOW RESULT
    # --------------------------------------------------------

    return redirect(
        "education:test_result",
        result_id=result.id
    )


# ============================================================
# STUDENT - TEST RESULT
# ============================================================

@student_required
def test_result(request, result_id):

    result = get_object_or_404(
        TestResult.objects.select_related(
            "test",
            "test__chapter",
            "test__chapter__subject",
            "student"
        ).prefetch_related(
            "answers__question"
        ),
        id=result_id,
        student=request.user
    )


    return render(

        request,

        "education/student/test_result.html",

        {
            "result": result,
            "answers": result.answers.all(),
        }

    )


# ============================================================
# TEACHER - STUDENT RESULTS
# ============================================================

@teacher_required
def teacher_results(request):
    """
    Show submitted TestResult records for tests created by the
    logged-in teacher. Results are read-only on this page.

    Supported filters:
    - student name / username search
    - class
    - subject
    - chapter
    - test
    """

    results = (
        TestResult.objects
        .filter(test__created_by=request.user)
        .select_related(
            "student",
            "test",
            "test__chapter",
            "test__chapter__subject",
            "test__chapter__subject__class_level",
        )
        .order_by("-submitted_at", "-id")
    )

    search_query = request.GET.get("q", "").strip()
    class_id = request.GET.get("class", "").strip()
    subject_id = request.GET.get("subject", "").strip()
    chapter_id = request.GET.get("chapter", "").strip()
    test_id = request.GET.get("test", "").strip()

    if search_query:
        results = results.filter(
            Q(student__username__icontains=search_query)
            | Q(student__first_name__icontains=search_query)
            | Q(student__last_name__icontains=search_query)
            | Q(test__title__icontains=search_query)
            | Q(test__chapter__name__icontains=search_query)
            | Q(test__chapter__subject__name__icontains=search_query)
            | Q(test__chapter__subject__class_level__name__icontains=search_query)
        )

    if class_id:
        results = results.filter(
            test__chapter__subject__class_level_id=class_id
        )

    if subject_id:
        results = results.filter(
            test__chapter__subject_id=subject_id
        )

    if chapter_id:
        results = results.filter(
            test__chapter_id=chapter_id
        )

    if test_id:
        results = results.filter(test_id=test_id)

    result_rows = []
    percentages = []

    for result in results:
        total_marks = float(result.total_marks or 0)
        score = float(result.score or 0)
        percentage = round((score / total_marks) * 100, 1) if total_marks else 0.0
        percentages.append(percentage)

        if percentage >= 80:
            performance = "Excellent"
        elif percentage >= 60:
            performance = "Good"
        elif percentage >= 40:
            performance = "Average"
        else:
            performance = "Needs Improvement"

        result_rows.append({
            "result": result,
            "percentage": percentage,
            "performance": performance,
        })

    classes = (
        Class.objects
        .filter(
            subjects__chapters__tests__created_by=request.user,
            subjects__chapters__tests__results__isnull=False,
        )
        .distinct()
        .order_by("order", "name")
    )

    subjects = (
        Subject.objects
        .filter(
            chapters__tests__created_by=request.user,
            chapters__tests__results__isnull=False,
        )
        .select_related("class_level")
        .distinct()
        .order_by("class_level__order", "name")
    )

    chapters = (
        Chapter.objects
        .filter(
            tests__created_by=request.user,
            tests__results__isnull=False,
        )
        .select_related("subject", "subject__class_level")
        .distinct()
        .order_by(
            "subject__class_level__order",
            "subject__name",
            "chapter_number",
        )
    )

    tests = (
        Test.objects
        .filter(
            created_by=request.user,
            results__isnull=False,
        )
        .select_related(
            "chapter",
            "chapter__subject",
            "chapter__subject__class_level",
        )
        .distinct()
        .order_by("-created_at")
    )

    average_percentage = (
        round(sum(percentages) / len(percentages), 1)
        if percentages
        else 0.0
    )

    return render(
        request,
        "education/teacher/results.html",
        {
            "result_rows": result_rows,
            "total_results": len(result_rows),
            "average_percentage": average_percentage,
            "students_count": len({row["result"].student_id for row in result_rows}),
            "classes": classes,
            "subjects": subjects,
            "chapters": chapters,
            "tests": tests,
            "filters": {
                "q": search_query,
                "class": class_id,
                "subject": subject_id,
                "chapter": chapter_id,
                "test": test_id,
            },
        },
    )


@teacher_required
def teacher_result_detail(request, result_id):
    """
    Read-only detailed view of one submitted result belonging to
    a test created by the logged-in teacher.
    """

    result = get_object_or_404(
        TestResult.objects
        .select_related(
            "student",
            "test",
            "test__chapter",
            "test__chapter__subject",
            "test__chapter__subject__class_level",
        )
        .prefetch_related("answers__question"),
        id=result_id,
        test__created_by=request.user,
    )

    total_marks = float(result.total_marks or 0)
    score = float(result.score or 0)
    percentage = round((score / total_marks) * 100, 1) if total_marks else 0.0

    return render(
        request,
        "education/teacher/result_detail.html",
        {
            "result": result,
            "answers": result.answers.all(),
            "percentage": percentage,
        },
    )

# ============================================================
# CLASS 10 - AI EXAM STRATEGY
# ============================================================

def _generate_ai_exam_strategy(student, results):

    api_key = config(
        "GEMINI_API_KEY",
        default=""
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not configured."
        )

    model_name = config(
        "GEMINI_MODEL",
        default="gemini-3.6-flash"
    )

    performance = []

    for result in results:

        percentage = 0

        if result.total_marks:
            percentage = round(
                (
                    float(result.score)
                    / float(result.total_marks)
                ) * 100,
                1
            )

        performance.append({
            "subject": result.test.chapter.subject.name,
            "chapter": result.test.chapter.name,
            "test": result.test.title,
            "score": result.score,
            "total": result.total_marks,
            "percentage": percentage,
        })

    prompt = f"""
You are an educational exam-strategy assistant
for a Class 10 student using the Udaan platform.

Create a practical and personalized Class 10
exam preparation strategy based ONLY on the student's
actual Udaan test performance below.

Student:
{student.get_full_name() or student.username}

Class 10 Test Performance:
{json.dumps(performance, ensure_ascii=False)}

Return ONLY valid JSON using exactly this structure:

{{
    "overall_assessment": "short assessment",
    "priority_subjects": [
        {{
            "subject": "subject name",
            "reason": "why this needs attention",
            "action": "what the student should do"
        }}
    ],
    "strong_areas": [
        "short point"
    ],
    "weak_areas": [
        "short point"
    ],
    "daily_plan": [
        {{
            "time": "1 hour",
            "activity": "specific study activity"
        }}
    ],
    "final_week_strategy": [
        "short actionable point"
    ],
    "exam_day_tips": [
        "short actionable point"
    ]
}}

Rules:
1. This is ONLY for Class 10 exam preparation.
2. Use the student's actual performance only.
3. Prioritize subjects/topics with lower scores.
4. Do not invent test scores or subjects.
5. Do not create mock tests because Udaan already has an AI test system.
6. Recommend one-shot revision lectures, important questions and previous-year papers where appropriate.
7. Give simple and practical advice suitable for a Class 10 student.
8. Keep the response concise.
"""

    api_url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/interactions"
    )

    response_schema = {
        "type": "object",
        "properties": {
            "overall_assessment": {
                "type": "string"
            },
            "priority_subjects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string"},
                        "reason": {"type": "string"},
                        "action": {"type": "string"},
                    },
                    "required": [
                        "subject",
                        "reason",
                        "action"
                    ]
                }
            },
            "strong_areas": {
                "type": "array",
                "items": {"type": "string"}
            },
            "weak_areas": {
                "type": "array",
                "items": {"type": "string"}
            },
            "daily_plan": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "time": {"type": "string"},
                        "activity": {"type": "string"},
                    },
                    "required": [
                        "time",
                        "activity"
                    ]
                }
            },
            "final_week_strategy": {
                "type": "array",
                "items": {"type": "string"}
            },
            "exam_day_tips": {
                "type": "array",
                "items": {"type": "string"}
            },
        },
        "required": [
            "overall_assessment",
            "priority_subjects",
            "strong_areas",
            "weak_areas",
            "daily_plan",
            "final_week_strategy",
            "exam_day_tips",
        ]
    }

    payload = {
        "model": model_name,
        "input": prompt,
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": response_schema
        },
        "generation_config": {
            "max_output_tokens": 3000
        },
        "store": False
    }

    try:
        response = requests.post(
            api_url,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=90
        )
    except requests.RequestException as exc:
        raise ValueError(
            "Unable to connect to the Gemini API. "
            "Please check your internet connection."
        ) from exc

    if not response.ok:
        try:
            error_data = response.json()
            error_message = (
                error_data
                .get("error", {})
                .get("message")
            )
        except ValueError:
            error_message = None

        raise ValueError(
            error_message
            or (
                "Gemini API request failed "
                f"with status {response.status_code}."
            )
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError(
            "Gemini returned an invalid API response."
        ) from exc

    if data.get("status") == "failed":
        raise ValueError(
            "Gemini interaction failed."
        )

    generated_text = ""

    for step in data.get("steps", []):
        if step.get("type") != "model_output":
            continue

        for content in step.get("content", []):
            if content.get("type") == "text":
                generated_text += content.get(
                    "text",
                    ""
                )

    generated_text = generated_text.strip()

    if not generated_text:
        raise ValueError(
            "Gemini did not return an exam strategy."
        )

    try:
        strategy = json.loads(
            generated_text
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini returned invalid strategy JSON."
        ) from exc

    return strategy



# ============================================================
# STUDENT - EXAM PREPARATION
# ============================================================

@student_required
def student_exam_strategy(request):

    """
    Class 10 Exam Preparation page.

    Students still have access to all classes.

    This page simply provides Class 10 preparation
    resources and Class 10 AI strategy.
    """


    # --------------------------------------------------------
    # GET CLASS 10 RESULTS ONLY
    # --------------------------------------------------------

    results = list(

        TestResult.objects.filter(

            student=request.user,

            test__chapter__subject__class_level__name__icontains="10"

        )

        .select_related(

            "test",

            "test__chapter",

            "test__chapter__subject",

            "test__chapter__subject__class_level",

        )

        .order_by(

            "-submitted_at"

        )[:20]

    )


    strategy = None

    generation_error = None


    # --------------------------------------------------------
    # GENERATE AI STRATEGY
    # --------------------------------------------------------

    if request.method == "POST":

        if not results:

            generation_error = (
                "Complete at least one Class 10 test "
                "to generate your personalized AI exam strategy."
            )

        else:

            try:

                strategy = _generate_ai_exam_strategy(

                    request.user,

                    results

                )

            except ValueError as exc:

                generation_error = str(
                    exc
                )


    # --------------------------------------------------------
    # PERFORMANCE SUMMARY
    # --------------------------------------------------------

    performance_summary = []


    for result in results:

        percentage = 0


        if result.total_marks:

            percentage = round(

                (

                    float(
                        result.score
                    )

                    /

                    float(
                        result.total_marks
                    )

                )

                * 100

            , 1)


        performance_summary.append({

            "subject":
                result.test.chapter.subject.name,

            "chapter":
                result.test.chapter.name,

            "test":
                result.test.title,

            "score":
                result.score,

            "total":
                result.total_marks,

            "percentage":
                percentage,

        })


    # --------------------------------------------------------
    # RENDER
    # --------------------------------------------------------

    return render(

        request,

        "education/student/exam_strategy.html",

        {

            "results":
                results,

            "performance_summary":
                performance_summary,

            "strategy":
                strategy,

            "generation_error":
                generation_error,

        }

    )