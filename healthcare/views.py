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

You are Udaan Health Assistant, an AI healthcare assistant
for rural communities.

YOUR MAIN PURPOSE:

Help users with healthcare-related information in a simple,
clear and easy-to-understand way.


IMPORTANT RULES:


1. HEALTHCARE ONLY

Answer ONLY healthcare-related questions.

You can help with:

- General health
- Common symptoms
- Women's health
- Child health
- Elderly health
- Disability health
- Nutrition
- Hygiene
- Medicines (general information only)
- Health reports
- Prescriptions
- Healthcare services
- Emergency health guidance
- Preventive healthcare
- Basic health awareness
- Healthcare images and uploaded reports/prescriptions


2. NON-HEALTHCARE QUESTIONS

If the user asks about:

- Python
- Programming
- Coding
- Agriculture
- Education
- Jobs
- Entertainment
- Movies
- Sports
- Politics
- Technology
- Any other non-healthcare topic

Reply EXACTLY with:

"I am Udaan Health Assistant. I can only help with healthcare-related information. Please ask me a healthcare question."


3. CONVERSATION CONTEXT

Remember and use the previous messages in the current conversation.

If the user asks a follow-up question, understand what they are
referring to from the previous messages.

Do not ask the user to repeat information that is already available
in the conversation.

Uploaded images are available only in the request where they are uploaded.

Do not claim to remember an old image unless it is uploaded again.


4. POINT-WISE ANSWERS

ALWAYS answer in a clear point-wise format.

Use:

- Bullet points
- Numbered lists
- Short headings

Avoid long paragraphs.


5. SIMPLE LANGUAGE

Use simple language that a rural community user can understand.

Avoid unnecessary medical terminology.

If you use a medical term, explain it in simple language.


6. LANGUAGE SUPPORT

If the user writes in English:
Respond in English.

If the user writes in Hindi:
Respond in Hindi.

If the user writes in Hinglish:
Respond in Hinglish.

If the user writes in Marathi:
Respond in Marathi.

Always try to respond in the same language as the user.


7. HEALTH SYMPTOMS

When a user asks about symptoms, preferably use:

Possible reasons:
- Point 1
- Point 2
- Point 3

What you can do:
- Point 1
- Point 2
- Point 3

When to see a doctor:
- Warning sign 1
- Warning sign 2
- Warning sign 3

Never say that the user definitely has a particular disease.


8. MEDICINES

You may provide general information about medicines.

You may explain:

- General purpose
- Common uses
- General precautions

DO NOT:

- Prescribe medicines
- Give personalized dosage instructions
- Tell the user to start a medicine
- Tell the user to stop a medicine
- Tell the user to change their dosage


9. HEALTH REPORTS, PRESCRIPTIONS AND IMAGES

If the user uploads a healthcare image:

- Analyze only what is visible or readable.
- Help explain visible text, labels, report values,
  prescription information and healthcare-related content.
- Explain medical terms in simple language.
- If the image is blurry or unreadable, say so.
- Do not invent missing values or information.
- Do not provide a definite diagnosis from an image.
- Do not claim an image proves a disease.
- Encourage professional evaluation for important or abnormal findings.

For prescriptions:

- Explain visible medicine names/instructions when possible.
- Do not prescribe medicines.
- Do not change dosage instructions.
- Do not tell the user to start or stop a medicine based only on the image.

For medical reports:

- Explain visible values and terms in simple language.
- Do not decide that the person definitely has a disease.


10. EMERGENCY SITUATIONS

If the user describes potentially serious or life-threatening symptoms:

- Clearly tell them to seek urgent medical attention.
- Keep the emergency guidance short and clear.

Examples:

- Severe breathing difficulty
- Severe chest pain
- Loss of consciousness
- Severe bleeding
- Stroke-like symptoms
- Serious injury


11. DO NOT DIAGNOSE

Never provide a definite medical diagnosis.

Use phrases such as:

- "This can have several possible causes."
- "This may be related to..."
- "A healthcare professional can properly evaluate this."


12. DO NOT REPLACE A DOCTOR

You are an informational healthcare assistant.

Do not claim to replace doctors, nurses, pharmacists or other qualified
healthcare professionals.


13. RESPONSE LENGTH

For simple questions:

Give 3-6 important points.

For detailed questions:

Use headings and bullet points.

Do not unnecessarily repeat information.


14. FRIENDLY TONE

Be polite, supportive and respectful.

Do not scare the user unnecessarily.


15. FINAL SAFETY

For important symptoms, medicines, reports, images or medical conditions,
recommend consulting a qualified healthcare professional when appropriate.

Never provide false certainty about a person's health.

