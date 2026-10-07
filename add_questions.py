import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udaan.settings')
django.setup()

from women_skills.models import Skill, QuizQuestion

def add_question(skill_name, question_text, a, b, c, d, correct):
    skill = Skill.objects.get(name=skill_name)
    QuizQuestion.objects.create(
        skill=skill,
        question_text=question_text,
        option_a=a,
        option_b=b,
        option_c=c,
        option_d=d,
        correct_option=correct
    )

# ---------- Papad & Pickle ----------
add_question("Papad & Pickle", "What is mainly used to make papad?", "Flour", "Cement", "Plastic", "Glass", "a")
add_question("Papad & Pickle", "Why is packaging important for papad and pickle?", "It looks nice only", "It keeps the product fresh and sellable", "It is not important", "It increases weight", "b")
add_question("Papad & Pickle", "Where can papad and pickle be sold?", "Local shops and Self Help Groups", "Only online in other countries", "Nowhere", "Only to family", "a")
add_question("Papad & Pickle", "What should you do before selling a new pickle recipe?", "Sell immediately without testing", "Test the recipe first", "Skip taste testing", "Add more oil only", "b")
add_question("Papad & Pickle", "Which of these is an ingredient commonly used in pickles?", "Spices", "Nails", "Wood", "Paint", "a")

# ---------- Candle Making ----------
add_question("Candle Making", "What is the main material used to make a candle?", "Wax", "Sand", "Metal", "Glass", "a")
add_question("Candle Making", "What holds the candle upright and helps it burn?", "Wick", "Sticker", "Box", "Ribbon", "a")
add_question("Candle Making", "What can be added to give candles a nice smell?", "Fragrance oils", "Salt", "Sugar", "Vinegar", "a")
add_question("Candle Making", "What shape does the candle take from?", "Mold", "Bag", "Bottle cap only", "Spoon", "a")
add_question("Candle Making", "Where can handmade candles be sold?", "Online and local markets", "Nowhere", "Only in factories", "Only to shopkeepers", "a")

# ---------- Beauty & Mehendi ----------
add_question("Beauty & Mehendi", "What is used to create mehendi designs?", "Henna cone", "Paintbrush", "Marker", "Chalk", "a")
add_question("Beauty & Mehendi", "Which of these is a basic beauty service mentioned?", "Facials", "Plumbing", "Carpentry", "Farming", "a")
add_question("Beauty & Mehendi", "How can someone improve their mehendi skills?", "Practice designs regularly", "Never practice", "Avoid tutorials", "Stop after one try", "a")
add_question("Beauty & Mehendi", "Where can beauty and mehendi services be offered?", "At home and events", "Only in hospitals", "Only in schools", "Nowhere", "a")
add_question("Beauty & Mehendi", "What is needed to start a basic beauty kit?", "Makeup essentials", "Cooking utensils", "Gardening tools", "Car parts", "a")

# ---------- Handmade Crafts ----------
add_question("Handmade Crafts", "Which of these is a handmade craft item?", "Jewelry", "Cement bricks", "Tractor parts", "Glass windows", "a")
add_question("Handmade Crafts", "What is commonly used in handmade crafts?", "Beads and thread", "Steel rods", "Bricks", "Motor oil", "a")
add_question("Handmade Crafts", "How should craft products be presented for selling?", "Take good photos", "Hide them", "Never show them", "Sell without any photos", "a")
add_question("Handmade Crafts", "Where can handmade crafts be sold?", "Exhibitions and social media", "Nowhere", "Only in warehouses", "Only to strangers on the street", "a")
add_question("Handmade Crafts", "What should you create first before selling many items?", "Sample products", "Nothing, sell directly", "Only prices", "Only packaging", "a")

# ---------- Soap Making ----------
add_question("Soap Making", "What is the base material for making soap?", "Soap base", "Cement", "Sand", "Metal", "a")
add_question("Soap Making", "What can be added to soap for natural benefits?", "Neem, turmeric, rose", "Sand", "Plastic", "Nails", "a")
add_question("Soap Making", "What gives soap its shape?", "Mold", "Bottle cap", "Bag", "Spoon", "a")
add_question("Soap Making", "What must happen to the soap base before adding ingredients?", "It must be melted", "It must be frozen", "It must be burned", "It must be crushed", "a")
add_question("Soap Making", "Where can handmade soaps be sold?", "Locally and online", "Nowhere", "Only in factories", "Only to strangers", "a")

print("✅ All 25 questions added successfully!")
