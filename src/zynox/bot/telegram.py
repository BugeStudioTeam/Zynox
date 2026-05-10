"""Telegram bot integration"""

import os
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

class TelegramBot:
    """Telegram bot handler"""
    
    def __init__(self, zynox_instance, token: str):
        self.zynox = zynox_instance
        self.token = token
        self.authorized_users = set()
        self.load_config()
    
    def load_config(self):
        """Load authorized users"""
        config_file = os.path.expanduser("~/.zynoxai/telegram_config.json")
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                data = json.load(f)
                self.authorized_users = set(data.get("authorized_users", []))
    
    def save_config(self):
        """Save authorized users"""
        config_file = os.path.expanduser("~/.zynoxai/telegram_config.json")
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump({"authorized_users": list(self.authorized_users)}, f, indent=2)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome = "🤖 ZynoxAI Bot\n\nSend me natural language requests like:\n- 'create a python file called hello.py'\n- 'find abc.txt and read it'\n- 'list all files'"
        await update.message.reply_text(welcome)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages"""
        user_id = update.effective_user.id
        
        # Authorize first user
        if not self.authorized_users:
            self.authorized_users.add(user_id)
            self.save_config()
            await update.message.reply_text("✅ You are now authorized as admin!")
        
        if user_id not in self.authorized_users:
            await update.message.reply_text("❌ Unauthorized")
            return
        
        await update.message.chat.send_action(action="typing")
        
        # Process request
        import io
        from contextlib import redirect_stdout
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            self.zynox.process_request(update.message.text)
        
        result = output_buffer.getvalue()
        if not result:
            result = "✅ Task completed"
        
        # Split long messages
        if len(result) > 4000:
            for i in range(0, len(result), 4000):
                await update.message.reply_text(result[i:i+4000])
        else:
            await update.message.reply_text(result)
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_msg = f"🤖 Bot Running\nProvider: {self.zynox.current_provider}\nAuthorized users: {len(self.authorized_users)}"
        await update.message.reply_text(status_msg)
    
    async def new_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /new command"""
        self.zynox.session_manager.new_session()
        await update.message.reply_text("✅ New session created")
    
    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        self.zynox.session_manager.clear_memory()
        await update.message.reply_text("✅ Memory cleared")
    
    def run(self):
        """Run the bot"""
        app = Application.builder().token(self.token).build()
        
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("status", self.status))
        app.add_handler(CommandHandler("new", self.new_session))
        app.add_handler(CommandHandler("clear", self.clear))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        print("[Telegram Bot Started]")
        app.run_polling()