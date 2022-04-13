from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

Participal = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Проверить Подписку", callback_data="CheckSub"))
def MainPanel(isOwner, isMember = False, isSubs = False):
    MainPanel = InlineKeyboardMarkup()
    if isMember:
        MainPanel.add(
            InlineKeyboardButton(text="Мои балы", callback_data="CheckMyScars"),
            InlineKeyboardButton(text="Изменить Wallet code", callback_data="ChangeWalletCode")
        )
    MainPanel.add(InlineKeyboardButton(text="Моя реферальная ссылка", callback_data="MyReffLink"))
    if isSubs:
        MainPanel.add(InlineKeyboardButton(text="Проверить Подписку", callback_data="CheckSub"))
    if isOwner:
        MainPanel.add(InlineKeyboardButton(text="Список", callback_data="list"))
    return MainPanel

GoToMenu = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Главное меню", callback_data="GoToMainMenu"))

def MainBttnsPanel(isOwner):
    MainBttnsPanel = ReplyKeyboardMarkup(resize_keyboard=True)
    MainBttnsPanel.add(KeyboardButton("Мои балы"))
    MainBttnsPanel.add(KeyboardButton("Изменить Wallet code"))
    MainBttnsPanel.add(KeyboardButton("Моя реферальная ссылка"))
    if isOwner:
        MainBttnsPanel.add(KeyboardButton("Список"))
    return MainBttnsPanel
