import aiogram
import config, logging, Markups
from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from BaseData import BaseData

logging.basicConfig(level=logging.INFO)
bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
ChannelID = "@testchnbot"

db = BaseData("basedata.db")

class Form(StatesGroup):
    walletCode = State()

@dp.message_handler(commands=['start'])
async def cmd_start(msg : types.Message):
    balance = 0
    NumInvited = 0
    if db.sql(f"SELECT userID FROM Subs WHERE userID = {msg.from_user.id}") != []:
        NumInvited, balance = db.sql(f"SELECT UsersUsesLink, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
    personalLink = f"https://t.me/EvenEasyBot?start={msg.from_user.id}"
    try:
        userID = msg.text.split(' ')[1]
        num = db.sql(f"SELECT UsersUsesLink FROM Subs WHERE userID={userID}")[0][0]
        db.sql(f"UPDATE Subs SET UsersUsesLink = {num + 1} WHERE userID={userID}")
    except IndexError:
        pass
    
    await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.Participal)
@dp.message_handler(commands=['send'])
async def sender(message : types.Message):
    try:
        user = await bot.get_chat_member(ChannelID, message.from_user.id)
    except:
        await message.answer("Вас нет в канале")
    if user.is_chat_admin():
        await bot.send_message(ChannelID,' '.join((message.text.split(' '))[1::]))
    else:
        await message.answer("У вас нет права писать сообщение в канал")

@dp.message_handler()
async def function(msg : types.Message):
    if msg.text == "Главная":
        balance = 0
        NumInvited = 0
        if db.sql(f"SELECT userID FROM Subs WHERE userID = {msg.from_user.id}") != []:
            NumInvited, balance = db.sql(f"SELECT UsersUsesLink, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
        personalLink = f"https://t.me/EvenEasyBot?start={msg.from_user.id}"
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.Participal)
    elif msg.text == "Рейтинг" and (await bot.get_chat_member(ChannelID, msg.from_user.id)).is_chat_admin:
        message = "Наш ТОП\n"
        i = 1
        for name, scars in db.sql("SELECT UserName, UsersUsesLink FROM Subs ORDER BY UsersUsesLink DESC LIMIT 10"):
            message += f"[ {i} ] {name} - {scars}\n"
            i += 1
        await msg.answer(message)

@dp.message_handler(state=Form.walletCode)
async def WalletCode(msg : types.Message, state : FSMContext):
    await state.finish()
    if msg.text == "Главная":
        balance = 0
        NumInvited = 0
        if db.sql(f"SELECT userID FROM Subs WHERE userID = {msg.from_user.id}") != []:
            NumInvited, balance = db.sql(f"SELECT UsersUsesLink, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
        personalLink = f"https://t.me/EvenEasyBot?start={msg.from_user.id}"
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.Participal)
        return
    db.sql(f"UPDATE Subs SET WalletCode = '{msg.text}' WHERE UserID = {msg.from_user.id}")
    await msg.answer(db.ReffLink)

@dp.callback_query_handler(text=["CheckSub"])
async def callback(call : types.CallbackQuery):
    try:
        user = await bot.get_chat_member(ChannelID, call.from_user.id)
        url = f"https://t.me/EvenEasyBot?start={user.user.id}"
        if db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}") == []:
            db.sql(f"INSERT INTO Subs VALUES ({user.user.id}, '{url}' ,0, 0, '{user.user.full_name}', 't')")
        elif db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}")[0][0] == 'f':
            db.sql(f"UPDATE Subs SET IsAParticipant = 't' WHERE USERID = {user.user.id}")
        await call.message.answer(db.ValidText)
        await Form.walletCode.set()
    except Exception as E:
        await call.message.answer("❌ Вы не Подписаны.")
        print(f"ERROR - {E}")
    

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)