from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .models import HealthReport

from openai import OpenAI

import base64
import requests
import math
import time


# ============================================================
# HEALTHCARE PAGES
# ============================================================

def healthcare_home(request):
    return render(request, 'healthcare/healthcare_home.html')


def womens_health(request):
    return render(request, 'healthcare/womens_health.html')


def general_health(request):
    return render(request, 'healthcare/general_health.html')


def menstrual_health(request):
    return render(request, 'healthcare/menstrual_health.html')


def pregnancy_health(request):
    return render(request, 'healthcare/pregnancy_health.html')


def nutrition_anemia(request):
    return render(request, 'healthcare/nutrition_anemia.html')


def pcos_hormonal(request):
    return render(request, 'healthcare/pcos_hormonal.html')


def breast_cervical(request):
    return render(request, 'healthcare/breast_cervical.html')


def mental_emotional_health(request):
    return render(request, 'healthcare/mental_emotional_health.html')


def reproductive_sexual_health(request):
    return render(request, 'healthcare/reproductive_sexual_health.html')


def women_health_across_ages(request):
    return render(request, 'healthcare/women_health_across_ages.html')


def women_health_insights(request):
    return render(request, 'healthcare/women_health_insights.html')


# ============================================================
# HEALTH AWARENESS
# ============================================================

def health_awareness(request):
    return render(request, 'healthcare/health_awareness.html')


def healthy_diet_nutrition(request):
    return render(
        request,
        'healthcare/healthy_diet_nutrition.html'
    )


def hygiene_sanitation(request):
    return render(
        request,
        'healthcare/hygiene_sanitation.html'
    )


def vaccination_immunization(request):
    return render(
        request,
        'healthcare/vaccination_immunization.html'
    )


def common_diseases_prevention(request):
    return render(
        request,
        'healthcare/common_diseases_prevention.html'
    )


def preventive_healthcare(request):
    return render(
        request,
        'healthcare/preventive_healthcare.html'
    )


def maternal_child_health(request):
    return render(
        request,
        'healthcare/maternal_child_health.html'
    )


def healthy_lifestyle(request):
    return render(
        request,
        'healthcare/healthy_lifestyle.html'
    )


def mental_health_all_ages(request):
    return render(
        request,
        'healthcare/mental_health_all_ages.html'
    )


def emergency_first_aid(request):
    return render(
        request,
        'healthcare/emergency_first_aid.html'
    )


# ============================================================
# NEARBY HEALTHCARE PAGE
# ============================================================

def nearby_healthcare(request):
    return render(
        request,
        'healthcare/nearby_healthcare.html'
    )

def health_report_ocr(request):
    return render(
        request,
        'healthcare/health_report_ocr.html'
    )


@require_POST
def save_health_report(request):

    extracted_information = request.POST.get(
        "extracted_information",
        ""
    ).strip()

    patient_name = request.POST.get(
        "patient_name",
        ""
    ).strip()

    report_type = request.POST.get(
        "report_type",
        "Medical Report / Prescription"
    ).strip()

    report_date = request.POST.get(
        "report_date",
        ""
    ).strip()

    uploaded_image = request.FILES.get("image")

    if not extracted_information:
        return JsonResponse({
            "success": False,
            "error": "No extracted report information found."
        }, status=400)

    try:
        report = HealthReport.objects.create(
            patient_name=patient_name,
            report_type=report_type or "Medical Report / Prescription",
            report_date=report_date or None,
            extracted_information=extracted_information,
            explanation="",
            report_image=uploaded_image
        )

        return JsonResponse({
            "success": True,
            "report_id": report.id,
            "message": "Health report saved successfully."
        })

    except Exception as e:
        print("Save Health Report Error:", e)

        return JsonResponse({
            "success": False,
            "error": "Unable to save the health report."
        }, status=500)

# =========================================================
# PREVIOUS HEALTH REPORTS
# =========================================================

def previous_health_reports(request):

    reports = HealthReport.objects.all().order_by('-created_at')

    return render(
        request,
        'healthcare/previous_health_reports.html',
        {
            'reports': reports
        }
    )

# =========================================================
# EMERGENCY HELPLINE
# =========================================================

def emergency_helpline(request):

    return render(
        request,
        'healthcare/emergency_helpline.html'
    )

