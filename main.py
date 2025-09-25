import asyncio
import random
import logging
from datetime import date
from typing import Dict, List, Any

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from faker import Faker

try:
    import config
    BOT_TOKEN = config.BOT_TOKEN
except Exception:
    BOT_TOKEN = ""

if not BOT_TOKEN:
    raise SystemExit("Create config.py with BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Faker locale mapping ---
LOCALE_MAP: Dict[str, str] = {
    "Nigeria": "en_NG",
    "USA": "en_US",
    "Canada": "en_CA",
    "Germany": "de_DE",
}

# Fallback datasets
FALLBACK: Dict[str, Dict[str, List[Any]]] = {
    "Nigeria": {
        "streets": ["12 Ahmadu Bello Way", "45 Unity Rd", "101 Bompai St", "77 Broad St", "9 Tafawa Balewa Ln"],
        "cities": ["Lagos", "Abuja", "Kano", "Port Harcourt", "Ibadan"],
        "phones": ["+2348034567890", "+2348061122334", "+2347019988776"]
    },
    "USA": {
        "streets": ["123 Main St", "456 Elm Ave", "789 Oak Blvd", "321 Pine Rd", "55 Maple Dr"],
        "cities": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
        "phones": ["+1-202-555-0145", "+1-415-555-0199", "+1-646-555-0111"]
    },
    "Canada": {
        "streets": ["55 King St", "88 Queen Ave", "200 Bay Rd", "17 Yonge St"],
        "cities": ["Toronto", "Vancouver", "Ottawa", "Montreal"],
        "phones": ["+1-416-555-0133", "+1-604-555-0188", "+1-613-555-0190"]
    },
    "Germany": {
        "streets": ["10 Alexanderplatz", "25 Hauptstrasse", "88 Lindenweg", "42 Goetheplatz"],
        "cities": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
        "phones": ["+49-30-123456", "+49-89-987654", "+49-40-543210"]
    }
}

COUNTRIES = list(LOCALE_MAP.keys())

# --- Helper functions ---

def get_faker_for(country: str) -> Faker:
    locale = LOCALE_MAP.get(country)
    try:
        return Faker(locale) if locale else Faker()
    except Exception as e:
        logging.warning(f"Faker locale '{locale}' not found. Falling back to default. Error: {e}")
        return Faker()

def get_data_with_fallback(fake_instance: Faker, attribute: str, country: str, fallback_type: str = None) -> Any:
    try:
        return getattr(fake_instance, attribute)()
    except (AttributeError, KeyError):
        if country in FALLBACK and fallback_type and fallback_type in FALLBACK[country]:
            return random.choice(FALLBACK[country][fallback_type])
        return "Not available"

def generate_identity(country: str) -> str:
    fake = get_faker_for(country)

    gender = random.choice(["Male", "Female"])
    try:
        name = fake.name_male() if gender == "Male" else fake.name_female()
    except AttributeError:
        name = fake.name()

    street = get_data_with_fallback(fake, 'street_address', country, 'streets')
    city = get_data_with_fallback(fake, 'city', country, 'cities')
    postal = get_data_with_fallback(fake, 'postcode', country)

    phone = get_data_with_fallback(fake, 'phone_number', country, 'phones')
    email = get_data_with_fallback(fake, 'free_email', country)
    dob = get_data_with_fallback(fake, 'date_of_birth', country)
    job = get_data_with_fallback(fake, 'job', country)

    national_id = None
    if country == "USA":
        national_id = get_data_with_fallback(fake, 'ssn', country)
    elif country == "Germany":
        national_id = str(random.randint(1000000000, 9999999999))
    elif country == "Canada":
        national_id = str(random.randint(100000000, 999999999))
    elif country == "Nigeria":
        national_id = str(random.randint(10000000000, 99999999999))

    bio = get_data_with_fallback(fake, 'sentence', country)

    parts = [
        f"🌍 {country} — Fake Identity",
        "-------------------------------",
        f"👤 Name: {name}",
        f"⚥ Gender: {gender}",
        f"🎂 DOB: {dob}",
        f"🏢 Job: {job}",
        f"🏠 Address: {street}, {city}",
        f"🏷️ Postal Code: {postal}",
        f"📞 Phone: {phone}",
        f"✉️ Email: {email}",
    ]

    if national_id:
        parts.append(f"🆔 National ID: {national_id}")

    parts.append(f"📝 Bio: {bio}")

    return "\n".join(parts)

# --- Keyboards ---

def main_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Fake Info", callback_data="menu_fake")],
        [InlineKeyboardButton(text="❓ Help", callback_data="help")]
    ])
    return kb

def countries_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton(text=c, callback_data=f"country:{c}")] for c in COUNTRIES]
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def go_to_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Sabon maɓallin don komawa babban menu"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Back to Main Menu", callback_data="back_main")]
    ])
    return kb

# --- Handlers ---

@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    text = (
        "Assalamu alaikum! Ni bot ne wanda zai taimaka maka ka samar da realistic fake identities.\n\n"
        "Danna 'Fake Info' don zaɓar ƙasa."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())

@dp.message(Command(commands=["help"]))
async def cmd_help(message: Message):
    text = (
        "Yadda ake amfani:\n"
        "/start - Fara bot\n"
        "/help - Wannan taimako\n\n"
        "Danna Fake Info -> Zaɓi ƙasa -> Samu fake identity.\n"
        "Note: Data is generated for testing and should not be used for illegal purposes."
    )
    await message.answer(text)

@dp.callback_query(F.data == "menu_fake")
async def callback_menu_fake(query: CallbackQuery):
    await query.message.edit_text(
        "🌍 Please select a country to generate an identity:",
        reply_markup=countries_keyboard()
    )
    await query.answer()

@dp.callback_query(F.data.startswith("country:"))
async def callback_country(query: CallbackQuery):
    payload = query.data.split(":", 1)[1]
    identity = generate_identity(payload)
    
    # Canza rubutun saƙon da ya riga ya wanzu
    await query.message.edit_text(
        text=identity, 
        reply_markup=go_to_main_menu_keyboard()
    )
    await query.answer(text="Generated ✅")

@dp.callback_query(F.data == "back_main")
async def callback_back_main(query: CallbackQuery):
    welcome_text = (
        "Assalamu alaikum! Ni bot ne wanda zai taimaka maka ka samar da realistic fake identities.\n\n"
        "Danna 'Fake Info' don zaɓar ƙasa."
    )
    
    # Canza rubutun saƙon zuwa babban menu
    await query.message.edit_text(
        text=welcome_text, 
        reply_markup=main_menu_keyboard()
    )
    await query.answer()

@dp.callback_query(F.data == "help")
async def callback_help(query: CallbackQuery):
    await query.message.edit_text(
        "Help:\n\nClick Fake Info -> choose country to get fake identity.\n\n"
        "Use /help for commands.",
        reply_markup=main_menu_keyboard()
    )
    await query.answer()

async def main():
    logging.info("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
