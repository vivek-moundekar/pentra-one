import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udaan.settings')
django.setup()

from women_skills.models import BusinessIdea, FinancialTip, SellingTip

def update_biz_video(title, video_url):
    b = BusinessIdea.objects.get(title=title)
    b.video_url = video_url
    b.save()

def update_fin_video(title, video_url):
    f = FinancialTip.objects.get(title=title)
    f.video_url = video_url
    f.save()

def update_sell_video(title, video_url):
    s = SellingTip.objects.get(title=title)
    s.video_url = video_url
    s.save()

# ---------- Business Ideas ----------
update_biz_video("Tailoring Business", "https://www.youtube.com/embed/QhZTc1x1-pM")
update_biz_video("Papad & Pickle Business", "https://www.youtube.com/embed/m3cdFo4yyDw")
update_biz_video("Candle Making Business", "https://www.youtube.com/embed/ocLS5hlUtJ0")
update_biz_video("Beauty & Mehendi Business", "https://www.youtube.com/embed/mMjnZRU1qPc")
update_biz_video("Handmade Crafts Business", "https://www.youtube.com/embed/yFaCV_Uu-1g")
update_biz_video("Soap Making Business", "https://www.youtube.com/embed/S6x_dEm5QQc")

# ---------- Financial Literacy (all 5 done) ----------
update_fin_video("Why Save Money?", "https://www.youtube.com/embed/_jrUzpd-WPg")
update_fin_video("How to Open a Bank Account", "https://www.youtube.com/embed/FTCiizTx_fw")
update_fin_video("What is UPI?", "https://www.youtube.com/embed/r7qMf8t9PSc")
update_fin_video("Avoiding Online Scams", "https://www.youtube.com/embed/Y8z67bi1i2A")
update_fin_video("Simple Budget Planning", "https://www.youtube.com/embed/M7ucIl9MGs0")

# ---------- Selling Tips (1 of 5 found) ----------
update_sell_video("Using WhatsApp Business", "https://www.youtube.com/embed/7a1AXiAmSB0")

print("✅ Videos added: 6 Business Ideas, 5 Financial Literacy, 1 Selling Tip!")