# =========================================================
# DELETE HEALTH REPORT
# =========================================================

from django.views.decorators.http import require_POST

@require_POST
def delete_health_report(request, report_id):

    try:
        report = HealthReport.objects.get(id=report_id)

        if report.report_image:
            report.report_image.delete(save=False)

        report.delete()

        return JsonResponse({
            "success": True,
            "message": "Health report deleted successfully."
        })

    except HealthReport.DoesNotExist:

        return JsonResponse({
            "success": False,
            "error": "Health report not found."
        }, status=404)

    except Exception as e:

        print("Delete Health Report Error:", e)

        return JsonResponse({
            "success": False,
            "error": "Unable to delete the health report."
        }, status=500)

# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        +
        math.cos(math.radians(lat1))
        *
        math.cos(math.radians(lat2))
        *
        math.sin(d_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ============================================================
# ADDRESS
# ============================================================

def get_centre_address(tags):

    parts = []

    address_keys = [
        "addr:housenumber",
        "addr:street",
        "addr:suburb",
        "addr:city",
        "addr:postcode"
    ]

    for key in address_keys:

        if tags.get(key):
            parts.append(tags[key])

    if parts:
        return ", ".join(parts)

    return "Address not available"


# ============================================================
# GOVERNMENT CENTRE CHECK
# ============================================================

def is_government_centre(tags):

    name = tags.get(
        "name",
        ""
    ).lower()

    operator = tags.get(
        "operator",
        ""
    ).lower()

    operator_type = tags.get(
        "operator:type",
        ""
    ).lower()

    text = (
        name
        + " "
        + operator
        + " "
        + operator_type
    )

    government_words = [
        "government",
        "govt",
        "public",
        "primary health centre",
        "primary health center",
        "phc",
        "community health centre",
        "community health center",
        "chc",
        "civil hospital",
        "district hospital"
    ]

    return any(
        word in text
        for word in government_words
    )


# ============================================================
# CLASSIFY HEALTHCARE CENTRE
# ============================================================

def classify_centre(tags):

    amenity = tags.get(
        "amenity",
        ""
    ).lower()

    healthcare = tags.get(
        "healthcare",
        ""
    ).lower()

    # Pharmacy
    if amenity == "pharmacy":
        return "pharmacy"

    # Government healthcare
    if is_government_centre(tags):
        return "government"

    # Hospital
    if (
        amenity == "hospital"
        or healthcare == "hospital"
    ):
        return "hospital"

    # Clinic / Doctor
    return "clinic"


# ============================================================
# NEARBY HEALTHCARE SEARCH API
# ============================================================

@require_GET
def nearby_healthcare_search(request):

    try:

        latitude = request.GET.get("lat")
        longitude = request.GET.get("lon")
        location_query = request.GET.get("query")

        location_name = "Your Location"

        # ====================================================
        # MANUAL LOCATION SEARCH
        # ====================================================

        if (
            location_query
            and not latitude
            and not longitude
        ):

            nominatim_url = (
                "https://nominatim.openstreetmap.org/search"
            )

            headers = {
                "User-Agent":
                    "UdaanHealthcareStudentProject/1.0"
            }

            params = {
                "q": location_query,
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "in"
            }

            response = requests.get(
                nominatim_url,
                params=params,
                headers=headers,
                timeout=15
            )

            response.raise_for_status()

            location_data = response.json()

            if not location_data:

                return JsonResponse({

                    "success": False,

                    "error":
                        "Location not found. Please enter a valid village, area or city."

                }, status=404)

            latitude = float(
                location_data[0]["lat"]
            )

            longitude = float(
                location_data[0]["lon"]
            )

            location_name = location_data[0].get(
                "display_name",
                location_query
            )

        # ====================================================
        # GPS LOCATION
        # ====================================================

        elif latitude and longitude:

            latitude = float(latitude)
            longitude = float(longitude)

        else:

            return JsonResponse({

                "success": False,

                "error":
                    "Please provide a location."

            }, status=400)


        # ====================================================
        # SEARCH AREA
        # ====================================================

        lat_offset = 0.045
        lon_offset = 0.045

        south = latitude - lat_offset
        north = latitude + lat_offset
        west = longitude - lon_offset
        east = longitude + lon_offset

        viewbox = (
            f"{west},{north},{east},{south}"
        )


        headers = {
            "User-Agent":
                "UdaanHealthcareStudentProject/1.0"
        }


        categories = {

            "hospital": [],

            "clinic": [],

            "pharmacy": [],

            "government": []

        }


        # ====================================================
        # NOMINATIM SEARCH FUNCTION
        # ====================================================

        def search_places(search_term):

            url = (
                "https://nominatim.openstreetmap.org/search"
            )

            params = {

                "q": search_term,

                "format": "jsonv2",

                "limit": 20,

                "viewbox": viewbox,

                "bounded": 1,

                "addressdetails": 1,

                "countrycodes": "in"

            }

            try:

                response = requests.get(

                    url,

                    params=params,

                    headers=headers,

                    timeout=15

                )

                print(
                    "Nominatim:",
                    search_term,
                    response.status_code
                )

                if response.status_code != 200:

                    return []

                return response.json()

            except Exception as e:

                print(
                    "Nominatim error:",
                    search_term,
                    e
                )

                return []


        # ====================================================
        # HOSPITALS
        # ====================================================

        hospital_results = search_places(
            "hospital"
        )

        for place in hospital_results:

            add_healthcare_place(

                categories,

                place,

                latitude,

                longitude,

                "hospital"

            )


        time.sleep(1.1)


        # ====================================================
        # CLINICS
        # ====================================================

        clinic_results = search_places(
            "clinic"
        )

        for place in clinic_results:

            add_healthcare_place(

                categories,

                place,

                latitude,

                longitude,

                "clinic"

            )


        time.sleep(1.1)


        # ====================================================
        # PHARMACIES
        # ====================================================

        pharmacy_results = search_places(
            "pharmacy"
        )

        for place in pharmacy_results:

            add_healthcare_place(

                categories,

                place,

                latitude,

                longitude,

                "pharmacy"

            )


        time.sleep(1.1)


        # ====================================================
        # GOVERNMENT HEALTH CENTRES
        # ====================================================

        government_results = search_places(
            "government hospital"
        )

        for place in government_results:

            add_healthcare_place(

                categories,

                place,

                latitude,

                longitude,

                "government"

            )


        # ====================================================
        # SORT BY DISTANCE
        # ====================================================

        for category in categories:

            categories[category].sort(

                key=lambda item:
                    item["distance"]

            )

            categories[category] = (
                categories[category][:10]
            )


        # ====================================================
        # FINAL RESPONSE
        # ====================================================

        return JsonResponse({

            "success": True,

            "location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "name":
                    location_name

            },

            "categories":
                categories

        })


    except Exception as e:

        print(
            "Nearby Healthcare Error:",
            e
        )

        return JsonResponse({

            "success": False,

            "error":
                "Unable to load nearby healthcare centres. Please try again."

        }, status=500)


