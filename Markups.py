from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

Participal = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Проверить Подписку", callback_data="CheckSub"))

MainPanel = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Мои балы", callback_data="CheckMyScars"),
    InlineKeyboardButton(text="Изменить Wallet code", callback_data="ChangeWalletCode"),
    InlineKeyboardButton(text="Моя реферальная ссылка ", callback_data="MyReffLink")
)
MainPanel.add(InlineKeyboardButton(text="Проверить Подписку", callback_data="CheckSub"))

GoToMenu = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Главное меню", callback_data="GoToMainMenu"))
