import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)
from func.utils import (
    log_event,
    get_last_feed,
    update_feed,
    latest_feed_id,
    get_time_since_last,
    last_diaper,
    get_time,
    string_to_datetime,
    format_timedelta,
)

with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

# Define states
MENU, OPTION1, OPTION2, OPTION3, OPTION4, OPTION5, OPTION6 = range(7)

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
        with open("allowed_users.txt", "r") as f:
            # Read each line, strip newlines, and convert to integer
            ALLOWED_USER_IDS = [int(line.strip()) for line in f.readlines()]
    except FileNotFoundError:
        print("allowed_users.txt not found. Make sure the file exists.")
# Check if a user is allowed
def is_user_allowed(user_id):
    return user_id in ALLOWED_USER_IDS

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
            InlineKeyboardButton("Last Feed Left", callback_data="Feed-Left"),
            InlineKeyboardButton("Last Feed Right", callback_data="Feed-Right"),
            InlineKeyboardButton("Last Feed Expressed", callback_data="Feed-Expressed"),
        ],
        [
            InlineKeyboardButton("Return last Feed", callback_data="Return-Feed"),
            InlineKeyboardButton("Return last Diaper", callback_data="Return-Diaper"),
        ]
    ])


async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    print(update.message.from_user.id)
    # Check if the user is allowed
    if user_id not in ALLOWED_USER_IDS:
        return ConversationHandler.END  # End the conversation for unauthorized users

    reply_markup = build_main_keyboard()
    await update.message.reply_text(
        "Welcome! Please choose an option:", reply_markup=reply_markup
    )
    return MENU


async def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    user_id = query.from_user.id

    # Check if the user is allowed
    if user_id not in ALLOWED_USER_IDS:
        return MENU  # Return to the menu or end the interaction

    await query.answer()

    data = query.data

    if data == "Return-Feed":
        # Get current time and last feed information
        current_bst = get_time()
        last_time_all, duration_all, orientation_all, feed_id = get_last_feed(ongoing=False)
        if last_time_all is None:  # Handle case if there's no last feed
            await query.edit_message_text(
                text="No previous feed found.",
                reply_markup=build_main_keyboard()
            )
            return MENU
        
        last_time_1 = string_to_datetime(last_time_all)
        time_since = current_bst - last_time_1

        # Create the message to send back to the user
        message = (
            f"🍼 Last Feed:\n"
            f"Orientation: {orientation_all}\n"
            f"Duration: {duration_all}\n"
            f"Time since: {format_timedelta(time_since)}\n"
            f"Feed ID: {feed_id}"
        )

    # If it's Return-Diaper, include diaper-related data
    if data == "Return-Diaper":
        time_since_pee = get_time_since_last('Pee')
        time_since_poop = get_time_since_last('Poop')
        time_since_mixed = get_time_since_last('Mixed')
        last_diaper_type, last_diaper_time_since = last_diaper(time_since_pee, time_since_poop, time_since_mixed)

        message = f"\n\n🩵 Last Diaper:\nType: {last_diaper_type}\nTime since: {last_diaper_time_since}"

    # Send the response with the feed details
    await query.edit_message_text(
        text=message,
        reply_markup=build_main_keyboard()
    )
    return MENU

    if "Dad" in data or "Mum" in data:
        event, orientation = data.split("-")
        log_event(event, orientation=orientation)

    elif data.startswith("Feed"):
        event, orientation = data.split("-")
        last_feed = get_last_feed()
        if not last_feed:
            log_event("Feeding", "ongoing", orientation=orientation, feed_id=None)
        else:
            update_feed(last_feed)
            log_event("Feeding", "ongoing", orientation=orientation, feed_id=latest_feed_id())

    static_message = "📜 *Select an option below:*\n"
    dynamic_message = f"✅ You selected *{data.replace('-', ' ')}*.\n"
    full_text = static_message + dynamic_message

    await query.edit_message_text(
        text=full_text,
        reply_markup=build_main_keyboard(),
        parse_mode="Markdown"
    )

    return MENU


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END


def main():
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    # ConversationHandler to handle the state machine
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [CallbackQueryHandler(button)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
