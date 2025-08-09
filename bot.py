# main.py
import logging
from telegram.ext import ApplicationBuilder, CommandHandler

# 从我们分离的文件中导入配置和处理器
import config
from commands.handlers import start, download
from commands.audio import audio

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数，用于启动机器人"""
    logger.info("机器人正在启动...")

    # 使用 config.py 中的 Token 创建应用
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # 添加命令处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", download))
    app.add_handler(CommandHandler("audio", audio))
    
    logger.info("机器人已上线，开始轮询...")
    # 启动轮询
    app.run_polling()
    logger.info("机器人已停止。")


if __name__ == "__main__":
    main()