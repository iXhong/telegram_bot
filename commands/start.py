# commands/start.py
from telegram import Update
from telegram.ext import ContextTypes
from utils import is_allowed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.message.from_user.id):
        await update.message.reply_text("❌ 你没有权限使用此 bot")
        return
    await update.message.reply_text("欢迎使用视频下载 bot！")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"你的 ID: {update.message.from_user.id}")
