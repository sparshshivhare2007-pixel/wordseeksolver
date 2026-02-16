import asyncio
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from bot.handlers import Handlers, HOSTING
from config import BOT_TOKEN

load_dotenv()

async def main():
    handlers = Handlers()
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("logout", handlers.logout))
    app.add_handler(CommandHandler("new", handlers.new_game))

    # Host conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('host', handlers.host)],
        states={
            HOSTING: [MessageHandler(filters.ALL & ~filters.COMMAND, handlers.handle_auth)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)

    # Game controls
    app.add_handler(MessageHandler(filters.Regex(r'\.(start|off)'), handlers.game_control))

    print("🤖 Wordle Solver Bot running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
