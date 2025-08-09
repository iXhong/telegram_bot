# bot.py
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from commands.start import start, myid
from commands.video import download
from commands.audio import audio

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 注册命令
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("download", download))
    app.add_handler(CommandHandler("audio", audio))

    app.run_polling()
