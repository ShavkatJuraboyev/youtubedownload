import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from pyrogram import Client
import yt_dlp

# Aiogram API TOKEN
API_TOKEN = "6253459858:AAEp2F4-NQms6VWgGNUgUJtAxlp_G6THA-U"

# Pyrogram API credentials
API_ID = 26765004  # Get this from my.telegram.org
API_HASH = "de884308b7f1e1c857ca3b0822aa850a"

# Bot and dispatcher objects
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Pyrogram client
pyrogram_client = Client(
    "bot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=API_TOKEN
)

# Directory for downloads
DOWNLOAD_PATH = "./downloads"


@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Respond to the /start command."""
    await message.reply("Hello! Send me a YouTube video link.")


def download_youtube_video(url):
    """Download a YouTube video."""
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        video_title = info.get('title', 'Unknown Title')
        video_size = info.get('filesize')  # May be None if not available
        return file_path, video_title, video_size


@dp.message()
async def video(message: types.Message):
    """Handle YouTube video download and send."""
    if message.text.startswith("http"):
        await message.reply("Downloading video, please wait. ⏱️ This may take a few minutes...")

        try:
            # Download video
            file_path, video_title, video_size = download_youtube_video(message.text)

            # Format video size if available
            if video_size is not None:
                video_size_mb = video_size / (1024 * 1024)
                size_text = f"🗂 {video_size_mb:.2f} MB\n"
            else:
                size_text = "🗂 Size unavailable\n"

            # Send video using Pyrogram
            print(message.chat.id)
            await pyrogram_client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                caption=f"📹 {video_title}\n"
                        f"{size_text}\n"
                        f"📥 Downloaded via @youtube_dovlonda_robot"
            )

        except Exception as e:
            await message.reply(f"An error occurred: {str(e)}")
        finally:
            # Remove downloaded file
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        await message.reply("Please send a valid YouTube link.")

async def main():
    """Start Pyrogram and Aiogram."""
    # Ensure download directory exists
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    # Start Pyrogram client
    await pyrogram_client.start()

    # Start Aiogram polling
    try:
        print("Bot is running!")
        await dp.start_polling(bot)
    finally:
        # Properly stop Pyrogram
        await pyrogram_client.stop()


if __name__ == '__main__':
    asyncio.run(main())
