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

#----------------------------------------------------------FUNCTION----------------------------------------------------------#

@dp.message_handler(commands=['start'])
async def cmd_start(msg : types.Message):
    balance = 0
    NumInvited = 0
    if db.sql(f"SELECT userID FROM Subs WHERE userID = {msg.from_user.id}") != []:
        NumInvited, balance = db.sql(f"SELECT Scars, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
    personalLink = f"https://t.me/EvenEasyBot?start={msg.from_user.id}"
    try:
        users = []
        userID = msg.text.split(' ')[1]
        try:
            users = db.sql(f"SELECT UserUsedRefName FROM Subs WHERE userID={userID}")[0][0].split('|')
        except AttributeError:
            users = []
        if str(msg.from_user.id) not in users and str(msg.from_user.id) != userID:
            users.append(str(msg.from_user.id))
            num = db.sql(f"SELECT Scars FROM Subs WHERE userID={userID}")[0][0]
            db.sql(f"UPDATE Subs SET Scars = {num + 1}, UserUsedRefName = '{'|'.join(users)}' WHERE userID={userID}")
    except IndexError:
        pass
    if db.sql(f"SELECT UserID FROM Subs WHERE UserID = {msg.from_user.id}") == []:
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.Participal)
    else:
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.MainPanel)

#------------------------------------------------------------------------#

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

#------------------------------------------------------------------------#


@dp.message_handler(state=Form.walletCode)
async def WalletCode(msg : types.Message, state : FSMContext):
    await state.finish()
    personalLink = f"https://t.me/EvenEasyBot?start={msg.from_user.id}"
    if msg.text == "Главное меню" or msg.text == '/start':
        balance = 0
        NumInvited = 0
        if db.sql(f"SELECT userID FROM Subs WHERE userID = {msg.from_user.id}") != []:
            NumInvited, balance = db.sql(f"SELECT Scars, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.MainPanel)
        return
    db.sql(f"UPDATE Subs SET WalletCode = '{msg.text}' WHERE UserID = {msg.from_user.id}")
    await msg.answer(db.ReffLink.format(personalLink), reply_markup=Markups.GoToMenu)

#----------------------------------------------------------CALL-BACK-BTTN-CLICK----------------------------------------------------------#

@dp.callback_query_handler(text=["CheckSub", "CheckMyScars", "ChangeWalletCode", "MyReffLink", "GoToMainMenu"])
async def callback(call : types.CallbackQuery):

    if call.data == "CheckSub":
        try:
            user = await bot.get_chat_member(ChannelID, call.from_user.id)

        except Exception as E:
            await call.message.answer("❌ Вы не Подписаны.")
            print(f"ERROR - {E}")
        
        try:
            if db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}") != []:
                await call.message.answer("ℹ️ Вы уже являетесь пользователем этого бота.")
                return
            url = f"https://t.me/EvenEasyBot?start={user.user.id}"
            if db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}") == []:
                db.sql(f"INSERT INTO Subs VALUES ({user.user.id}, '{url}' ,0, 0, '{user.user.full_name}', 't', '', '')")
            elif db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}")[0][0] == 'f':
                db.sql(f"UPDATE Subs SET IsAParticipant = 't' WHERE USERID = {user.user.id}")
            await bot.send_photo(call.message.chat.id, open('photo.jpg', 'rb'), caption=db.ValidText)
            await Form.walletCode.set()
        except Exception as E:
            print(f"ERROR - {E}")

    elif call.data == "GoToMainMenu":
        await call.message.answer(db.MainText.format(call.from_user.first_name), reply_markup=Markups.MainPanel)

    elif call.data == "ChangeWalletCode":
        await call.message.answer("Введите новий wallet code")
        await Form.walletCode.set()

    elif call.data == "MyReffLink":
        refLink = db.sql(f'SELECT ReferalLink FROM Subs WHERE UserID = {call.from_user.id}')[0][0]
        await call.message.answer(f"Ваша реферальная ссылка : \n{refLink}")

    else:
        Scars = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {call.from_user.id}")[0][0]
        await call.message.answer(f"Кол-во ваших баллов : {Scars}")

#---------------------------------RUN-THE-BOT-------------------------------------#

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)