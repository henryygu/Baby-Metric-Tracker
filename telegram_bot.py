import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)
from backend import crud, database, schemas
from backend.database import engine, Session
from datetime import datetime
import pytz
import yaml

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

# Define states
MENU = 0

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
ALLOWED_USER_IDS = []

# Read allowed user IDs from the file
def load_allowed_user_ids():
    global ALLOWED_USER_IDS
    try:
        with open("allowed_telegram_ids.txt", "r") as f:
            ALLOWED_USER_IDS = [int(line.strip()) for line in f.readlines()]
            logger.info(f"Allowed user IDs: {ALLOWED_USER_IDS}")
    except FileNotFoundError:
        logger.error("allowed_telegram_ids not found.")

def build_main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Pee Dad", callback_data="Pee-Dad"),
            InlineKeyboardButton("Poop Dad", callback_data="Poop-Dad"),
            InlineKeyboardButton("Mixed Dad", callback_data="Mixed-Dad"),
        ],
        [
            InlineKeyboardButton("Pee Mum", callback_data="Pee-Mum"),
            InlineKeyboardButton("Poop Mum", callback_data="Poop-Mum"),
            InlineKeyboardButton("Mixed Mum", callback_data="Mixed-Mum"),
        ],
        [
            InlineKeyboardButton("Start Feed Left", callback_data="Feed-Left"),
            InlineKeyboardButton("Start Feed Right", callback_data="Feed-Right"),
            InlineKeyboardButton("Start Feed Expressed", callback_data="Feed-Expressed"),
        ],
        [
            InlineKeyboardButton("Stop Feed", callback_data="Feed-Stop"),
        ],
        [
            InlineKeyboardButton("Start Sleep", callback_data="Sleep-Start"),
            InlineKeyboardButton("Stop Sleep", callback_data="Sleep-Stop"),
        ],
        [
            InlineKeyboardButton("Return last Feed", callback_data="Return-Feed"),
            InlineKeyboardButton("Return last Diaper", callback_data="Return-Diaper"),
        ]
    ])

async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USER_IDS:
        return ConversationHandler.END

    reply_markup = build_main_keyboard()
    await update.message.reply_text(
        "Welcome! Please choose an option:", reply_markup=reply_markup
    )
    return MENU

async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ALLOWED_USER_IDS:
        return MENU

    await query.answer()
    data = query.data

    with Session(engine) as db:
        if data == "Return-Feed":
            stats = crud.get_stats(db)
            last_feed = stats["last_completed_feed"]
            if not last_feed:
                message = "No previous feed found."
            else:
                now = crud.get_current_time()
                ts = last_feed.timestamp
                if ts.tzinfo is None: ts = crud.tz.localize(ts)
                time_since = now - ts
                
                hours, remainder = divmod(int(time_since.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                ts_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                message = (
                    f"🍼 Last Feed:\n"
                    f"Orientation: {last_feed.orientation}\n"
                    f"Duration: {last_feed.details}\n"
                    f"Time since: {ts_str}\n"
                    f"Feed ID: {last_feed.feed_id}"
                )
            await query.edit_message_text(text=message, reply_markup=build_main_keyboard())
            return MENU

        elif data == "Return-Diaper":
            stats = crud.get_stats(db)["diapers"]
            message = f"🦥 Last Diaper:\nType: {stats['last_type']}\nTime since: {stats['last_time_str']}"
            await query.edit_message_text(text=message, reply_markup=build_main_keyboard())
            return MENU

        if "Dad" in data or "Mum" in data:
            event, orientation = data.split("-")
            crud.log_event(db, schemas.LogCreate(event=event, orientation=orientation))
        elif data == "Feed-Stop":
            crud.stop_ongoing_session(db, "Feeding")
        elif data == "Sleep-Start":
            crud.log_event(db, schemas.LogCreate(event="Sleep", details="ongoing"))
        elif data == "Sleep-Stop":
            crud.stop_ongoing_session(db, "Sleep")
        elif data.startswith("Feed"):
            event, orientation = data.split("-")
            # Stop any ongoing feed if it exists before starting new one (simplified logic)
            crud.stop_ongoing_session(db, "Feeding")
            latest_id = crud.get_latest_feed_id(db)
            crud.log_event(db, schemas.LogCreate(event="Feeding", details="ongoing", orientation=orientation, feed_id=latest_id + 1))

    full_text = f"📜 *Select an option below:*\n✅ You selected *{data.replace('-', ' ')}*."
    await query.edit_message_text(text=full_text, reply_markup=build_main_keyboard(), parse_mode="Markdown")
    return MENU

def main():
    load_allowed_user_ids()
    application = ApplicationBuilder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={MENU: [CallbackQueryHandler(button)]},
        fallbacks=[CommandHandler("start", start)],
    )
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
