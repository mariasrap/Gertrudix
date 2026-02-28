import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
INBOX_DIR = Path(__file__).parent.parent.parent / "data" / "telegram_inbox"


def ensure_inbox_exists():
    """Create inbox directory if it doesn't exist."""
    INBOX_DIR.mkdir(parents=True, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    logging.info(f"Received /start from {update.effective_user.id}")
    await update.message.reply_text(
        "Hi! I'm Gertrudix's quick capture bot.\n\n"
        "Send me any message and I'll save it for your morning review."
    )


async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save any text message to inbox."""
    logging.info(f"Received message from {update.effective_user.id}: {update.message.text[:50]}...")
    ensure_inbox_exists()

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    filename = f"{timestamp}_message.md"

    # Handle duplicate filenames within same minute
    filepath = INBOX_DIR / filename
    counter = 1
    while filepath.exists():
        filename = f"{timestamp}_message_{counter}.md"
        filepath = INBOX_DIR / filename
        counter += 1

    # Create markdown content
    content = f"""# Quick Capture

**Date:** {now.strftime("%Y-%m-%d %H:%M")}

---

{update.message.text}
"""

    filepath.write_text(content, encoding='utf-8')

    await update.message.reply_text("✓ Saved for morning review")


def create_bot() -> Application:
    """Create and configure the bot application."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_message))

    return app


def run():
    """Run the bot."""
    print("Starting Gertrudix Telegram bot...")
    app = create_bot()
    app.run_polling(allowed_updates=Update.ALL_TYPES)
