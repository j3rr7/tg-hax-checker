import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    MenuButton, MenuButtonCommands, KeyboardButtonPollType
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from dotenv import load_dotenv
import logging
from itertools import cycle

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger().setLevel(logging.DEBUG)

requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

load_dotenv()


def check(url, proxied=False):
    headers = {
        "UserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "content-type": "application/json"
    }
    data = requests.get(url, headers=headers, timeout=30)
    return data.text if data.status_code == 200 else None


def get_server_info(url):
    html_text = check(url)
    if not html_text:
        return "no-data"
    soup = BeautifulSoup(html_text, "html.parser")
    zone_list = [x.text for x in soup("h5", class_="card-title mb-4")]
    sum_list = [x.text for x in soup("h1", class_="card-text")]
    vps_list = []
    vps_dict = {}
    vps_str = ""
    for k, v in zip(zone_list, sum_list):
        zone = k.split("-", 1)[0].lstrip("./")
        sum_ = (
            k.split("-", 1)[1] + "(" + v.rstrip(" VPS") + " node)"
            if len(k.split("-", 1)) > 1
            else v
        )
        vps_list.append((zone, sum_))
    for k_v in vps_list:
        k, v = k_v
        vps_dict.setdefault(k, []).append(v)
    for k, v in vps_dict.items():
        vps_str += ">> " + k + "-" + ", ".join(v) + "\n"
    return vps_str


def get_data_center(url, frmt=False):
    html_text = check(url)
    if not html_text:
        return "no data"
    soup = BeautifulSoup(html_text, "html.parser")
    ctr_list = [x.text for x in soup("option", value=re.compile(r"^[A-Z]{2,}-"))]
    ctr_str = "\n".join(ctr_list)
    return ctr_str


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            KeyboardButton("/check", callback_data="check"),
            KeyboardButton("/hax", callback_data="hax"),
            KeyboardButton("/woiden", callback_data="woiden"),
            KeyboardButton("/both", callback_data="both"),
        ],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Options:",
        reply_markup=reply_markup
    )


async def check_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global_vps_stat = get_server_info("https://hax.co.id/data-center")

    avail_str = f'[ Data Centers ]\n---------- \n{global_vps_stat}'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=avail_str
    )


async def hax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hax_vps_stat = get_data_center("https://hax.co.id/create-vps", True)
    avail_str = f'[ Available Centers ]\n---------- \n{hax_vps_stat}'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=avail_str
    )


async def woiden(update: Update, context: ContextTypes.DEFAULT_TYPE):
    woiden_vps_stat = get_data_center("https://woiden.id/create-vps", True)
    avail_str = f'[ Available Centers ]\n---------- \n{woiden_vps_stat}'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=avail_str
    )


async def both(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hax_vps_stat = get_data_center("https://hax.co.id/create-vps", True)
    woiden_vps_stat = get_data_center("https://woiden.id/create-vps", True)
    avail_str = f'[ Available Centers ]\n---------- \n' \
                f'--- HAX ---\n' \
                f'{hax_vps_stat}\n' \
                f'--- WOIDEN ---\n' \
                f'{woiden_vps_stat}'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=avail_str
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    start_handler = CommandHandler('start', start)
    check_handler = CommandHandler('check', check_)
    hax_handler = CommandHandler('hax', hax)
    woiden_handler = CommandHandler('woiden', woiden)
    both_handler = CommandHandler('both', both)

    application.add_handler(start_handler)
    application.add_handler(check_handler)
    application.add_handler(hax_handler)
    application.add_handler(woiden_handler)
    application.add_handler(both_handler)

    application.run_polling()
