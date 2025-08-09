# bot/handlers.py
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError

from .downloader import download_media
from config import TELEGRAM_FILE_SIZE_LIMIT

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_html(
        "<b>欢迎使用 YouTube 下载机器人！</b>\n\n"
        "发送 <code>/download &lt;YouTube链接&gt;</code> 即可下载视频。\n\n"
        "注意：由于 Telegram 限制，目前仅支持下载 <b>50MB</b> 以下的视频。"
    )

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /download 命令"""
    if not context.args:
        await update.message.reply_text("请提供一个 YouTube 链接。用法: /download <youtube-url>")
        return

    url = context.args[0]
    
    # 使用 chat_id 和 message_id 组合成唯一标识符
    unique_id = f"{update.effective_chat.id}_{update.message.id}"
    
    # 发送一个初始消息，并保存它以便后续编辑
    status_message = await update.message.reply_text(f"🔗 链接已收到，正在准备下载...")

    # 调用下载模块
    result = await download_media(url, unique_id)

    if result is None:
        await status_message.edit_text("❌ 下载失败。\n请检查链接是否正确，或视频可能受版权/地区保护。")
        return

    video_path, video_title = result

    # 检查文件大小
    if os.path.getsize(video_path) > TELEGRAM_FILE_SIZE_LIMIT:
        await status_message.edit_text(f"😭 下载完成，但视频文件超过 50MB，无法通过 Telegram 发送。")
        os.remove(video_path) # 删除大文件
        return

    await status_message.edit_text("✅ 下载完成！正在上传到 Telegram...")

    try:
        with open(video_path, "rb") as video_file:
            await update.message.reply_video(video=video_file, caption=video_title, supports_streaming=True)
        
        # 成功发送后删除状态消息
        await status_message.delete()

    except NetworkError as e:
        logger.error(f"上传时发生网络错误: {e}")
        await status_message.edit_text("❌ 上传失败，似乎网络连接出了点问题。")
    except Exception as e:
        logger.error(f"上传视频时发生未知错误: {e}")
        await status_message.edit_text("❌ 上传时发生未知错误。")
    finally:
        # 确保无论成功与否都删除本地文件
        if os.path.exists(video_path):
            os.remove(video_path)
            logger.info(f"本地文件已删除: {video_path}")