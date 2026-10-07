import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udaan.settings')
django.setup()

from women_skills.models import FinancialTip, SellingTip

def add_financial(title, desc, icon, title_hi, desc_hi, title_mr, desc_mr):
    FinancialTip.objects.create(
        title=title, description=desc, icon=icon,
        title_hi=title_hi, description_hi=desc_hi,
        title_mr=title_mr, description_mr=desc_mr
    )

def add_selling(title, desc, icon, title_hi, desc_hi, title_mr, desc_mr):
    SellingTip.objects.create(
        title=title, description=desc, icon=icon,
        title_hi=title_hi, description_hi=desc_hi,
        title_mr=title_mr, description_mr=desc_mr
    )

# ---------- Financial Literacy ----------
add_financial(
    "Why Save Money?", "Saving even a small amount regularly helps you handle emergencies and grow your business over time.", "🐷",
    "पैसे क्यों बचाएं?", "थोड़ी-थोड़ी बचत भी नियमित रूप से करने से आप आपातकाल संभाल पाएंगी और व्यवसाय बढ़ा पाएंगी।",
    "पैसे का बचत का करा?", "थोडी थोडी नियमित बचत केल्याने तुम्ही आणीबाणी सांभाळू शकाल आणि व्यवसाय वाढवू शकाल."
)
add_financial(
    "How to Open a Bank Account", "Visit your nearest bank with an ID proof and address proof. Many banks offer free basic savings accounts for women.", "🏦",
    "बैंक खाता कैसे खोलें", "अपने पास के बैंक में पहचान पत्र और पते के प्रमाण के साथ जाएं। कई बैंक महिलाओं के लिए मुफ्त खाता देते हैं।",
    "बँक खाते कसे उघडावे", "तुमच्या जवळच्या बँकेत ओळखपत्र आणि पत्ता पुरावा घेऊन जा. अनेक बँका महिलांसाठी मोफत खाते देतात."
)
add_financial(
    "What is UPI?", "UPI lets you send and receive money instantly using your phone, without needing cash. It's free and safe to use.", "📱",
    "UPI क्या है?", "UPI से आप फोन से बिना नकद के तुरंत पैसे भेज और पा सकती हैं। यह मुफ्त और सुरक्षित है।",
    "UPI म्हणजे काय?", "UPI मुळे तुम्ही फोनवरून रोख न वापरता लगेच पैसे पाठवू आणि मिळवू शकता. हे मोफत आणि सुरक्षित आहे."
)
add_financial(
    "Avoiding Online Scams", "Never share your OTP, PIN, or password with anyone, even if they claim to be from the bank. Banks never ask for these.", "🔒",
    "ऑनलाइन धोखाधड़ी से बचें", "अपना OTP, PIN या पासवर्ड किसी को न बताएं, भले ही वे बैंक से होने का दावा करें। बैंक कभी नहीं मांगते।",
    "ऑनलाइन फसवणुकीपासून वाचा", "तुमचा OTP, PIN किंवा पासवर्ड कोणालाही सांगू नका, जरी ते बँकेतून असल्याचा दावा करत असतील."
)
add_financial(
    "Simple Budget Planning", "Divide your income into three parts: daily needs, savings, and business investment. Track it in a small notebook.", "📝",
    "आसान बजट योजना", "अपनी आय को तीन भागों में बांटें: रोज़मर्रा की ज़रूरतें, बचत, और व्यवसाय निवेश। एक छोटी नोटबुक में लिखें।",
    "सोपे अंदाजपत्रक", "तुमचे उत्पन्न तीन भागांत विभागा: रोजच्या गरजा, बचत, आणि व्यवसाय गुंतवणूक. एका छोट्या वहीत नोंद ठेवा."
)

# ---------- Selling Tips ----------
add_selling(
    "Using WhatsApp Business", "Create a free WhatsApp Business account to showcase your products with photos, prices, and easy ordering.", "💬",
    "व्हाट्सएप बिज़नेस का उपयोग", "अपने प्रोडक्ट फोटो, कीमत के साथ दिखाने के लिए मुफ्त व्हाट्सएप बिज़नेस अकाउंट बनाएं।",
    "व्हॉट्सअॅप बिझनेस वापरणे", "तुमची उत्पादने फोटो आणि किमतीसह दाखवण्यासाठी मोफत व्हॉट्सअॅप बिझनेस खाते तयार करा."
)
add_selling(
    "Selling at Local Markets", "Weekly local markets (haat/bazaar) are a great way to reach customers directly and get instant feedback.", "🏪",
    "स्थानीय बाज़ार में बेचना", "साप्ताहिक बाज़ार ग्राहकों तक सीधे पहुंचने और तुरंत प्रतिक्रिया पाने का अच्छा तरीका है।",
    "स्थानिक बाजारात विक्री", "साप्ताहिक बाजार थेट ग्राहकांपर्यंत पोहोचण्याचा आणि लगेच प्रतिक्रिया मिळवण्याचा चांगला मार्ग आहे."
)
add_selling(
    "Taking Good Product Photos", "Use natural daylight, a plain background, and take photos from multiple angles to attract more buyers.", "📸",
    "अच्छी प्रोडक्ट फोटो लेना", "प्राकृतिक रोशनी, सादा background, और कई एंगल से फोटो लें ताकि ज़्यादा ग्राहक आकर्षित हों।",
    "चांगले उत्पादन फोटो काढणे", "नैसर्गिक प्रकाश, साधी पार्श्वभूमी आणि अनेक कोनातून फोटो काढा जेणेकरून अधिक ग्राहक आकर्षित होतील."
)
add_selling(
    "Talking to Customers", "Be polite, answer questions clearly, and always follow up after a sale to build trust and repeat customers.", "🗣",
    "ग्राहकों से बात करना", "विनम्र रहें, सवालों के स्पष्ट जवाब दें, और बिक्री के बाद फॉलो-अप करें ताकि भरोसा बने।",
    "ग्राहकांशी बोलणे", "नम्र रहा, प्रश्नांची स्पष्ट उत्तरे द्या, आणि विक्रीनंतर पाठपुरावा करा जेणेकरून विश्वास निर्माण होईल."
)
add_selling(
    "Receiving Payments Safely", "Use UPI apps like PhonePe or Google Pay for safe, instant payments. Always confirm payment before handing over goods.", "💳",
    "सुरक्षित भुगतान लेना", "सुरक्षित, तुरंत भुगतान के लिए PhonePe या Google Pay जैसे UPI ऐप का उपयोग करें। सामान देने से पहले भुगतान की पुष्टि करें।",
    "सुरक्षित पेमेंट घेणे", "सुरक्षित, त्वरित पेमेंटसाठी PhonePe किंवा Google Pay सारखे UPI अॅप वापरा. वस्तू देण्यापूर्वी पेमेंटची खात्री करा."
)

print("✅ All tips added successfully!")