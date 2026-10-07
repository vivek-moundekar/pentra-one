from django.shortcuts import render
from .models import Skill, BusinessIdea, FinancialTip, SellingTip

def skill_list(request):
    skills = Skill.objects.all()
    return render(request, 'women_skills/skills.html', {'skills': skills})
from .models import BusinessIdea

def business_ideas(request):
    ideas = BusinessIdea.objects.all()
    return render(request, 'women_skills/business.html', {'ideas': ideas})
def women_home(request):
    return render(request, 'women_skills/home.html')
def financial_literacy(request):
    tips = FinancialTip.objects.all()
    return render(request, 'women_skills/financial.html', {'tips': tips})

def selling_tips(request):
    tips = SellingTip.objects.all()
    return render(request, 'women_skills/selling.html', {'tips': tips})

def my_progress(request):
    return render(request, 'women_skills/progress.html')
