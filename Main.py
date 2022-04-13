import config, logging, Markups, os
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

async def CheckSubsMembers():
    for i in db.sql("SELECT UserID FROM Subs"):
        arr = (db.sql(f"SELECT UserUsedRefName FROM Subs WHERE UserID = {i[0]}")[0][0]).split('|') if db.sql(f"SELECT UserUsedRefName FROM Subs WHERE UserID = {i[0]}")[0][0] != '' else [] 
        if arr != []:
            for id in arr[1::]:
                member = await bot.get_chat_member(ChannelID, id)
                if not member.is_chat_member():
                    scars = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {i[0]}")[0][0]
                    arr.remove(id)
                    db.sql(f"UPDATE Subs SET Scars = {scars - 1}, UserUsedRefName = '{'|'.join(arr)}' WHERE userID={i[0]}")
                    user = await bot.get_chat_member(ChannelID, i[0])
                    await bot.send_message(member.user.id, "Ви уже не участвуете в конкурсе")
                    await bot.send_message(user.user.id, f"Участник {member.user.mention} покинул чат, у Вас минус 1 балл 😔")


#----------------------------------------------------------FUNCTION----------------------------------------------------------#

@dp.message_handler(commands=['start'])
async def cmd_start(msg : types.Message):
    await CheckSubsMembers()
    member = await bot.get_chat_member(ChannelID, msg.from_user.id)
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
            if num + 1 == 1:
                await bot.send_message(userID, """🔥Поздравляю, Вы участвуете в конкурсе!
По Вашей ссылке перешел 1 человек

 Чем больше людей перейдет по Вашей ссылке, тем больше шансов на победу! 🤑""", reply_markup=Markups.MainBttnsPanel(member.is_chat_creator()))
            db.sql(f"UPDATE Subs SET Scars = {num + 1}, UserUsedRefName = '{'|'.join(users)}' WHERE userID={userID}")
    except IndexError:
        pass
    if db.sql(f"SELECT UserID FROM Subs WHERE UserID = {msg.from_user.id}") == []:
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.Participal, parse_mode="Markdown")
    else:
        Scars = db.sql(f"SELECT Scars FROM Subs WHERE userID={msg.from_user.id}")[0][0]
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.MainPanel(member.is_chat_creator(), Scars >= 1, member.is_chat_member), parse_mode="Markdown")

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
    user = await bot.get_chat_member(ChannelID, msg.from_user.id)
    if msg.text == "Главное меню" or msg.text == '/start':
        balance = 0
        NumInvited = 0
        Scars = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {msg.from_user.id}")[0][0]
        if db.sql(f"SELECT userID FROM Subs WHERE userID = {msg.from_user.id}") != []:
            NumInvited, balance = db.sql(f"SELECT Scars, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.MainPanel(False, Scars >= 1, user.is_chat_member))
        return
    db.sql(f"UPDATE Subs SET WalletCode = '{msg.text}' WHERE UserID = {msg.from_user.id}")
    await msg.answer(db.Form3Text, reply_markup=Markups.MainPanel(user.is_chat_creator()), parse_mode="Markdown")

@dp.message_handler()
async def Functions(msg : types.Message):
    await CheckSubsMembers()
    if msg.text == "Мои балы":
        Scars = 0 if db.sql(f"SELECT Scars FROM Subs WHERE UserID = {msg.from_user.id}") == [] else db.sql(f"SELECT Scars FROM Subs WHERE UserID = {msg.from_user.id}")[0][0]
        await msg.answer(f"Кол-во ваших баллов : {Scars}")
    elif msg.text == "Изменить Wallet code":
        await msg.answer("Введите новий wallet code")
        await Form.walletCode.set()
    elif msg.text == "Моя реферальная ссылка":
        refLink = f"https://t.me/EvenEasyBot?start={msg.from_user.id}"
        await msg.answer(f"Ваша реферальная ссылка :\n{refLink}\n*для участия в конкурсе, пригласите минимум 1 человека")
#----------------------------------------------------------CALL-BACK-BTTN-CLICK----------------------------------------------------------#

@dp.callback_query_handler(text=["CheckSub", "CheckMyScars", "ChangeWalletCode", "MyReffLink", "GoToMainMenu", "list"])
async def callback(call : types.CallbackQuery):
    await CheckSubsMembers()
    try:
        await call.answer()
    except:
        pass
    if call.data == "CheckSub":
        user = await bot.get_chat_member(ChannelID, call.from_user.id)
        if not user.is_chat_member():
            await call.message.answer("❌ Вы не Подписаны.")
            return
        
        try:
            if db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}") != []:
                await call.message.answer("ℹ️ Вы уже являетесь пользователем этого бота.")
                return
            url = f"https://t.me/EvenEasyBot?start={user.user.id}"
            if db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}") == []:
                db.sql(f"INSERT INTO Subs VALUES ({user.user.id}, '{url}' ,0, 0, '{str(user.user.mention)}', 't', '', '')")
            elif db.sql(f"SELECT IsAParticipant FROM Subs WHERE UserID = {user.user.id}")[0][0] == 'f':
                db.sql(f"UPDATE Subs SET IsAParticipant = 't' WHERE USERID = {user.user.id}")
            await bot.send_photo(call.message.chat.id, open('photo.jpg', 'rb'), caption=db.ValidText, parse_mode="Markdown")
            await Form.walletCode.set()
        except Exception as E:
            print(f"ERROR - {E}")

    elif call.data == "GoToMainMenu":
        user = await bot.get_chat_member(ChannelID, call.from_user.id)
        try:
            Scars = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {call.from_user.id}")[0][0]
        except IndexError:
            Scars = 0
        await call.message.answer(db.MainText.format(call.from_user.first_name), reply_markup=Markups.MainPanel(user.is_chat_creator(), Scars >= 1, user.is_chat_member), parse_mode="Markdown")

    elif call.data == "ChangeWalletCode":
        await call.message.answer("Введите новий wallet code")
        await Form.walletCode.set()

    elif call.data == "MyReffLink":
        refLink = f"https://t.me/EvenEasyBot?start={call.from_user.id}"
        await call.message.answer(f"Ваша реферальная ссылка :\n{refLink}\n*для участия в конкурсе, пригласите минимум 1 человека")
    elif call.data == "list":
        with open("MembersList.txt", 'a', encoding='utf8') as file:
            file.truncate(0)
            for name, WalletCode, Scars in db.sql("SELECT UserName, WalletCode, Scars FROM Subs ORDER BY Scars DESC"):
                file.write(f"[ {name} ] , {WalletCode} - {Scars}\n")
        with open(file.name, 'rb') as f:
            await bot.send_document(call.from_user.id, f)
    else:
        Scars = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {call.from_user.id}")[0][0]
        await call.message.answer(f"Кол-во ваших баллов : {Scars}")

#---------------------------------RUN-THE-BOT-------------------------------------#

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)