from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from .solver import WordleSolver
from .database import db
import asyncio

HOSTING, AUTH_CODE = range(2)

class Handlers:
    def __init__(self):
        self.solvers = {}  # user_id -> WordleSolver

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 *Wordle Solver Bot*\n\n"
            "• `/host` - Login Telegram account\n"
            "• `/logout` - Logout\n"
            "• `/new` - Start new game\n\n"
            "*In target chat:*\n"
            "• `.start` - Start solver\n"
            "• `.off` - Stop solver",
            parse_mode='Markdown'
        )

    async def host(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        await update.message.reply_text(
            "🔐 *Login your account:*\n\n"
            "1️⃣ Forward ANY message from target account\n"
            "OR\n"
            "2️⃣ Send phone number (+1234567890)"
        )
        return HOSTING

    async def handle_auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        session_name = f"solver_{user_id}"

        # Create solver
        solver = WordleSolver(session_name)
        self.solvers[user_id] = solver
        
        # Start client in background
        asyncio.create_task(solver.start())
        
        await update.message.reply_text(
            f"✅ *Logged in!*\n\n"
            "Send me target CHAT ID or forward message from target chat:\n"
            "`/setchat -1001234567890`"
        )
        return ConversationHandler.END

    async def logout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id in self.solvers:
            await self.solvers[user_id].stop()
            del self.solvers[user_id]
        db.remove_session(user_id)
        await update.message.reply_text("👋 Logged out!")

    async def new_game(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        _, chat_id = db.get_session(user_id)
        if chat_id and user_id in self.solvers:
            solver = self.solvers[user_id]
            solver.chat_id = chat_id
            await update.message.reply_text(f"🎮 Started in chat `{chat_id}`", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ First `/host` and set chat!")

    async def game_control(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message.text.startswith('.'):
            return
        text = update.message.text.lower()
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        session_name, user_chat_id = db.get_session(user_id)
        if user_chat_id == chat_id:
            if '.start' in text:
                await update.message.reply("🚀 Solver started!")
            elif '.off' in text:
                await update.message.reply("⏹️ Solver stopped!")
