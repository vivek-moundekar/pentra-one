import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udaan.settings')
django.setup()

from women_skills.models import Skill, BusinessIdea

def add_business(title, skill_name, desc, investment, time_req, profit, where):
    skill = Skill.objects.get(name=skill_name)
    BusinessIdea.objects.create(
        title=title,
        related_skill=skill,
        description=desc,
        investment=investment,
        time_required=time_req,
        profit_potential=profit,
        where_to_sell=where
    )

add_business(
    "Tailoring Business", "Tailoring",
    "Start a small stitching business from home, taking orders for clothes, alterations and custom designs from your local community.",
    "₹5000 - ₹10000", "2-4 weeks to start", "Medium to High",
    "Local shops, word of mouth, WhatsApp groups, local markets"
)

add_business(
    "Papad & Pickle Business", "Papad & Pickle",
    "Make and sell homemade papad and pickles using traditional family recipes. A low-investment business with steady local demand.",
    "₹1000 - ₹3000", "1 week to start", "Medium",
    "Local shops, Self Help Groups, weekly markets, WhatsApp"
)

add_business(
    "Candle Making Business", "Candle Making",
    "Create decorative and scented candles to sell as gifts, home decor items, or for festive occasions like Diwali and weddings.",
    "₹1500 - ₹4000", "1-2 weeks to start", "Medium to High",
    "Online pages, local markets, gift shops, festive stalls"
)

add_business(
    "Beauty & Mehendi Business", "Beauty & Mehendi",
    "Offer mehendi and basic beauty services at home or for events like weddings and festivals. Can grow into a full home-based salon.",
    "₹1000 - ₹5000", "2-3 weeks to start", "High",
    "Home visits, weddings, festivals, local events"
)

add_business(
    "Handmade Crafts Business", "Handmade Crafts",
    "Create and sell handmade jewelry, bags, and decorative items. Great for building a small brand through social media and exhibitions.",
    "₹500 - ₹2000", "1 week to start", "Medium",
    "Local exhibitions, WhatsApp, Instagram, gift shops"
)

add_business(
    "Soap Making Business", "Soap Making",
    "Make herbal, natural soaps using ingredients like neem, turmeric and rose. A growing market for organic skincare products.",
    "₹1000 - ₹3000", "1-2 weeks to start", "Medium to High",
    "Local markets, online pages, health/organic stores"
)

print("✅ All business ideas added successfully!")