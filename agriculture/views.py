from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings

from .models import Crop, CropTranslation
from .translations import AGRICULTURE_UI

from google import genai
from PIL import Image, ImageOps

import io
import base64


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


# =========================================================
# AGRICULTURE LANGUAGE
# =========================================================

def agriculture_language(request):
    """
    Agriculture has its own language selection.
    It does NOT change the language of the rest of Udaan.
    """

    language = request.session.get("agriculture_language", "en")

    if language not in SUPPORTED_LANGUAGES:
        language = "en"

    return language


def agriculture_ui(language):
    return AGRICULTURE_UI.get(
        language,
        AGRICULTURE_UI["en"]
    )


def set_agriculture_language(request):
    """
    Change only the Agriculture module language.
    """

    if request.method == "POST":

        language = request.POST.get("language", "en")

        if language in SUPPORTED_LANGUAGES:
            request.session["agriculture_language"] = language
            request.session.modified = True

    next_url = request.POST.get(
        "next",
        request.META.get(
            "HTTP_REFERER",
            "/agriculture/"
        )
    )

    return redirect(next_url)


# =========================================================
# CROP TRANSLATION
# =========================================================

def translated_crop(crop, language):
    """
    Apply the selected Agriculture language
    to a crop without changing the database record.
    """

    if language == "en":
        return crop

    translation = crop.translations.filter(
        language=language
    ).first()

    if not translation:
        return crop

    crop.name = (
        translation.name
        or crop.name
    )

    crop.description = (
        translation.description
        or crop.description
    )

    crop.season = (
        translation.season
        or crop.season
    )

    crop.soil = (
        translation.soil
        or crop.soil
    )

    crop.water_requirement = (
        translation.water_requirement
        or crop.water_requirement
    )

    crop.sowing_time = (
        translation.sowing_time
        or crop.sowing_time
    )

    crop.harvesting_time = (
        translation.harvesting_time
        or crop.harvesting_time
    )

    crop.common_problems = (
        translation.common_problems
        or crop.common_problems
    )

    crop.farmer_tip = (
        translation.farmer_tip
        or crop.farmer_tip
    )

    return crop


# =========================================================
# AGRICULTURE HOME
# =========================================================

def agriculture_home(request):

    language = agriculture_language(request)

    crops = Crop.objects.filter(
        is_active=True
    )

    crops = [
        translated_crop(crop, language)
        for crop in crops
    ]

    return render(
        request,
        "agriculture/agriculture_home.html",
        {
            "crops": crops,
            "language": language,
            "ui": agriculture_ui(language),
        }
    )


# =========================================================
# CROP LIST
# =========================================================

def crop_list(request):

    language = agriculture_language(request)

    crops = Crop.objects.filter(
        is_active=True
    )

    crops = [
        translated_crop(crop, language)
        for crop in crops
    ]

    return render(
        request,
        "agriculture/crops.html",
        {
            "crops": crops,
            "language": language,
            "ui": agriculture_ui(language),
        }
    )


# =========================================================
# CROP DETAIL
# =========================================================

def crop_detail(request, crop_id):

    language = agriculture_language(request)

    crop = get_object_or_404(
        Crop,
        id=crop_id,
        is_active=True
    )

    crop = translated_crop(
        crop,
        language
    )

    return render(
        request,
        "agriculture/crop_detail.html",
        {
            "crop": crop,
            "language": language,
            "ui": agriculture_ui(language),
        }
    )


# =========================================================
# CROP PROBLEMS
# =========================================================

def crop_problems(request):

    language = agriculture_language(request)

    crops = Crop.objects.filter(
        is_active=True
    )

    crops = [
        translated_crop(crop, language)
        for crop in crops
    ]

    return render(
        request,
        "agriculture/crop_problems.html",
        {
            "crops": crops,
            "language": language,
            "ui": agriculture_ui(language),
        }
    )


def crop_problem_detail(request, crop_id):

    language = agriculture_language(request)

    crop = get_object_or_404(
        Crop,
        id=crop_id,
        is_active=True
    )

    crop = translated_crop(
        crop,
        language
    )

    return render(
        request,
        "agriculture/crop_problem_detail.html",
        {
            "crop": crop,
            "language": language,
            "ui": agriculture_ui(language),
        }
    )


# =========================================================
# WEATHER
# =========================================================

def weather(request):

    language = agriculture_language(request)

    return render(
        request,
        "agriculture/weather.html",
        {
            "language": language,
            "ui": agriculture_ui(language),
        }
    )


# =========================================================
# IMAGE PREVIEW
# =========================================================

def create_image_preview(image):

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=88,
        optimize=True
    )

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return (
        "data:image/jpeg;base64,"
        + encoded
    )


# =========================================================
# SCAN & ASK
# =========================================================

