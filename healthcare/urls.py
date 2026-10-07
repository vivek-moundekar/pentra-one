from django.urls import path
from . import views

urlpatterns = [
    path('', views.healthcare_home, name='healthcare_home'),

    path('chatbot/', views.healthcare_chatbot, name='healthcare_chatbot'),
    path('chatbot/send/', views.healthcare_chatbot_send, name='healthcare_chatbot_send'),

    path('womens-health/', views.womens_health, name='womens_health'),
    path(
    'disability-care/',
    views.disability_care,
    name='disability_care'),
    path('general-health/', views.general_health, name='general_health'),
    path('menstrual-health/', views.menstrual_health, name='menstrual_health'),
    path('pregnancy-health/', views.pregnancy_health, name='pregnancy_health'),
    path('nutrition-anemia/', views.nutrition_anemia, name='nutrition_anemia'),
    path('pcos-hormonal/', views.pcos_hormonal, name='pcos_hormonal'),
    path('breast-cervical/', views.breast_cervical, name='breast_cervical'),
    path('mental-emotional-health/', views.mental_emotional_health, name='mental_emotional_health'),
    path('reproductive-sexual-health/', views.reproductive_sexual_health, name='reproductive_sexual_health'),
    path(
    'women-health-across-ages/',
    views.women_health_across_ages,
    name='women_health_across_ages'),
    path(
    'women-health-insights/',
    views.women_health_insights,
    name='women_health_insights'),
    path(
    'health-awareness/',
    views.health_awareness,
    name='health_awareness'),
    path(
    'healthy-diet-nutrition/',
    views.healthy_diet_nutrition,
    name='healthy_diet_nutrition'),
    path(
    'hygiene-sanitation/',
    views.hygiene_sanitation,
    name='hygiene_sanitation'),
    path(
    'vaccination-immunization/',
    views.vaccination_immunization,
    name='vaccination_immunization'),
    path(
    'common-diseases-prevention/',
    views.common_diseases_prevention,
    name='common_diseases_prevention'),
    path(
    'preventive-healthcare/',
    views.preventive_healthcare,
    name='preventive_healthcare'),
    path(
    'maternal-child-health/',
    views.maternal_child_health,
    name='maternal_child_health'),
    path(
    'healthy-lifestyle/',
    views.healthy_lifestyle,
    name='healthy_lifestyle'),
    path(
    'mental-health-all-ages/',
    views.mental_health_all_ages,
    name='mental_health_all_ages'),
    path(
    'emergency-first-aid/',
    views.emergency_first_aid,
    name='emergency_first_aid'),
    path(
    'nearby-healthcare/',
    views.nearby_healthcare,
    name='nearby_healthcare'),
    path(
    'nearby-healthcare/search/',
    views.nearby_healthcare_search,
    name='nearby_healthcare_search'),
    path(
    'health-report-ocr/',
    views.health_report_ocr,
    name='health_report_ocr'),
    path(
    'health-report-ocr/analyze/',
    views.analyze_health_report,
    name='analyze_health_report'),
    path(
    'health-report-ocr/save/',
    views.save_health_report,
    name='save_health_report'),
    path(
    'previous-health-reports/',
    views.previous_health_reports,
    name='previous_health_reports'),
    path(
    'delete-health-report/<int:report_id>/',
    views.delete_health_report,
    name='delete_health_report'),
    path(
    'emergency-helpline/',
    views.emergency_helpline,
    name='emergency_helpline'),
    path(
    'disability-awareness/',
    views.disability_awareness,
    name='disability_awareness'),
    path(
    'daily-care-safety/',
    views.daily_care_safety,
    name='daily_care_safety'),
    path(
    'mental-emotional-support/',
    views.mental_emotional_support,
    name='mental_emotional_support'),
    path(
    'accessibility-assistive-devices/',
    views.accessibility_assistive_devices,
    name='accessibility_assistive_devices'),
    path(
    'healthcare-rehabilitation/',
    views.healthcare_rehabilitation,
    name='healthcare_rehabilitation'),
    path(
    'government-schemes-support/',
    views.government_schemes_support,
    name='government_schemes_support'),
    


]