from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *
import os
import asyncio

api = "7843366745:AAEDOYZz8HrihRcbDMEiihhhIRScmTCuhBk"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
button3 = KeyboardButton(text="Купить")
button4 = KeyboardButton(text="Регистрация")
kb.add(button).add(button2).add(button3).add(button4)


inline_kb = InlineKeyboardMarkup(resize_keyboard=True)
button_calories = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
inline_keyboard = InlineKeyboardMarkup()

for i in range(1, 5):
    button = InlineKeyboardButton(f"Product{i}", callback_data="product_buying")
    inline_keyboard.add(button)
inline_kb.add(button_calories, button_formulas)
product_images = {
    1: 'photo/1.png',
    2: 'photo/2.png',
    3: 'photo/3.png',
    4: 'photo/4.png'
}

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()

@dp.message_handler(text="Регистрация")
async def sign_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    username = message.text
    if not is_included(username):
        await state.update_data(username=username)
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()
    else:
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    if 120 >= int(message.text) >= 0:
        await state.update_data(age=int(message.text))
        data = await state.get_data()
        add_user(data["username"], data["email"], data["age"])
        await message.answer("Регистрация прошла успешно")
        await state.finish()
    else:
        await message.answer("Возраст должен быть в диапозоне от 0 до 120")
        await RegistrationState.age.set()


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    for i in range(1, 5):
        product_info = f'Название: Product{i} | Описание: описание {i} | Цена: {i * 100}'
        await message.answer(product_info)
        with open(product_images[i], 'rb') as photo:
            await message.answer_photo(photo=photo)
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_keyboard)

@dp.message_handler(text="Информация")
async def info(message):
        with open("photo/info.png", "rb") as img:
            await message.answer_photo(img, caption="Это лучший магазин всех времён!", reply_markup=kb)

@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.answer("Вы успешно приобрели продукт!")
    await bot.send_message(call.from_user.id, "Вы успешно приобрели продукт!")


@dp.message_handler(text=["/start"])
async def start_message(message):
    await message.answer(f"Привет,{message.from_user.username}! Я бот, помогающий твоему здоровью.", reply_markup=kb)



@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("BMR = 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5")
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer("Введите свой возраст")
    await UserState.age.set()
    await call.answer()

@dp.message_handler(state=UserState.age)
async def set_growth(message,state):
    await state.update_data(a=message.text)
    await message.answer("Введите свой рост")
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message,state):
    await state.update_data(b=message.text)
    await message.answer("Введите свой вес")
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(c=message.text)
    data = await state.get_data()
    age = int(data.get('a'))
    growth = int(data.get('b'))
    weight = int(data.get('c'))
    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f"Ваша норма ЧЛЕНОВ: {calories}")

@dp.message_handler()
async def all_messages(message: types.Message):
    print("Введите команду /start, чтобы начать общение")
    await message.answer("Введите команду /start, чтобы начать общение")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