def scan_and_ask(request):

    language = agriculture_language(request)

    ui = agriculture_ui(language)

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    if request.method != "POST":

        return render(
            request,
            "agriculture/scan.html",
            {
                "language": "same",
                "module_language": language,
                "ui": ui,
            }
        )

    # -----------------------------------------------------
    # INPUT
    # -----------------------------------------------------

    uploaded_file = request.FILES.get(
        "image"
    )

    question = request.POST.get(
        "question",
        ""
    ).strip()

    answer_language = request.POST.get(
        "language",
        "same"
    )

    # -----------------------------------------------------
    # IMAGE VALIDATION
    # -----------------------------------------------------

    if not uploaded_file:

        return render(
            request,
            "agriculture/scan.html",
            {
                "message": ui.get("scan_no_image", "Please choose a photo first."),
                "question": question,
                "language": answer_language,
                "module_language": language,
                "ui": ui,
            }
        )

    # -----------------------------------------------------
    # QUESTION VALIDATION
    # -----------------------------------------------------

    if not question:

        return render(
            request,
            "agriculture/scan.html",
            {
                "message": ui.get("scan_no_question", "Please enter your question."),
                "language": answer_language,
                "module_language": language,
                "ui": ui,
            }
        )

    # -----------------------------------------------------
    # AI PROCESSING
    # -----------------------------------------------------

    try:

        image = Image.open(
            io.BytesIO(
                uploaded_file.read()
            )
        )

        image = ImageOps.exif_transpose(
            image
        )

        if image.mode != "RGB":
            image = image.convert("RGB")

        image.thumbnail(
            (1024, 1024)
        )

        uploaded_image_url = (
            create_image_preview(image)
        )

        # -------------------------------------------------
        # ANSWER LANGUAGE
        # -------------------------------------------------

        if answer_language == "same":

            language_instruction = """
Reply in exactly the same language and writing style
as the farmer's question.

Question:
{question}

Roman Hindi/Hinglish must remain Roman Hinglish.
Do not convert it to Devanagari.

Hindi Devanagari → Hindi.
Marathi → Marathi.
Gujarati → Gujarati.
Bengali → Bengali.
Tamil → Tamil.
Telugu → Telugu.
Kannada → Kannada.
Punjabi → Punjabi.
English → English.
""".format(
                question=question
            )

        else:

            language_instruction = {

                "english":
                    "Reply completely in simple English.",

                "hindi":
                    "Reply completely in simple Hindi using Devanagari.",

                "marathi":
                    "Reply completely in simple Marathi using Devanagari.",

                "gujarati":
                    "Reply completely in simple Gujarati.",

                "bengali":
                    "Reply completely in simple Bengali.",

                "tamil":
                    "Reply completely in simple Tamil.",

                "telugu":
                    "Reply completely in simple Telugu.",

                "kannada":
                    "Reply completely in simple Kannada.",

                "punjabi":
                    "Reply completely in simple Punjabi using Gurmukhi.",

            }.get(
                answer_language,
                "Reply in simple English."
            )

        # -------------------------------------------------
        # AI PROMPT
        # -------------------------------------------------

        prompt = f"""
You are Udaan, a practical agriculture assistant
for Indian farmers.

Farmer question:
{question}

{language_instruction}

Look at the image and answer the farmer's question.

Give a SHORT, useful answer.

Maximum 100-120 words.

Use this format when appropriate:

🌱 What I See
⚠️ What It May Be
💡 What To Do
🛡️ Prevention

For identification questions,
use only the relevant sections.

For fruit, berry, plant or animal-feed safety:

never claim something is safe to eat or feed
if identification is uncertain.

Use simple everyday farmer language.

No long introduction.
No formal report.
No unnecessary technical explanation.
Do not repeat the question.
Do not say "As an AI".
"""

        # -------------------------------------------------
        # GEMINI
        # -------------------------------------------------

        client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                prompt,
                image
            ]
        )

        answer = (
            response.text.strip()
            if response and response.text
            else
            "I could not understand the image clearly. "
            "Please try a clearer photo."
        )

        answer = (
            answer
            .replace("```", "")
            .replace("**", "")
            .replace("###", "")
        )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        return render(
            request,
            "agriculture/scan.html",
            {
                "message":
                    ui.get("scan_success", "Analysis completed successfully."),

                "answer":
                    answer,

                "question":
                    question,

                "language":
                    answer_language,

                "module_language":
                    language,

                "uploaded_image_url":
                    uploaded_image_url,

                "ui":
                    ui,
            }
        )

    # -----------------------------------------------------
    # ERROR
    # -----------------------------------------------------

    except Exception as error:

        print(
            "FAST SCAN ERROR:",
            error
        )

        return render(
            request,
            "agriculture/scan.html",
            {
                "message":
                    ui.get("scan_busy", "The AI service is busy right now. Please try again."),

                "question":
                    question,

                "language":
                    answer_language,

                "module_language":
                    language,

                "ui":
                    ui,
            }
        )