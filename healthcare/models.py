from django.db import models


class HealthReport(models.Model):
    patient_name = models.CharField(
        max_length=255,
        blank=True
    )

    report_type = models.CharField(
        max_length=100,
        blank=True
    )

    report_date = models.DateField(
        null=True,
        blank=True
    )

    extracted_information = models.TextField()

    explanation = models.TextField(
        blank=True
    )

    report_image = models.FileField(
        upload_to='health_reports/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.patient_name or 'Health Report'} - {self.created_at.strftime('%d-%m-%Y')}"