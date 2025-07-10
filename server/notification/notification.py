from telegram import Update, Bot, InputMediaPhoto
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters,CommandHandler
import tempfile
import cv2
import os

TOKEN = "8057292272:AAEOITnwJa32XARBIOffikKQeszvDVCs2m0"
IDS_FILE = "server/notification/ips.dat"


def load_chat_ids():
    if not os.path.exists(IDS_FILE):
        return set()
    with open(IDS_FILE, "r") as f:
        return set(map(int, map(str.strip, f.readlines())))

def save_chat_id(chat_id):
    with open(IDS_FILE, "a") as f:
        f.write(f"{chat_id}\n")

active_chats = load_chat_ids()

async def save_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in active_chats:
        active_chats.add(chat_id)
        save_chat_id(chat_id)
        print(f"New chat_id: {chat_id}")
        await update.message.reply_text(f"chat_id saved: {chat_id}")
    else:
        await update.message.reply_text(f"{chat_id}")


def save_cv_image(img):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    cv2.imwrite(f.name, img)
    return f.name

async def send_telegram_notifification(header, text, img1, img2):
    bot = Bot(token=TOKEN)
    active_chats = load_chat_ids() 
    
    img1_path = save_cv_image(img1)
    img2_path = save_cv_image(img2)

    print("starting the notification handler...")
    print("Chat IDs:", active_chats)

    media = [
        InputMediaPhoto(media=open(img1_path, "rb"), caption=f"<b>{header}</b>\n{text}", parse_mode="HTML"),
        InputMediaPhoto(media=open(img2_path, "rb"))
    ]

    for chat_id in active_chats:
        try:
            bot.send_media_group(chat_id=chat_id, media=media)
            print(f"Sent {chat_id}")
        except Exception as e:
            print(f"ERROR {chat_id}: {e}")
    await bot.send_media_group(chat_id=chat_id, media=media)

if __name__ == "__main__":
    print("Bot started...")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", save_chat))  # только /start
    app.run_polling()