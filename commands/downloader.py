# bot/downloader.py (修正后)

import asyncio
import os
import logging
from typing import Optional, Tuple

from config import DOWNLOAD_DIR

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def download_media(url: str, unique_id: str, media_type: str) -> Optional[Tuple[str, str]]:
    """
    使用 yt-dlp 异步下载媒体文件（视频或音-频）。
    修复了音-频下载后文件名不匹配的 bug。
    """
    try:
        if media_type == 'video':
            # 视频下载逻辑保持不变，--get-filename 对视频合并通常是可靠的
            output_template = f"{DOWNLOAD_DIR}/{unique_id}_%(title)s.%(ext)s"
            cmd = [
                "yt-dlp",
                "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "--merge-output-format", "mp4",
                "--output", output_template,
                "--get-filename",  # 获取将要生成的文件名
                url
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logger.error(f"获取视频文件名失败: {stderr.decode(errors='ignore').strip()}")
                return None
            
            media_path = stdout.decode().strip()
            # 移除 --get-filename 参数以进行实际下载
            cmd.pop(-2) 

        elif media_type == 'audio':
            # --- 音-频下载逻辑重大修改 ---
            output_template = f"{DOWNLOAD_DIR}/{unique_id}_%(title)s.%(ext)s" # 让 yt-dlp 决定扩展名
            cmd = [
                "yt-dlp",
                "--format", "bestaudio/best",
                "--extract-audio",
                "--audio-format", "mp3", # 最终格式是 mp3
                "--audio-quality", "0",
                "--output", output_template,
                url
            ]
            # 对于音-频转换，我们不再使用 --get-filename，直接下载

        else:
            logger.error(f"不支持的媒体类型: {media_type}")
            return None

        # --- 执行下载 ---
        logger.info(f"正在执行下载命令: {' '.join(cmd)}")
        process_download = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process_download.communicate()

        if process_download.returncode != 0:
            error_message = stderr.decode(errors='ignore').strip()
            logger.error(f"媒体下载失败 (yt-dlp): {error_message}")
            return None

        # --- Bug 修复的关键部分 ---
        if media_type == 'audio':
            # 下载完成后，主动在目录中查找我们生成的 .mp3 文件
            found_file = None
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(unique_id) and f.endswith(".mp3"):
                    found_file = os.path.join(DOWNLOAD_DIR, f)
                    break
            
            if not found_file:
                logger.error(f"下载后未能找到对应的 .mp3 文件， unique_id: {unique_id}")
                return None
            media_path = found_file
        
        # 确认最终文件存在
        if not os.path.exists(media_path):
            logger.error(f"下载声称成功，但最终文件未找到: {media_path}")
            return None

        media_title = os.path.basename(media_path).replace(f"{unique_id}_", "").rsplit('.', 1)[0]
        logger.info(f"媒体处理成功: {media_path}")
        return media_path, media_title

    except Exception as e:
        logger.error(f"下载过程中发生未知错误: {e}")
        return None