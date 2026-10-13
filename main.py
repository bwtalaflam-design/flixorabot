import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "FLIXORA Bot is Running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

Thread(target=run).start()
# استبدل الكلمات التالية بالمعلومات الخاصة بك
TELEGRAM_TOKEN = "8891007374:AAEzt3qRpeiPwea7MlFFpOb4LaQrwkFKLac"
TMDB_API_KEY = "1e6cffbcef10a9bb0fff7d452fffe102"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# دالة للبحث عن الأفلام والمسلسلات باللغة العربية
def search_media(query):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&language=ar&query={query}"
    response = requests.get(url).json()
    return response.get('results', [])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = (
        "أهلاً بك في بوت **FLIXORA** الشامل 🎬\n\n"
        "البوت الآن مرتبط بأكبر مكتبة أفلام ومسلسلات عالمية!\n"
        "للبحث عن أي فيلم أو مسلسل، فقط **أرسل اسمه هنا في المحادثة**."
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_search(message):
    query = message.text
    results = search_media(query)

    if not results:
        bot.reply_to(message, "لم يتم العثور على نتائج بهذا الاسم. حاول كتابة الاسم بشكل أوضح.")
        return

    markup = InlineKeyboardMarkup()
    for item in results[:5]:  # عرض أول 5 نتائج مطابقة
        title = item.get('title') or item.get('name')
        media_type = "فيلم 🎬" if item.get('media_type') == 'movie' else "مسلسل 📺"
        media_id = item.get('id')
        m_type = item.get('media_type')
        
        if title and m_type in ['movie', 'tv']:
            markup.add(InlineKeyboardButton(f"{title} ({media_type})", callback_data=f"info_{m_type}_{media_id}"))

    bot.send_message(message.chat.id, f"نتائج البحث عن: *{query}*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def show_details(call):
    _, m_type, media_id = call.data.split("_")
    
    # جلب تفاصيل العمل المختار
    url = f"https://api.themoviedb.org/3/{m_type}/{media_id}?api_key={TMDB_API_KEY}&language=ar"
    data = requests.get(url).json()

    title = data.get('title') or data.get('name')
    overview = data.get('overview') or "لا يوجد ملخص متوفر باللغة العربية لهذا العمل."
    rating = data.get('vote_average', 'غير محدد')
    release_date = data.get('release_date') or data.get('first_air_date') or 'غير معروف'
    poster_path = data.get('poster_path')

    caption = (
        f"🎬 *{title}*\n\n"
        f"📅 **تاريخ الإصدار:** {release_date}\n"
        f"⭐️ **التقييم:** {rating}/10\n\n"
        f"📖 **الملخص والقصة:**\n{overview}"
    )

    if poster_path:
        photo_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        bot.send_photo(call.message.chat.id, photo_url, caption=caption, parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, caption, parse_mode="Markdown")

if __name__ == "__main__":
    print("FLIXORA Bot with TMDB API is starting...")
    bot.polling(none_stop=True)
