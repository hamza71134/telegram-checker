
import asyncio
import logging
import os
import random
import re
import time
from aiogram import Bot, Dispatcher, types
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
from dotenv import load_dotenv

load_dotenv()

# Load credentials from environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
phone_number = os.getenv("PHONE_NUMBER")
bot_token = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

client = TelegramClient('bot_session', api_id, api_hash)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply(
        """👋 Telegram Checker Bot চালু হয়েছে!

➤ শুধু নাম্বার পাঠালেই হবে (এক লাইনে বা আলাদা করে)
➤ সর্বোচ্চ ৩০টা নাম্বার একসাথে পাঠাতে পারো

উদাহরণ:
8801712345678
+8801811223344"""
    )


@dp.message_handler()
async def handle_numbers(message: types.Message):
    raw_text = message.text.strip()
    numbers = re.findall(r"(\+?\d{10,15})", raw_text)

    if not numbers:
        await message.reply("⚠️ কোনো বৈধ নাম্বার পাওয়া যায়নি।")
        return

    if len(numbers) > 30:
        await message.reply("⚠️ সর্বোচ্চ ৩০টা নাম্বার পাঠাতে পারো। দয়া করে কমিয়ে পাঠাও।")
        return

    await client.connect()

    for number in numbers:
        if not number.startswith("+"):
            number = "+" + number

        try:
            contact = InputPhoneContact(
                client_id=random.randint(10000, 999999),
                phone=number,
                first_name="Check",
                last_name="User"
            )
            result = await client(ImportContactsRequest([contact]))
            user = result.users[0] if result.users else None

            if user:
                await message.reply(f"[✅] {number} => Telegram এ আছে")
                await client(DeleteContactsRequest([user.id]))
            else:
                await message.reply(f"[❌] {number} => Telegram এ নেই")

        except Exception:
            await message.reply(f"[❌] {number} => Telegram এ নেই")

        time.sleep(1)

    await client.disconnect()


async def start_bot():
    await client.start(phone=phone_number)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(start_bot())
