from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

Participal = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Проверить Подписку", callback_data="CheckSub"))

MainPanel = ReplyKeyboardMarkup(resize_keyboard=True)
MainPanel.add(KeyboardButton("Главная"))
#MainPanel.add(KeyboardButton("Играть на TON"))
#MainPanel.add(KeyboardButton("Binance"))
#MainPanel.add(KeyboardButton("Рейтинг"))