from django.db import models

# Create your models here.

class Skill(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    investment = models.CharField(max_length=100)
    materials = models.TextField()
    guide = models.TextField()
    name_hi = models.CharField(max_length=100, blank=True)
    description_hi = models.TextField(blank=True)
    guide_hi = models.TextField(blank=True)
    materials_hi = models.TextField(blank=True)

    name_mr = models.CharField(max_length=100, blank=True)
    description_mr = models.TextField(blank=True)
    guide_mr = models.TextField(blank=True)
    materials_mr = models.TextField(blank=True)
 
    def __str__(self):
        return self.name
class QuizQuestion(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=300)
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1,
        choices=[('a', 'Option A'), ('b', 'Option B'), ('c', 'Option C'), ('d', 'Option D')]
    )
    question_text_hi = models.CharField(max_length=300, blank=True)
    option_a_hi = models.CharField(max_length=200, blank=True)
    option_b_hi = models.CharField(max_length=200, blank=True)
    option_c_hi = models.CharField(max_length=200, blank=True)
    option_d_hi = models.CharField(max_length=200, blank=True)
    question_text_mr = models.CharField(max_length=300, blank=True)
    option_a_mr = models.CharField(max_length=200, blank=True)
    option_b_mr = models.CharField(max_length=200, blank=True)
    option_c_mr = models.CharField(max_length=200, blank=True)
    option_d_mr = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.question_text

class LearningStage(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='stages')
    stage_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(max_length=500, blank=True)
    video_url = models.URLField(max_length=500, blank=True)
    title_hi = models.CharField(max_length=200, blank=True)
    description_hi = models.TextField(blank=True)

    title_mr = models.CharField(max_length=200, blank=True)
    description_mr = models.TextField(blank=True)

    class Meta:
        ordering = ['stage_number']

    def __str__(self):
        return f"{self.skill.name} - Stage {self.stage_number}: {self.title}"

class BusinessIdea(models.Model):
    title = models.CharField(max_length=200)
    related_skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name='business_ideas')
    description = models.TextField()
    investment = models.CharField(max_length=100)
    time_required = models.CharField(max_length=100)
    profit_potential = models.CharField(max_length=50)
    where_to_sell = models.TextField()
    image_url = models.URLField(max_length=500, blank=True)
    title_hi = models.CharField(max_length=200, blank=True)
    description_hi = models.TextField(blank=True)
    where_to_sell_hi = models.TextField(blank=True)

    title_mr = models.CharField(max_length=200, blank=True)
    description_mr = models.TextField(blank=True)
    where_to_sell_mr = models.TextField(blank=True)
    video_url = models.URLField(max_length=500, blank=True)

class FinancialTip(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="💰")

    title_hi = models.CharField(max_length=200, blank=True)
    description_hi = models.TextField(blank=True)

    title_mr = models.CharField(max_length=200, blank=True)
    description_mr = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    video_url = models.URLField(max_length=500, blank=True)
    def __str__(self):
        return self.title


class SellingTip(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=10, default="🛍")

    title_hi = models.CharField(max_length=200, blank=True)
    description_hi = models.TextField(blank=True)

    title_mr = models.CharField(max_length=200, blank=True)
    description_mr = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    video_url = models.URLField(max_length=500, blank=True)
    def __str__(self):
        return self.title
