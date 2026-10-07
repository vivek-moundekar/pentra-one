import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udaan.settings')
django.setup()

from women_skills.models import Skill, LearningStage

def add_stage(skill_name, num, title, desc, image, video=""):
    skill = Skill.objects.get(name=skill_name)
    LearningStage.objects.create(
        skill=skill,
        stage_number=num,
        title=title,
        description=desc,
        image_url=image,
        video_url=video
    )

# ---------- Tailoring (Stage 3, 4, 5) ----------
add_stage("Tailoring", 3, "Taking Measurements",
    "Learn to measure chest, waist, hip, shoulder and length correctly using a measuring tape. Accurate measurements are the foundation of a well-fitted garment.",
    "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600")

add_stage("Tailoring", 4, "Making a Simple Product",
    "Start with an easy project like a cloth pouch or simple kurta. Cut the fabric using your measurements, pin the pieces together, and stitch step by step.",
    "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=600")

add_stage("Tailoring", 5, "Finishing & Selling",
    "Check your finished product for loose threads and even stitching. Price it based on material and time cost, then sell through local shops, WhatsApp or exhibitions.",
    "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600")

# ---------- Papad & Pickle ----------
add_stage("Papad & Pickle", 1, "Getting Started",
    "Gather ingredients like flour or urad dal, spices, oil and rolling equipment. Keep your kitchen clean and utensils ready before you begin.",
    "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600")

add_stage("Papad & Pickle", 2, "Preparing the Dough/Mixture",
    "Mix flour with water and spices to form a smooth dough or batter. Knead well for papad, or prepare the base mixture for pickles with oil and masala.",
    "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600",
    "https://www.youtube.com/embed/m3cdFo4yyDw")

add_stage("Papad & Pickle", 3, "Shaping and Drying",
    "Roll out small portions into thin round papads and place them to sun-dry for 2-3 days. For pickles, cut vegetables/fruits and mix with spices and oil, then store in jars.",
    "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600")

add_stage("Papad & Pickle", 4, "Quality Check & Packaging",
    "Make sure papads are completely dry with no moisture before storing, and pickles are properly mixed with oil to prevent spoiling. Pack in clean, sealed containers.",
    "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600")

add_stage("Papad & Pickle", 5, "Selling",
    "Start by selling to neighbors and local shops. Use word of mouth, WhatsApp groups and Self Help Group networks to grow your customer base.",
    "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600")

# ---------- Candle Making ----------
add_stage("Candle Making", 1, "Getting Started",
    "Collect wax, wicks, a melting pot, molds or containers, and fragrance oils. Set up your work area on a heat-safe surface, away from children.",
    "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?w=600")

add_stage("Candle Making", 2, "Melting the Wax",
    "Melt wax slowly using a double-boiler method (a pot inside a pot of hot water) until fully liquid. Never melt wax directly on high flame.",
    "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?w=600",
    "https://www.youtube.com/embed/ocLS5hlUtJ0")

add_stage("Candle Making", 3, "Adding Color & Fragrance",
    "Once melted, mix in a small amount of color and a few drops of fragrance oil. Stir well so the color and scent are evenly spread through the wax.",
    "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?w=600")

add_stage("Candle Making", 4, "Pouring & Setting",
    "Center the wick in your mold or container, then carefully pour the wax in. Let it cool and harden undisturbed for a few hours before removing from the mold.",
    "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?w=600")

add_stage("Candle Making", 5, "Packaging & Selling",
    "Trim the wick, clean up the edges, and package attractively with labels. Sell as gifts, home decor items, or through local markets and online pages.",
    "https://images.unsplash.com/photo-1602874801007-bd458bb1b8b6?w=600")

# ---------- Beauty & Mehendi ----------
add_stage("Beauty & Mehendi", 1, "Getting Started",
    "Get henna cones (ready-made or prepare your own paste), and basic beauty tools like cotton, facial kits and threading tools. Practice on paper before trying on skin.",
    "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=600")

add_stage("Beauty & Mehendi", 2, "Basic Mehendi Patterns",
    "Start with simple shapes like dots, lines, flowers and leaves. Practice holding the cone at a steady angle for smooth, even lines.",
    "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=600",
    "https://www.youtube.com/embed/mMjnZRU1qPc")

add_stage("Beauty & Mehendi", 3, "Basic Beauty Techniques",
    "Learn simple beauty services like eyebrow threading and basic facials using safe, hygienic tools and products suited for different skin types.",
    "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=600")

add_stage("Beauty & Mehendi", 4, "Building Your Kit",
    "Slowly build a basic kit with henna cones, threading tools, and beauty essentials. Keep everything clean and organized for hygienic service.",
    "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=600")

add_stage("Beauty & Mehendi", 5, "Offering Services",
    "Offer your services to neighbors, at festivals, weddings and local events. Word of mouth and good quality work will help you build a loyal customer base.",
    "https://images.unsplash.com/photo-1583391733956-6c78276477e2?w=600")

# ---------- Handmade Crafts ----------
add_stage("Handmade Crafts", 1, "Getting Started",
    "Gather basic materials like beads, thread, glue, decorative paper and fabric scraps. Choose one simple item to start with, like a bracelet or paper gift box.",
    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600")

add_stage("Handmade Crafts", 2, "Basic Techniques",
    "Learn basic stringing, knotting and gluing techniques used in most handmade crafts. Practice with simple bead patterns before moving to complex designs.",
    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600",
    "https://www.youtube.com/embed/yFaCV_Uu-1g")

add_stage("Handmade Crafts", 3, "Creating Sample Products",
    "Make a few sample pieces to test your technique and finish quality. Use these samples to show customers what you can create.",
    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600")

add_stage("Handmade Crafts", 4, "Presentation & Photography",
    "Take clear, well-lit photos of your finished crafts against a simple background. Good photos make a big difference when selling online or on WhatsApp.",
    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600")

add_stage("Handmade Crafts", 5, "Selling",
    "Sell through local exhibitions, WhatsApp status, Instagram, or word of mouth. Start with friends and family, then expand to a wider audience.",
    "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600")

# ---------- Soap Making ----------
add_stage("Soap Making", 1, "Getting Started",
    "Gather a melt-and-pour soap base, essential oils, molds and natural additives like neem, turmeric or rose. Set up on a clean, heat-safe surface.",
    "https://images.unsplash.com/photo-1600857062241-98e5dba7f214?w=600")

add_stage("Soap Making", 2, "Melting the Soap Base",
    "Cut the soap base into cubes and melt gently using a double-boiler or microwave in short bursts, stirring often. Avoid overheating.",
    "https://images.unsplash.com/photo-1600857062241-98e5dba7f214?w=600",
    "https://www.youtube.com/embed/S6x_dEm5QQc")

add_stage("Soap Making", 3, "Adding Natural Ingredients",
    "Mix in natural additives like neem powder, turmeric or rose extract along with a few drops of essential oil for fragrance and skin benefits.",
    "https://images.unsplash.com/photo-1600857062241-98e5dba7f214?w=600")

add_stage("Soap Making", 4, "Pouring & Setting",
    "Pour the mixture into soap molds and let it cool and harden completely, usually for a few hours, before removing from the mold.",
    "https://images.unsplash.com/photo-1600857062241-98e5dba7f214?w=600")

add_stage("Soap Making", 5, "Packaging & Selling",
    "Wrap the finished soaps neatly with labels mentioning ingredients. Sell locally, at exhibitions, or online as natural, handmade skincare products.",
    "https://images.unsplash.com/photo-1600857062241-98e5dba7f214?w=600")

print("✅ All learning stages added successfully!")