# ============================================================
# ADD HEALTHCARE PLACE
# ============================================================

def add_healthcare_place(
    categories,
    place,
    user_lat,
    user_lon,
    category
):

    try:

        place_lat = float(
            place["lat"]
        )

        place_lon = float(
            place["lon"]
        )


        name = (

            place.get("name")

            or
            place.get(
                "display_name",
                ""
            ).split(",")[0]

            or
            "Healthcare Centre"

        )


        address = place.get(

            "display_name",

            "Address not available"

        )


        distance = calculate_distance(

            user_lat,

            user_lon,

            place_lat,

            place_lon

        )


        # ====================================================
        # REMOVE DUPLICATES
        # ====================================================

        for existing in categories[category]:

            if (

                abs(
                    existing["latitude"]
                    - place_lat
                ) < 0.0001

                and

                abs(
                    existing["longitude"]
                    - place_lon
                ) < 0.0001

            ):

                return


        categories[category].append({

            "name":
                name,

            "address":
                address,

            "latitude":
                place_lat,

            "longitude":
                place_lon,

            "distance":
                round(
                    distance,
                    2
                )

        })


    except Exception as e:

        print(
            "Place processing error:",
            e
        )


# ============================================================
# AI HEALTHCARE CHATBOT
# ============================================================

def healthcare_chatbot(request):

    return render(
        request,
        'healthcare/healthcare_chatbot.html'
    )


