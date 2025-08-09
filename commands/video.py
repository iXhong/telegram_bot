# commands/download.py
from telegram import Update
from telegram.ext import ContextTypes
from utils import is_allowed, run_yt_dlp, get_latest_file, DOWNLOAD_DIR

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.message.from_user.id):
        await update.message.reply_text("❌ 你没有权限使用此功能")
        return
    if not context.args:
        await update.message.reply_text("用法: /download <url>")
        return

    url = context.args[0]
    await update.message.reply_text(f"正在下载: {url}")

    try:
        run_yt_dlp([
            "yt-dlp",
            "-f", "mp4",
            "-o", f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
            url
        ])

        video_path = get_latest_file()
        if not video_path:
            await update.message.reply_text("下载失败")
            return

        await update.message.reply_text("上传中...")
        with open(video_path, "rb") as f:
            await update.message.reply_video(f)
        os.remove(video_path)

    except Exception as e:
        await update.message.reply_text(f"下载失败: {e}")
