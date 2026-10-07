from django.db import models


class GovernmentScheme(models.Model):

    CATEGORY_CHOICES = [
        ('Agriculture', 'Agriculture'),
        ('Education', 'Education'),
        ('Women & Child', 'Women & Child'),
        ('Employment', 'Employment'),
        ('Housing', 'Housing'),
        ('Health', 'Health'),
        ('Financial Assistance', 'Financial Assistance'),
        ('Social Welfare', 'Social Welfare'),
    ]

    name = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES
    )

    # English Content
    short_description = models.TextField()
    full_description = models.TextField()
    benefits = models.TextField()
    eligibility = models.TextField()
    documents_required = models.TextField()
    application_process = models.TextField()

    implementing_department = models.CharField(max_length=200)

    state = models.CharField(max_length=100)

    official_url = models.URLField(blank=True)

    helpline = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
# Create your models here.
