# commands/audio.py
from telegram import Update
from telegram.ext import ContextTypes
from utils import is_allowed, run_yt_dlp, get_latest_file, DOWNLOAD_DIR

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.message.from_user.id):
        await update.message.reply_text("❌ 你没有权限使用此功能")
        return
    if not context.args:
        await update.message.reply_text("用法: /audio <url>")
        return

    url = context.args[0]
    await update.message.reply_text(f"正在提取音频: {url}")

    try:
        run_yt_dlp([
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "-o", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            url
        ])

        audio_path = get_latest_file()
        if not audio_path:
            await update.message.reply_text("提取失败")
            return

        await update.message.reply_text("上传中...")
        with open(audio_path, "rb") as f:
            await update.message.reply_audio(f)
        os.remove(audio_path)

    except Exception as e:
        await update.message.reply_text(f"提取失败: {e}")