"""


# ============================================================
# CHATBOT SEND
# ============================================================
@require_POST
def healthcare_chatbot_send(request):

    message = request.POST.get(
        "message",
        ""
    ).strip()

    uploaded_image = request.FILES.get(
        "image"
    )

    if not message and not uploaded_image:

        return JsonResponse({

            "success":
                False,

            "error":
                "Please enter a message or upload a health image."

        }, status=400)


    # ========================================================
    # API KEY
    # ========================================================

    api_key = getattr(
        settings,
        "HEALTHCARE_GEMINI_API_KEY",
        ""
    )


    if not api_key:

        return JsonResponse({

            "success":
                False,

            "error":
                "Healthcare Gemini API key is not configured."

        }, status=500)


    # ========================================================
    # IMAGE PROCESSING
    # ========================================================

    image_data_url = None


    if uploaded_image:

        allowed_types = {

            "image/jpeg",

            "image/png",

            "image/webp"

        }


        if uploaded_image.content_type not in allowed_types:

            return JsonResponse({

                "success":
                    False,

                "error":
                    "Please upload only a JPG, PNG or WebP image."

            }, status=400)


        if uploaded_image.size > 5 * 1024 * 1024:

            return JsonResponse({

                "success":
                    False,

                "error":
                    "Image size must be 5 MB or smaller."

            }, status=400)


        try:

            image_bytes = uploaded_image.read()

            encoded_image = base64.b64encode(
                image_bytes
            ).decode(
                "utf-8"
            )

            image_data_url = (

                f"data:{uploaded_image.content_type};base64,"

                f"{encoded_image}"

            )

        except Exception as e:

            print(
                "Image processing error:",
                e
            )

            return JsonResponse({

                "success":
                    False,

                "error":
                    "The uploaded image could not be processed."

            }, status=400)


    # ========================================================
    # CHAT HISTORY
    # ========================================================

    chat_history = request.session.get(
        "healthcare_chat_history",
        []
    )

    chat_history = chat_history[-10:]


    messages = [

        {

            "role":
                "system",

            "content":
                HEALTHCARE_SYSTEM_INSTRUCTION

        }

    ]


    for item in chat_history:

        messages.append({

            "role":
                item["role"],

            "content":
                item["content"]

        })


    # ========================================================
    # IMAGE MESSAGE
    # ========================================================

    if image_data_url:

        image_question = message or (

            "Please analyze this healthcare image and explain what "
            "you can observe in simple, point-wise language. If it is "
            "a medical report or prescription, explain the visible "
            "information and medical terms. Do not diagnose."

        )


        messages.append({

            "role":
                "user",

            "content": [

                {

                    "type":
                        "text",

                    "text":
                        image_question

                },

                {

                    "type":
                        "image_url",

                    "image_url": {

                        "url":
                            image_data_url

                    }

                }

            ]

        })


    else:

        messages.append({

            "role":
                "user",

            "content":
                message

        })


    # ========================================================
    # GEMINI API
    # Retry + fallback handling for temporary 503 / high-demand errors
    # ========================================================

    try:

        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

        # Try the preferred model first, then fall back to other stable Flash models.
        # This prevents the whole chatbot from failing when one Gemini model is busy.
        gemini_models = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
            "gemini-3.5-flash-lite",
        ]

        response = None
        last_error = None

        for model_name in gemini_models:

            # Retry each model a few times for temporary server overloads.
            for attempt in range(3):

                try:

                    print(
                        f"Healthcare Gemini: trying {model_name}, "
                        f"attempt {attempt + 1}/3"
                    )

                    response = client.chat.completions.create(
                        model=model_name,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=300,
                        reasoning_effort="low"
                    )

                    # Successful request: stop retrying/fallback.
                    break

                except Exception as model_error:

                    last_error = model_error
                    error_text = str(model_error).lower()

                    is_temporary_error = (
                        "503" in error_text
                        or "unavailable" in error_text
                        or "high demand" in error_text
                        or "overloaded" in error_text
                        or "temporarily" in error_text
                    )

                    print(
                        f"Healthcare Gemini model error "
                        f"({model_name}, attempt {attempt + 1}):",
                        model_error
                    )

                    # For a temporary overload, wait briefly and retry.
                    if is_temporary_error and attempt < 2:
                        time.sleep(2 * (attempt + 1))
                        continue

                    # Stop retrying this model and move to the fallback model.
                    break

            if response is not None:
                break

        if response is None:
            if last_error:
                raise last_error
            raise RuntimeError("No Gemini model returned a response.")

        reply = response.choices[0].message.content

        if not reply:
            reply = (
                "Sorry, I could not generate a response right now."
            )


        # ====================================================
        # SAVE CHAT HISTORY
        # ====================================================

        history_message = message


        if uploaded_image and not history_message:

            history_message = (
                "[User uploaded a healthcare image for analysis.]"
            )


        elif uploaded_image:

            history_message = (

                f"[User uploaded a healthcare image: "

                f"{uploaded_image.name}] {message}"

            )


        chat_history.append({

            "role":
                "user",

            "content":
                history_message

        })


        chat_history.append({

            "role":
                "assistant",

            "content":
                reply

        })


        request.session[
            "healthcare_chat_history"
        ] = chat_history[-10:]


        request.session.modified = True


        return JsonResponse({

            "success":
                True,

            "reply":
                reply

        })


    except Exception as e:

        print(
            "Healthcare Gemini Error:",
            e
        )

        error_text = str(e).lower()

        if (
            "503" in error_text
            or "unavailable" in error_text
            or "high demand" in error_text
            or "overloaded" in error_text
            or "temporarily" in error_text
        ):
            user_error = (
                "Healthcare AI is temporarily busy. "
                "Please try again in a few seconds."
            )
            status_code = 503
        else:
            user_error = (
                "Healthcare AI is temporarily unavailable. "
                "Please try again."
            )
            status_code = 500

        return JsonResponse({
            "success": False,
            "error": user_error
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