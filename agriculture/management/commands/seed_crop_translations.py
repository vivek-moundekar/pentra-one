import json

from django.conf import settings
from django.core.management.base import BaseCommand

from agriculture.models import Crop, CropTranslation
from google import genai


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "pa": "Punjabi",
}


# ============================================================
# SHORT FARMER-FRIENDLY ENGLISH DATA
# ============================================================

CROP_DATA = {

    "Wheat": {
        "name": "Wheat",
        "description": (
            "A common Rabi food crop grown in cool weather."
        ),
        "season": "Rabi",
        "soil": (
            "Fertile, well-drained loamy soil."
        ),
        "water_requirement": (
            "Moderate irrigation. Water is important during root growth, flowering and grain filling."
        ),
        "sowing_time": (
            "Usually October to December."
        ),
        "harvesting_time": (
            "Usually March to April."
        ),
        "common_problems": (
            "Aphids, rust disease, weeds and moisture stress."
        ),
        "farmer_tip": (
            "Do not over-irrigate. Check the crop regularly for yellowing or rust spots."
        ),
    },


    "Rice": {
        "name": "Rice",
        "description": (
            "A major food crop that grows best in warm conditions with enough moisture."
        ),
        "season": "Kharif",
        "soil": (
            "Clay or clay-loam soil that can hold moisture."
        ),
        "water_requirement": (
            "Needs good moisture, especially during early growth and flowering."
        ),
        "sowing_time": (
            "Usually June to July."
        ),
        "harvesting_time": (
            "Usually September to November."
        ),
        "common_problems": (
            "Leaf pests, stem borers, weeds and fungal diseases."
        ),
        "farmer_tip": (
            "Check the field regularly and avoid unnecessary standing water."
        ),
    },


    "Cotton": {
        "name": "Cotton",
        "description": (
            "A warm-season fibre crop widely grown in India."
        ),
        "season": "Kharif",
        "soil": (
            "Deep, fertile and well-drained black soil is suitable."
        ),
        "water_requirement": (
            "Needs enough moisture but does not like prolonged waterlogging."
        ),
        "sowing_time": (
            "Usually June to July."
        ),
        "harvesting_time": (
            "Harvest begins after the bolls mature."
        ),
        "common_problems": (
            "Bollworms, sucking pests, weeds and leaf diseases."
        ),
        "farmer_tip": (
            "Inspect new leaves and flower buds often for insects."
        ),
    },


    "Soybean": {
        "name": "Soybean",
        "description": (
            "An important oilseed and pulse crop commonly grown in the monsoon."
        ),
        "season": "Kharif",
        "soil": (
            "Fertile, well-drained soil with good moisture retention."
        ),
        "water_requirement": (
            "Needs enough moisture during flowering and pod formation."
        ),
        "sowing_time": (
            "Usually June to July."
        ),
        "harvesting_time": (
            "Usually September to October."
        ),
        "common_problems": (
            "Leaf-eating insects, stem pests, weeds and fungal diseases."
        ),
        "farmer_tip": (
            "Avoid waterlogging and inspect the crop after heavy rain."
        ),
    },


    "Maize": {
        "name": "Maize",
        "description": (
            "A useful cereal crop grown for food, feed and industry."
        ),
        "season": "Kharif / Rabi / Summer",
        "soil": (
            "Fertile, well-drained loamy soil."
        ),
        "water_requirement": (
            "Needs regular moisture, especially during flowering and grain formation."
        ),
        "sowing_time": (
            "Depends on season; Kharif is usually June to July."
        ),
        "harvesting_time": (
            "Usually about 3 to 4 months after sowing."
        ),
        "common_problems": (
            "Fall armyworm, stem borer, weeds and leaf diseases."
        ),
        "farmer_tip": (
            "Check young leaves often for insect damage."
        ),
    },


    "Chickpea": {
        "name": "Chickpea",
        "description": (
            "A major pulse crop grown mainly in the cool Rabi season."
        ),
        "season": "Rabi",
        "soil": (
            "Well-drained loam to black soil."
        ),
        "water_requirement": (
            "Needs limited irrigation. Avoid excess water."
        ),
        "sowing_time": (
            "Usually October to November."
        ),
        "harvesting_time": (
            "Usually February to March."
        ),
        "common_problems": (
            "Pod borer, wilt, weeds and moisture stress."
        ),
        "farmer_tip": (
            "Do not give too much water and watch flowers for pod borers."
        ),
    },


    "Tomato": {
        "name": "Tomato",
        "description": (
            "A common vegetable crop grown for fresh and processed food."
        ),
        "season": "Rabi / Kharif / Summer",
        "soil": (
            "Fertile, well-drained sandy loam to loam soil."
        ),
        "water_requirement": (
            "Needs regular but balanced irrigation."
        ),
        "sowing_time": (
            "Depends on the region and season."
        ),
        "harvesting_time": (
            "Harvest when fruits reach the required maturity."
        ),
        "common_problems": (
            "Fruit borer, whitefly, leaf disease and cracking."
        ),
        "farmer_tip": (
            "Keep the field clean and avoid sudden changes in watering."
        ),
    },


    "Onion": {
        "name": "Onion",
        "description": (
            "An important vegetable and commercial crop grown in many parts of India."
        ),
        "season": "Rabi / Kharif",
        "soil": (
            "Loose, fertile and well-drained soil."
        ),
        "water_requirement": (
            "Needs regular but controlled irrigation."
        ),
        "sowing_time": (
            "Depends on the growing season and region."
        ),
        "harvesting_time": (
            "Harvest when bulbs mature and tops start falling."
        ),
        "common_problems": (
            "Thrips, fungal diseases, weeds and bulb rot."
        ),
        "farmer_tip": (
            "Avoid excess irrigation and keep weeds under control."
        ),
    },


    "Sugarcane": {
        "name": "Sugarcane",
        "description": (
            "A long-duration commercial crop mainly used for sugar."
        ),
        "season": "Annual / Seasonal",
        "soil": (
            "Deep, fertile soil with good drainage and moisture holding."
        ),
        "water_requirement": (
            "Needs regular water through the growing period."
        ),
        "sowing_time": (
            "Depends on region and planting season."
        ),
        "harvesting_time": (
            "Usually around 10 to 18 months, depending on region."
        ),
        "common_problems": (
            "Borers, termites, weeds and fungal diseases."
        ),
        "farmer_tip": (
            "Maintain proper moisture and inspect stems for borer damage."
        ),
    },


    "Groundnut": {
        "name": "Groundnut",
        "description": (
            "An important oilseed crop that grows well in warm conditions."
        ),
        "season": "Kharif / Summer",
        "soil": (
            "Loose, well-drained sandy loam to loam soil."
        ),
        "water_requirement": (
            "Needs enough moisture during flowering and pod development."
        ),
        "sowing_time": (
            "Usually June to July for Kharif."
        ),
        "harvesting_time": (
            "Harvest when pods are mature and well developed."
        ),
        "common_problems": (
            "Leaf spots, sucking pests, termites and weeds."
        ),
        "farmer_tip": (
            "Avoid waterlogging and check leaves for early disease spots."
        ),
    },

}


