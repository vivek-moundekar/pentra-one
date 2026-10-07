import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udaan.settings')
django.setup()

from women_skills.models import FinancialTip, SellingTip

def update_fin_image(title, image_url):
    tip = FinancialTip.objects.get(title=title)
    tip.image_url = image_url
    tip.save()

def update_sell_image(title, image_url):
    tip = SellingTip.objects.get(title=title)
    tip.image_url = image_url
    tip.save()

# ---------- Financial Literacy ----------
update_fin_image("Why Save Money?",
    "https://images.pexels.com/photos/3943715/pexels-photo-3943715.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_fin_image("How to Open a Bank Account",
    "https://images.pexels.com/photos/6969954/pexels-photo-6969954.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_fin_image("What is UPI?",
    "https://images.pexels.com/photos/4226272/pexels-photo-4226272.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_fin_image("Avoiding Online Scams",
    "https://images.pexels.com/photos/6353659/pexels-photo-6353659.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_fin_image("Simple Budget Planning",
    "https://images.pexels.com/photos/4386366/pexels-photo-4386366.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

# ---------- Selling Tips ----------
update_sell_image("Using WhatsApp Business",
    "https://images.pexels.com/photos/6812441/pexels-photo-6812441.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_sell_image("Selling at Local Markets",
    "https://images.pexels.com/photos/13103276/pexels-photo-13103276.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_sell_image("Taking Good Product Photos",
    "https://images.pexels.com/photos/370474/pexels-photo-370474.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_sell_image("Talking to Customers",
    "https://images.pexels.com/photos/30319868/pexels-photo-30319868.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

update_sell_image("Receiving Payments Safely",
    "https://images.pexels.com/photos/6237886/pexels-photo-6237886.jpeg?auto=compress&cs=tinysrgb&h=627&fit=crop&w=1200")

print("✅ All financial and selling images added successfully!")