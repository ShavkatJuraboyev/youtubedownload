from pyrogram import Client, filters
import os
import yt_dlp

# Telegram API ma'lumotlari
api_id = 26765004  # my.telegram.org saytida oling
api_hash = "de884308b7f1e1c857ca3b0822aa850a"
bot_token = "6253459858:AAEp2F4-NQms6VWgGNUgUJtAxlp_G6THA-U"
app = Client("video_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

DOWNLOAD_PATH = "./downloads"

def download_youtube_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_PATH}/%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        return file_path, info['title'], info['filesize']

@app.on_message(filters.text & filters.private)
async def video_handler(client, message):
    if message.text.startswith("http"):
        await message.reply_text("Video yuklanmoqda, iltimos biroz kuting, ⏱️ bir necha daqiqa olinishi mumkin...")

        file_path = None
        video_title = None
        video_size = None

        try:
            # Videoni yuklab olish va ma'lumotlarni olish
            file_path, video_title, video_size = download_youtube_video(message.text)

            # Video hajmini MB ga aylantirish
            if video_size is not None:
                video_size_mb = video_size / (1024 * 1024)
                size_info = f"🗂 {video_size_mb:.2f} MB\n"
            else:
                size_info = "🗂 Video hajmi aniqlanmadi\n"

            # Yuklangan videoni foydalanuvchiga yuborish va video haqida ma'lumot berish
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                caption=f"📹 `{video_title}`\n"
                        f"{size_info}\n"
                        f"📥 @youtube_dovlonda_robot orqali yuklandi",
                    )
        except Exception as e:
            await message.reply_text(f"Xatolik yuz berdi: {str(e)}")
        finally:
            # Yuklangan faylni o'chirish
            if file_path and os.path.exists(file_path):
                os.remove(file_path)


if __name__ == "__main__":
    print("Bot ishga tushdi!")
    app.run()  # `idle()` o'rniga `run()` foydalanamiz