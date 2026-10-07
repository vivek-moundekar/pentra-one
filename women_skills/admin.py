from django.contrib import admin
from .models import Skill, QuizQuestion, LearningStage, BusinessIdea, FinancialTip, SellingTip

admin.site.register(Skill)
admin.site.register(QuizQuestion)
admin.site.register(LearningStage)
admin.site.register(BusinessIdea)
admin.site.register(FinancialTip)
admin.site.register(SellingTip)