# ============================================================
# AI TRANSLATION PROMPT
# ============================================================

TRANSLATION_PROMPT = """
Translate this crop information into {language}.

This is for an Indian farmer.

IMPORTANT:

- Keep every answer short.
- Use very simple everyday language.
- Make it easy to understand quickly.
- Do not make the text formal or academic.
- Do not add new facts.
- Keep numbers, months and seasons correct.
- Keep the meaning practical.
- Each field should remain concise.

FIELD RULES:

description:
1 short sentence.

season:
Only the season.

soil:
1 short sentence.

water_requirement:
1 short sentence.

sowing_time:
1 short sentence.

harvesting_time:
1 short sentence.

common_problems:
Short list of 2-4 common problems.

farmer_tip:
1 short practical tip.

Return ONLY valid JSON.

Use exactly these keys:

name
description
season
soil
water_requirement
sowing_time
harvesting_time
common_problems
farmer_tip

English source:

{data}
"""


# ============================================================
# MANAGEMENT COMMAND
# ============================================================

class Command(BaseCommand):

    help = (
        "Create short and farmer-friendly "
        "crop translations for all supported languages."
    )


    # ========================================================
    # TRANSLATE ONE CROP
    # ========================================================

    def translate_crop(
        self,
        client,
        crop_name,
        data,
        language_name
    ):

        prompt = TRANSLATION_PROMPT.format(
            language=language_name,
            data=json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            )
        )


        models_to_try = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-flash-latest",
        ]


        last_error = None


        for model_name in models_to_try:

            try:

                self.stdout.write(
                    f"    {language_name}: "
                    f"{model_name}"
                )


                response = (
                    client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                )


                text = response.text.strip()


                if text.startswith("```json"):
                    text = text[7:]


                if text.startswith("```"):
                    text = text[3:]


                if text.endswith("```"):
                    text = text[:-3]


                text = text.strip()


                result = json.loads(text)


                required_fields = [

                    "name",
                    "description",
                    "season",
                    "soil",
                    "water_requirement",
                    "sowing_time",
                    "harvesting_time",
                    "common_problems",
                    "farmer_tip",

                ]


                for field in required_fields:

                    if field not in result:

                        raise ValueError(
                            f"Missing field: {field}"
                        )


                return result


            except Exception as error:

                last_error = error

                self.stdout.write(
                    self.style.WARNING(
                        f"    Failed: {error}"
                    )
                )


        raise RuntimeError(
            f"Translation failed for "
            f"{crop_name} -> {language_name}: "
            f"{last_error}"
        )


    # ========================================================
    # HANDLE
    # ========================================================

    def handle(
        self,
        *args,
        **kwargs
    ):

        api_key = getattr(
            settings,
            "GEMINI_API_KEY",
            None
        )


        if not api_key:

            self.stdout.write(
                self.style.ERROR(
                    "GEMINI_API_KEY is missing."
                )
            )

            return


        client = genai.Client(
            api_key=api_key
        )


        database_crops = {
            crop.name: crop
            for crop in Crop.objects.all()
        }


        created = 0
        updated = 0
        failed = 0


        # ====================================================
        # EVERY CROP
        # ====================================================

        for crop_name, english_data in CROP_DATA.items():

            crop = database_crops.get(
                crop_name
            )


            if not crop:

                self.stdout.write(
                    self.style.WARNING(
                        f"Crop not found: {crop_name}"
                    )
                )

                failed += 1

                continue


            self.stdout.write("")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Processing {crop_name}"
                )
            )


            # ------------------------------------------------
            # ENGLISH
            # ------------------------------------------------

            _, was_created = (
                CropTranslation.objects.update_or_create(
                    crop=crop,
                    language="en",
                    defaults={
                        "name":
                            english_data["name"],

                        "description":
                            english_data["description"],

                        "season":
                            english_data["season"],

                        "soil":
                            english_data["soil"],

                        "water_requirement":
                            english_data[
                                "water_requirement"
                            ],

                        "sowing_time":
                            english_data[
                                "sowing_time"
                            ],

                        "harvesting_time":
                            english_data[
                                "harvesting_time"
                            ],

                        "common_problems":
                            english_data[
                                "common_problems"
                            ],

                        "farmer_tip":
                            english_data[
                                "farmer_tip"
                            ],
                    }
                )
            )


            if was_created:
                created += 1
            else:
                updated += 1


            self.stdout.write(
                "  English: saved"
            )


            # ------------------------------------------------
            # OTHER LANGUAGES
            # ------------------------------------------------

            for language_code, language_name in (
                LANGUAGES.items()
            ):

                if language_code == "en":
                    continue


                try:

                    translated = self.translate_crop(
                        client,
                        crop_name,
                        english_data,
                        language_name
                    )


                    _, was_created = (
                        CropTranslation.objects.update_or_create(
                            crop=crop,
                            language=language_code,
                            defaults={
                                "name":
                                    translated["name"],

                                "description":
                                    translated[
                                        "description"
                                    ],

                                "season":
                                    translated[
                                        "season"
                                    ],

                                "soil":
                                    translated[
                                        "soil"
                                    ],

                                "water_requirement":
                                    translated[
                                        "water_requirement"
                                    ],

                                "sowing_time":
                                    translated[
                                        "sowing_time"
                                    ],

                                "harvesting_time":
                                    translated[
                                        "harvesting_time"
                                    ],

                                "common_problems":
                                    translated[
                                        "common_problems"
                                    ],

                                "farmer_tip":
                                    translated[
                                        "farmer_tip"
                                    ],
                            }
                        )
                    )


                    if was_created:
                        created += 1
                    else:
                        updated += 1


                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  {language_name}: saved"
                        )
                    )


                except Exception as error:

                    failed += 1

                    self.stdout.write(
                        self.style.ERROR(
                            f"  {language_name}: FAILED"
                        )
                    )

                    self.stdout.write(
                        str(error)
                    )


        # ====================================================
        # FINAL RESULT
        # ====================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "===================================="
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Crop translation completed."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated: {updated}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Failed/Skipped: {failed}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "===================================="
            )
        )