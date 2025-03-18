import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Telegram bot tokeni
TOKEN = "7568083205:AAGxHE6AndtyCuUUC9Kg8NcKOu-l-IzFzmo"

# Google Sheets sozlamalari
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1O8dcoWEialwvr8x5YPDbyORvux8Ex3MAd0W81NDRJUs/edit?gid=0"

# Google Sheets uchun autentifikatsiya
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SPREADSHEET_URL).sheet1

# Logger sozlamalari
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Conversation bosqichlari
NAME, SURNAME, PHONE, CONFIRM = range(4)

user_data = {}

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Assalomu alaykum! Ismingizni kiriting:")
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    user_data["name"] = update.message.text
    update.message.reply_text("Familiyangizni kiriting:")
    return SURNAME

def get_surname(update: Update, context: CallbackContext) -> int:
    user_data["surname"] = update.message.text
    update.message.reply_text("Telefon raqamingizni kiriting (masalan, +998901234567):")
    return PHONE

def get_phone(update: Update, context: CallbackContext) -> int:
    phone = update.message.text
    if not phone.startswith("+998") or not phone[1:].isdigit() or len(phone) != 13:
        update.message.reply_text("❌ Noto‘g‘ri format! Iltimos, telefon raqamingizni +998XXXXXXXXX shaklida kiriting:")
        return PHONE

    user_data["phone"] = phone

    msg = f"Ma'lumotlaringiz to‘g‘rimi?\n\n👤 Ism: {user_data['name']}\n📝 Familiya: {user_data['surname']}\n📞 Telefon: {user_data['phone']}"
    keyboard = [["Ha", "Yo‘q"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    update.message.reply_text(msg, reply_markup=reply_markup)
    return CONFIRM

def confirm(update: Update, context: CallbackContext) -> int:
    if update.message.text == "Ha":
        sheet.append_row([user_data["name"], user_data["surname"], user_data["phone"]], table_range="C3:E3")
        update.message.reply_text("✅ Ma'lumotlaringiz saqlandi! Rahmat!")
        return ConversationHandler.END
    else:
        update.message.reply_text("🔄 Qayta boshlaymiz. Ismingizni kiriting:")
        return NAME

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("❌ Jarayon bekor qilindi.")
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            SURNAME: [MessageHandler(Filters.text & ~Filters.command, get_surname)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
            CONFIRM: [MessageHandler(Filters.text & ~Filters.command, confirm)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

import json
from oauth2client.service_account import ServiceAccountCredentials

json_data = '''{
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_KEY_HERE\\n-----END PRIVATE KEY-----\\n",
    "client_email": "your-service-account-email",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your-cert-url"
}'''

creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(json_data), scope)
