# bot/audio.py (新文件)

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError

from .downloader import download_media # 导入我们改造后的函数
from config import TELEGRAM_FILE_SIZE_LIMIT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /audio 命令，下载并发送音频"""
    if not context.args:
        await update.message.reply_text("请提供一个链接。用法: /audio <youtube-or-bilibili-url>")
        return

    url = context.args[0]
    unique_id = f"{update.effective_chat.id}_{update.message.id}"
    
    status_message = await update.message.reply_text("🎵 音频链接已收到，正在准备下载...")

    # 调用下载模块，并指明 media_type='audio'
    result = await download_media(url, unique_id, media_type='audio')

    if result is None:
        await status_message.edit_text("❌ 音频下载失败。\n请检查链接或重试。")
        return

    audio_path, audio_title = result

    if os.path.getsize(audio_path) > TELEGRAM_FILE_SIZE_LIMIT:
        await status_message.edit_text(f"😭 音频文件超过 50MB，无法发送。")
        os.remove(audio_path)
        return

    await status_message.edit_text("✅ 下载完成！正在上传音频...")

    try:
        with open(audio_path, "rb") as audio_file:
            await update.message.reply_audio(audio=audio_file, title=audio_title, caption=f"🎵 {audio_title}")
        
        await status_message.delete()

    except NetworkError as e:
        logger.error(f"上传音频时发生网络错误: {e}")
        await status_message.edit_text("❌ 上传失败，网络连接似乎出了问题。")
    except Exception as e:
        logger.error(f"上传音频时发生未知错误: {e}")
        await status_message.edit_text("❌ 上传时发生未知错误。")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            logger.info(f"本地音频文件已删除: {audio_path}")