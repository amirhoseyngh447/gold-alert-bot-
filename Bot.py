import requests
import time
import threading
from telegram.ext import Updater, CommandHandler

TOKEN = "8502662632:AAF8sYcE61SER_bTkSrm1Zx9Pwk2oQ-493g"

alerts = {}  # user_id -> target_price_toman


def get_gold_price_toman():
    url = "https://api.brsapi.ir/v1/price/gold"
    r = requests.get(url, timeout=10).json()
    price_rial = r["data"]["gold18"]
    return int(price_rial / 10)  # Rial → Toman


def start(update, context):
    update.message.reply_text(
        "سلام 👋\n"
        "من ربات هشدار قیمت طلای ۱۸ عیار هستم.\n\n"
        "برای ثبت هشدار:\n"
        "/set 3000000\n\n"
        "برای دیدن قیمت:\n"
        "/price"
    )


def set_alert(update, context):
    user_id = update.message.chat_id

    if len(context.args) == 0:
        update.message.reply_text("لطفاً قیمت هدف را به تومان وارد کن. مثال:\n/set 3000000")
        return

    try:
        price = int(context.args[0])
        alerts[user_id] = price
        update.message.reply_text(
            f"هشدار ثبت شد ✔️\n"
            f"وقتی قیمت طلای ۱۸ به {price:,} تومان برسد خبر می‌دهم."
        )
    except:
        update.message.reply_text("قیمت نامعتبر است.")


def show_price(update, context):
    price = get_gold_price_toman()
    update.message.reply_text(f"قیمت فعلی طلای ۱۸ عیار:\n{price:,} تومان")


def price_checker():
    while True:
        try:
            price = get_gold_price_toman()
            print("Current Gold Price:", price)

            for user, target in list(alerts.items()):
                if price <= target:
                    updater.bot.send_message(
                        user,
                        f"⚠️ هشدار\n"
                        f"قیمت طلای ۱۸ به {price:,} تومان رسید یا کمتر شد.\n"
                        f"🎯 هدف شما: {target:,} تومان"
                    )
                    del alerts[user]
        except Exception as e:
            print("Error:", e)

        time.sleep(3600)  # check every 1 hour


updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("set", set_alert))
dp.add_handler(CommandHandler("price", show_price))

threading.Thread(target=price_checker, daemon=True).start()

updater.start_polling()
updater.idle()