HEALTHCARE_SYSTEM_INSTRUCTION = """
You are Pentra One Health Assistant, an informational healthcare assistant for rural communities.

Rules:
- Answer only healthcare-related questions.
- Use simple, clear language and short bullet points.
- Reply in the same language as the user (English, Hindi, Hinglish, or Marathi).
- For symptoms, explain possible causes, basic self-care, and warning signs. Never give a definite diagnosis.
- For medicines, provide only general information. Never prescribe, change dosage, or tell the user to start/stop a medicine.
- For reports, prescriptions, and healthcare images, explain only visible/readable information. Never invent missing values.
- If the image/report is unclear, say that clearly.
- For serious symptoms such as severe chest pain, severe breathing difficulty, unconsciousness, stroke-like symptoms, severe bleeding, or serious injury, advise urgent medical attention immediately.
- Keep simple answers to about 3-6 useful points.
- If the question is not about healthcare, reply exactly:
  "I am Pentra One Health Assistant. I can only help with healthcare-related information. Please ask me a healthcare question."
"""


# ============================================================
# FAST GEMINI HELPERS
# ============================================================

def _healthcare_client():
    """Create a Gemini OpenAI-compatible client with no automatic retries."""
    api_key = getattr(settings, "HEALTHCARE_GEMINI_API_KEY", "")

    if not api_key:
        raise RuntimeError("Healthcare Gemini API key is not configured.")

    return OpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        timeout=18.0,
        max_retries=0,
    )


def _is_temporary_ai_error(error):
    error_text = str(error).lower()
    temporary_words = (
        "503",
        "429",
        "unavailable",
        "high demand",
        "overloaded",
        "temporarily",
        "rate limit",
        "resource exhausted",
        "timeout",
        "timed out",
    )
    return any(word in error_text for word in temporary_words)


def _call_healthcare_ai(messages, max_tokens=260):
    """
    Fast AI call:
    - low-latency model first
    - only one fallback model
    - no sleep / no repeated retry loops
    """
    client = _healthcare_client()

    model_names = (
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
    )

    last_error = None

    for model_name in model_names:
        try:
            print(f"Healthcare Gemini: trying {model_name}")

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2,
                max_tokens=max_tokens,
            )

            reply = response.choices[0].message.content

            if reply and reply.strip():
                return reply.strip()

        except Exception as exc:
            last_error = exc
            print(f"Healthcare Gemini model error ({model_name}):", exc)

            # For permanent errors such as invalid API key / malformed request,
            # do not waste time trying more models.
            if not _is_temporary_ai_error(exc):
                raise

    if last_error:
        raise last_error

    raise RuntimeError("Healthcare AI returned an empty response.")


def _image_to_data_url(uploaded_image):
    """Validate and convert an uploaded healthcare image to a data URL."""
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    if uploaded_image.content_type not in allowed_types:
        raise ValueError("Please upload only a JPG, PNG or WebP image.")

    # Keep image requests reasonably small for faster upload/API processing.
    if uploaded_image.size > 5 * 1024 * 1024:
        raise ValueError("Image size must be 5 MB or smaller.")

    image_bytes = uploaded_image.read()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    return (
        f"data:{uploaded_image.content_type};base64,"
        f"{encoded_image}"
    )


# ============================================================
# CHATBOT SEND
# ============================================================

