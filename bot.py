import os
import telebot
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

@bot.message_handler(commands=["start"])
def start(msg):
    chat = msg.chat.id
    user_data[chat] = {"step": "ask_count"}
    bot.send_message(chat, "👋 স্বাগতম! কতটি পণ্য রসিদে থাকবে?")

@bot.message_handler(func=lambda m: m.chat.id in user_data)
def handle(m):
    chat = m.chat.id
    state = user_data[chat]
    text = m.text.strip()

    if state["step"] == "ask_count":
        try:
            cnt = int(text)
            state.update({"count": cnt, "products": [], "idx": 0})
            state["step"] = "ask_name"
            bot.send_message(chat, f"📝 পণ্যের নাম লিখুন #1")
        except:
            bot.send_message(chat, "সঠিক সংখ্যা লিখুন, যেমন: ৩")

    elif state["step"] == "ask_name":
        state["products"].append({"name": text})
        bot.send_message(chat, f"💰 দাম লিখুন #{state['idx']+1}")
        state["step"] = "ask_price"

    elif state["step"] == "ask_price":
        try:
            price = float(text)
            state["products"][state["idx"]]["price"] = price
            state["idx"] += 1
            if state["idx"] < state["count"]:
                state["step"] = "ask_name"
                bot.send_message(chat, f"📝 পণ্যের নাম লিখুন #{state['idx']+1}")
            else:
                bot.send_message(chat, "📄 রসিদ তৈরি করা হচ্ছে…")
                resp = requests.post(API_URL, json={"products": state["products"]})
                if resp.status_code == 200:
                    pdf = BytesIO(resp.content)
                    bot.send_document(chat, pdf, visible_file_name="receipt.pdf", caption="✅ এটি আপনার রসিদ।")
                else:
                    bot.send_message(chat, f"Error: {resp.text}")
                del user_data[chat]
        except:
            bot.send_message(chat, "সঠিকভাবে দাম লিখুন, যেমন: ৯৯.৫০")

if __name__ == "__main__":
    bot.polling(none_stop=True)
