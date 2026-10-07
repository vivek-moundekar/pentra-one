import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udaan.settings')
django.setup()

from women_skills.models import BusinessIdea

def update_image(title, image_url):
    idea = BusinessIdea.objects.get(title=title)
    idea.image_url = image_url
    idea.save()

update_image("Tailoring Business",
    "https://images.pexels.com/photos/18652118/pexels-photo-18652118.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_image("Papad & Pickle Business",
    "https://images.pexels.com/photos/8978859/pexels-photo-8978859.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_image("Candle Making Business",
    "https://images.pexels.com/photos/7233940/pexels-photo-7233940.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_image("Beauty & Mehendi Business",
    "https://images.pexels.com/photos/2643557/pexels-photo-2643557.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_image("Handmade Crafts Business",
    "https://images.pexels.com/photos/6957322/pexels-photo-6957322.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_image("Soap Making Business",
    "https://images.pexels.com/photos/16244099/pexels-photo-16244099.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

print("✅ All business images updated successfully!")