@require_POST
def healthcare_chatbot_send(request):
    message = request.POST.get("message", "").strip()
    uploaded_image = request.FILES.get("image")

    if not message and not uploaded_image:
        return JsonResponse({
            "success": False,
            "error": "Please enter a message or upload a health image."
        }, status=400)

    try:
        # Keep only the latest 6 messages (roughly 3 exchanges).
        # This keeps follow-up context while reducing payload and latency.
        chat_history = request.session.get("healthcare_chat_history", [])[-6:]

        messages = [{
            "role": "system",
            "content": HEALTHCARE_SYSTEM_INSTRUCTION,
        }]

        for item in chat_history:
            role = item.get("role")
            content = item.get("content")

            if role in {"user", "assistant"} and content:
                messages.append({
                    "role": role,
                    "content": content,
                })

        if uploaded_image:
            image_data_url = _image_to_data_url(uploaded_image)

            image_question = message or (
                "Analyze this healthcare image. If it is a medical report or "
                "prescription, extract and explain the readable information in "
                "simple bullet points. Mention abnormal-looking values only as "
                "observations, not as a diagnosis."
            )

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": image_question,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                        },
                    },
                ],
            })
        else:
            messages.append({
                "role": "user",
                "content": message,
            })

        reply = _call_healthcare_ai(messages, max_tokens=260)

        history_message = message

        if uploaded_image and not history_message:
            history_message = "[User uploaded a healthcare image for analysis.]"
        elif uploaded_image:
            history_message = (
                f"[User uploaded healthcare image: {uploaded_image.name}] "
                f"{message}"
            )

        chat_history.append({
            "role": "user",
            "content": history_message,
        })

        chat_history.append({
            "role": "assistant",
            "content": reply,
        })

        request.session["healthcare_chat_history"] = chat_history[-6:]
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "reply": reply,
        })

    except ValueError as exc:
        return JsonResponse({
            "success": False,
            "error": str(exc),
        }, status=400)

    except Exception as exc:
        print("Healthcare Gemini Error:", exc)

        if "api key" in str(exc).lower():
            user_error = "Healthcare Gemini API key is not configured correctly."
            status_code = 500
        elif _is_temporary_ai_error(exc):
            user_error = (
                "Healthcare AI is busy right now. Please try again in a moment."
            )
            status_code = 503
        else:
            user_error = (
                "Healthcare AI could not process the request. Please try again."
            )
            status_code = 500

        return JsonResponse({
            "success": False,
            "error": user_error,
        }, status=status_code)


# ============================================================
# FAST HEALTH REPORT / PRESCRIPTION ANALYSIS
# ============================================================

@require_POST
def analyze_health_report(request):
    """
    Separate lightweight endpoint for report/prescription image analysis.

    POST fields:
        image: JPG / PNG / WebP
        message: optional extra instruction

    Returns both `analysis` and `extracted_information` so existing front-end
    code can use either key.
    """
    uploaded_image = request.FILES.get("image")
    extra_message = request.POST.get("message", "").strip()

    if not uploaded_image:
        return JsonResponse({
            "success": False,
            "error": "Please upload a health report or prescription image."
        }, status=400)

    try:
        image_data_url = _image_to_data_url(uploaded_image)

        report_prompt = (
            "Read this medical report or prescription carefully. "
            "Extract only information that is actually readable. "
            "Return a concise point-wise explanation with these sections when "
            "applicable: Report type, Patient details, Test/medicine names, "
            "Visible values or instructions, Simple explanation, and Important "
            "notes. Do not invent unreadable text and do not give a definite "
            "diagnosis."
        )

        if extra_message:
            report_prompt += f"\nUser request: {extra_message}"

        messages = [
            {
                "role": "system",
                "content": HEALTHCARE_SYSTEM_INSTRUCTION,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": report_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                        },
                    },
                ],
            },
        ]

        analysis = _call_healthcare_ai(messages, max_tokens=420)

        return JsonResponse({
            "success": True,
            "analysis": analysis,
            "reply": analysis,
            "extracted_information": analysis,
        })

    except ValueError as exc:
        return JsonResponse({
            "success": False,
            "error": str(exc),
        }, status=400)

    except Exception as exc:
        print("Health Report Analysis Error:", exc)

        if "api key" in str(exc).lower():
            user_error = "Healthcare Gemini API key is not configured correctly."
            status_code = 500
        elif _is_temporary_ai_error(exc):
            user_error = (
                "Report analysis service is busy right now. Please try again shortly."
            )
            status_code = 503
        else:
            user_error = (
                "Unable to analyze this report right now. Please try another clear image."
            )
            status_code = 500

        return JsonResponse({
            "success": False,
            "error": user_error,
        }, status=status_code)


def disability_care(request):
    return render(request, 'healthcare/disability_care.html')
def disability_awareness(request):
    return render(request, 'healthcare/disability_awareness.html')
def daily_care_safety(request):
    return render(request, 'healthcare/daily_care_safety.html')
def mental_emotional_support(request):
    return render(request, 'healthcare/mental_emotional_support.html')
def accessibility_assistive_devices(request):
    return render(
        request,
        'healthcare/accessibility_assistive_devices.html'
    )
def healthcare_rehabilitation(request):
    return render(
        request,
        'healthcare/healthcare_rehabilitation.html'
    )
def government_schemes_support(request):
    return render(
        request,
        'healthcare/government_schemes_support.html'
    )