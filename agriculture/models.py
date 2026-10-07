from django.db import models


class Crop(models.Model):

    name = models.CharField(
        max_length=100
    )

    scientific_name = models.CharField(
        max_length=150,
        blank=True
    )

    description = models.TextField()

    season = models.CharField(
        max_length=100,
        blank=True
    )

    soil = models.TextField(
        blank=True
    )

    water_requirement = models.TextField(
        blank=True
    )

    sowing_time = models.CharField(
        max_length=150,
        blank=True
    )

    harvesting_time = models.CharField(
        max_length=150,
        blank=True
    )

    common_problems = models.TextField(
        blank=True,
        help_text="Short common pests, diseases or problems."
    )

    farmer_tip = models.TextField(
        blank=True,
        help_text="One short practical tip for farmers."
    )

    image = models.ImageField(
        upload_to="crops/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        ordering = ["name"]


    def __str__(self):

        return self.name


class CropTranslation(models.Model):

    LANGUAGE_CHOICES = [

        ("en", "English"),
        ("hi", "Hindi"),
        ("mr", "Marathi"),
        ("gu", "Gujarati"),
        ("bn", "Bengali"),
        ("ta", "Tamil"),
        ("te", "Telugu"),
        ("kn", "Kannada"),
        ("pa", "Punjabi"),

    ]


    crop = models.ForeignKey(
        Crop,
        on_delete=models.CASCADE,
        related_name="translations"
    )

    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    season = models.CharField(
        max_length=150,
        blank=True
    )

    soil = models.TextField(
        blank=True
    )

    water_requirement = models.TextField(
        blank=True
    )

    sowing_time = models.CharField(
        max_length=200,
        blank=True
    )

    harvesting_time = models.CharField(
        max_length=200,
        blank=True
    )

    common_problems = models.TextField(
        blank=True
    )

    farmer_tip = models.TextField(
        blank=True
    )


    class Meta:

        ordering = [
            "crop__name",
            "language"
        ]

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "crop",
                    "language"
                ],
                name="unique_crop_language"
            )

        ]


    def __str__(self):

        return (
            f"{self.crop.name} - "
            f"{self.get_language_display()}"
        )