# utils.py
import os
import subprocess
from config import ALLOWED_USERS, DOWNLOAD_DIR

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_allowed(user_id):
    """检查用户是否在白名单"""
    return user_id in ALLOWED_USERS

def run_yt_dlp(args):
    """运行 yt-dlp 命令"""
    subprocess.run(args, check=True)

def get_latest_file():
    """获取最近下载的文件路径"""
    files = sorted(
        [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)],
        key=os.path.getmtime,
        reverse=True
    )
    return files[0] if files else None
