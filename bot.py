import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not BOT_TOKEN or not ADMIN_CHAT_ID:
    raise ValueError("BOT_TOKEN и ADMIN_CHAT_ID должны быть установлены в переменных окружения!")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния анкеты
class ApplicationForm(StatesGroup):
    age = State()
    nickname = State()
    tiktok = State()
    activity = State()
    contact = State()
    motivation = State()
    experience = State()

# Клавиатура для админа
def get_admin_keyboard(application_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{application_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{application_id}")
        ]
    ])
    return keyboard

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "🎬 *Добро пожаловать в BakiSMP!*\n\n"
        "Ты хочешь стать тиктокером нашего сервера?\n"
        "Тогда давай начнем заполнение анкеты!\n\n"
        "Напиши /apply, чтобы подать заявку.",
        parse_mode="Markdown"
    )

@dp.message(Command("apply"))
async def cmd_apply(message: types.Message, state: FSMContext):
    await state.set_state(ApplicationForm.age)
    await message.answer(
        "📝 *Заполнение анкеты*\n\n"
        "Вопрос 1 из 7:\n"
        "Сколько тебе лет? (напиши цифру)",
        parse_mode="Markdown"
    )

@dp.message(ApplicationForm.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введи число (например: 16)")
        return
    await state.update_data(age=message.text)
    await state.set_state(ApplicationForm.nickname)
    await message.answer(
        "Вопрос 2 из 7:\n"
        "Какой у тебя ник на сервере BakiSMP?"
    )

@dp.message(ApplicationForm.nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await state.set_state(ApplicationForm.tiktok)
    await message.answer(
        "Вопрос 3 из 7:\n"
        "Ссылка на твой TikTok профиль:"
    )

@dp.message(ApplicationForm.tiktok)
async def process_tiktok(message: types.Message, state: FSMContext):
    await state.update_data(tiktok=message.text)
    await state.set_state(ApplicationForm.activity)
    await message.answer(
        "Вопрос 4 из 7:\n"
        "Сколько времени в день ты проводишь на сервере?\n"
        "(например: 3-4 часа)"
    )

@dp.message(ApplicationForm.activity)
async def process_activity(message: types.Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await state.set_state(ApplicationForm.contact)
    await message.answer(
        "Вопрос 5 из 7:\n"
        "Твой контакт для связи (Telegram или Discord):"
    )

@dp.message(ApplicationForm.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(ApplicationForm.motivation)
    await message.answer(
        "Вопрос 6 из 7:\n"
        "Почему именно ты должен стать тиктокером BakiSMP?\n"
        "(напиши пару предложений)"
    )

@dp.message(ApplicationForm.motivation)
async def process_motivation(message: types.Message, state: FSMContext):
    await state.update_data(motivation=message.text)
    await state.set_state(ApplicationForm.experience)
    await message.answer(
        "Вопрос 7 из 7 (последний):\n"
        "Есть ли у тебя опыт монтажа или съемок в Minecraft?"
    )

@dp.message(ApplicationForm.experience)
async def process_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    
    data = await state.get_data()
    
    application_text = (
        f"📩 *НОВАЯ ЗАЯВКА В BAKISMP!*\n"
        f"{'='*30}\n\n"
        f"👤 *Возраст:* {data.get('age')}\n"
        f"🎮 *Ник на сервере:* {data.get('nickname')}\n"
        f"📱 *TikTok:* {data.get('tiktok')}\n"
        f"⏳ *Активность:* {data.get('activity')}\n"
        f"📞 *Контакт:* {data.get('contact')}\n"
        f"✍️ *Мотивация:* {data.get('motivation')}\n"
        f"🎬 *Опыт:* {data.get('experience')}\n"
    )
    
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=application_text,
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(message.from_user.id)
    )
    
    await message.answer(
        "✅ *Твоя заявка успешно отправлена!*\n\n"
        "Она уже у администратора на рассмотрении.\n"
        "Мы свяжемся с тобой в ближайшее время!\n"
        "Спасибо, что хочешь стать частью BakiSMP! ❤️",
        parse_mode="Markdown"
    )
    
    await state.clear()

@dp.callback_query(F.data.startswith("approve_"))
async def approve_application(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"✅ Заявка пользователя одобрена!")
    try:
        await bot.send_message(
            chat_id=user_id,
            text="🎉 *Поздравляем!*\n\n"
                 "Ты принят в команду тиктокеров BakiSMP!\n"
                 "Свяжись с администратором для дальнейших инструкций.\n"
                 "Добро пожаловать! 🚀",
            parse_mode="Markdown"
        )
    except:
        pass
    await callback.answer("Заявка одобрена!")

@dp.callback_query(F.data.startswith("reject_"))
async def reject_application(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"❌ Заявка пользователя отклонена.")
    try:
        await bot.send_message(
            chat_id=user_id,
            text="😔 *К сожалению...*\n\n"
                 "Мы не можем взять тебя в команду тиктокеров BakiSMP сейчас.\n"
                 "Спасибо за проявленный интерес! Возможно, в будущем мы свяжемся с тобой.\n"
                 "Удачи на сервере! ❤️",
            parse_mode="Markdown"
        )
    except:
        pass
    await callback.answer("Заявка отклонена!")

async def main():
    print("Бот BakiSMP запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
