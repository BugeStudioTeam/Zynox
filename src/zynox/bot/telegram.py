"""Telegram bot integration"""

import os
import json
import io
from contextlib import redirect_stdout
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ..config import TELEGRAM_CONFIG_FILE
from ..utils.colors import green, yellow

class TelegramBotHandler:
    """Telegram Bot Handler - Runs in main thread"""
    
    def __init__(self, zynox_instance, token):
        self.zynox = zynox_instance
        self.token = token
        self.application = None
        self.authorized_users = set()
        self.load_config()
    
    def load_config(self):
        """Load telegram configuration"""
        if os.path.exists(TELEGRAM_CONFIG_FILE):
            try:
                with open(TELEGRAM_CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self.authorized_users = set(config.get("authorized_users", []))
            except:
                pass
    
    def save_config(self):
        """Save telegram configuration"""
        config = {"authorized_users": list(self.authorized_users)}
        with open(TELEGRAM_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized"""
        return not self.authorized_users or user_id in self.authorized_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_msg = """
🤖 *ZynoxAI Bot*

AI-powered file and folder creation tool.

*Commands:*
/start - Show this
/help - Show help
/status - Show status
/new - New session
/clear - Clear memory
/history - Show history
/list - List files
/pwd - Show current directory
/cd <path> - Change directory

*Usage:*
Just send any request like:
- "create a python file called hello.py"
- "find abc.txt and read it"
- "list all files"
        """
        await update.message.reply_text(welcome_msg, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_msg = """
*ZynoxAI Bot Commands:*

/new - New conversation session
/clear - Clear current memory
/history - Show conversation history
/status - Show bot status
/list - List files in current directory
/pwd - Show current working directory
/cd <path> - Change directory

*Just type your request naturally!*
        """
        await update.message.reply_text(help_msg, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        status_msg = f"""
*Bot Status:*
🤖 Bot: Running
🔄 Provider: {self.zynox.current_provider}
💾 Session: {self.zynox.memory.current_session['session_id'][:20]}...
📝 Messages: {len(self.zynox.memory.current_session['messages'])}
🌍 Environment: {self.zynox.environment.upper()}

*System:*
📁 Working Dir: {os.getcwd()}
        """
        await update.message.reply_text(status_msg, parse_mode='Markdown')
    
    async def new_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /new command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        self.zynox.memory.new_session()
        await update.message.reply_text("✅ New conversation session created!")
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        self.zynox.memory.clear_memory()
        await update.message.reply_text("✅ Memory cleared!")
    
    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        messages = self.zynox.memory.current_session.get("messages", [])[-10:]
        if not messages:
            await update.message.reply_text("No conversation history")
            return
        
        history_text = "*Recent Conversation:*\n\n"
        for msg in messages:
            role = "👤 User" if msg["role"] == "user" else "🤖 AI"
            content = msg["content"][:100]
            history_text += f"{role}: {content}\n\n"
        
        await update.message.reply_text(history_text[:4000], parse_mode='Markdown')
    
    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /list command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        files = self.zynox.list_files(".")
        await update.message.reply_text(f"📁 *Current Directory:*\n```\n{files[:3000]}\n```", parse_mode='Markdown')
    
    async def pwd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pwd command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        await update.message.reply_text(f"📂 Current directory: `{os.getcwd()}`", parse_mode='Markdown')
    
    async def cd_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cd command"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized")
            return
        
        if not context.args:
            await update.message.reply_text("Usage: /cd <path>")
            return
        
        path = context.args[0]
        try:
            os.chdir(path)
            await update.message.reply_text(f"✅ Changed to: `{os.getcwd()}`", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Failed: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user_id = update.effective_user.id
        if not self.is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized. Contact admin to get access.")
            return
        
        user_input = update.message.text
        await update.message.chat.send_action(action="typing")
        
        try:
            output_buffer = io.StringIO()
            with redirect_stdout(output_buffer):
                self.zynox.memory.add_message("user", user_input)
                self.zynox.task_complete = False
                
                file_list = self.zynox.list_files(".")
                prompt = self.zynox.create_prompt(user_input, "", file_list)
                response = self.zynox.call_api(self.zynox.current_provider, prompt)
                
                if response:
                    self.zynox.memory.add_message("assistant", response[:300])
                    self.zynox.parse_and_execute(response, ".")
            
            result = output_buffer.getvalue()
            if not result or len(result.strip()) == 0:
                result = "✅ Task completed"
            
            if len(result) > 4000:
                for i in range(0, len(result), 4000):
                    await update.message.reply_text(result[i:i+4000])
            else:
                await update.message.reply_text(result)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        print(f"Telegram error: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text("❌ An error occurred. Please try again.")
    
    def run(self):
        """Run the bot"""
        self.application = Application.builder().token(self.token).build()
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("new", self.new_command))
        self.application.add_handler(CommandHandler("clear", self.clear_command))
        self.application.add_handler(CommandHandler("history", self.history_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("pwd", self.pwd_command))
        self.application.add_handler(CommandHandler("cd", self.cd_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)
        
        print(green("[Telegram Bot Started. Press Ctrl+C to stop]"))
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        return True