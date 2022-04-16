import aiogram
import config, logging, Markups, os
from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from BaseData import BaseData

logging.basicConfig(level=logging.INFO)
bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
ChannelID = "@Qredo_Russian"
BotName = "Qredo_Russia_AirDrop_bot"

db = BaseData("basedata.db")

class Form(StatesGroup):
    walletCode = State()

async def CheckSubsMembers():
    print("CHECK MEMBERS")
    for i, name in db.sql("SELECT UserId, UserName FROM Subs"):
        print("USER", i)
        linkID = db.sql(f"SELECT UsedLinkID FROM Subs WHERE UserID = {i}")[0][0]
        try:
            userName = '' if db.sql(f"SELECT UserName FROM Subs WHERE UserID = {i}")[0][0] == '' else db.sql(f"SELECT UserName FROM Subs WHERE UserID = {i}")[0][0]
        except:
            userName = ''
        print(linkID)
        member1 = await bot.get_chat_member(ChannelID, i)
        if not member1.is_chat_member() and linkID == '' and userName != '':
            db.sql(f"UPDATE Subs SET UserName = '' WHERE UserID = {i}")
            await bot.send_message(member1.user.id, "❌Вы уже не участвуете в конкурсе, Вы покинули группу [Qredo Russian](https://t.me/Qredo_Russian)", reply_markup=Markups.Participal, parse_mode="Markdown")
            return
        arr = db.sql(f"SELECT UserID FROM Subs WHERE UsedLinkID = '{i}'")
        print("USED LINK")
        for id in arr:
            print(id[0])
            member = await bot.get_chat_member(ChannelID, id[0])
            try:
                scarsNow = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {i}")[0][0] if db.sql(f"SELECT Scars FROM Subs WHERE UserID = {i}")[0][0] != None else 0
            except:
                scarsNow = 0
            scars = len(arr)
            print(scars, scars)
            print(id[0],"Is",member.is_chat_member())
            print(scars > scarsNow)
            if not member.is_chat_member():
                db.sql(f"UPDATE Subs SET UsedLinkID = '', UserName = '' WHERE UserID = {id[0]}")
                print("Is not member")
                db.sql(f"UPDATE Subs SET Scars = {scars - 1} WHERE userID={i}")
                print("Updated")
                user = await bot.get_chat_member(ChannelID, i)
                await bot.send_message(member.user.id, "❌Вы уже не участвуете в конкурсе, Вы покинули группу [Qredo Russian](https://t.me/Qredo_Russian)", reply_markup=Markups.Participal, parse_mode="Markdown")
                await bot.send_message(user.user.id, f"Участник {member.user.mention} покинул чат, у Вас минус 1 балл 😔")
                print("Sended message")

def InsertData(UserID, ID = ''):
    if db.sql(f"SELECT UserID FROM Subs WHERE UserID = {UserID}") == []:
        db.sql(f"INSERT INTO Subs(UserID, UsedLinkID) VALUES ({UserID},'{ID}')")

async def SetScars(name, myID):
    print("SET SCARS")
    if name == '' or myID == name:
        return
    print("is not empty")
    arr = db.sql(f"SELECT UserID FROM Subs WHERE UsedLinkID = '{name}'")
    scars = len(arr)
    print(scars)
    try:
        scarsold = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {name}")[0][0] if db.sql(f"SELECT Scars FROM Subs WHERE UserID = {name}")[0][0] != None else 0
    except:
        scarsold = 0
    print(scarsold)
    db.sql(f"UPDATE Subs SET Scars = {scars} WHERE UserID = {name}")
    print("Updated")
    if scars == 1 and scarsold < 1:
        await bot.send_message(name,"""🔥Поздравляю, Вы участвуете в конкурсе!
По Вашей ссылке перешел 1 человек

 Чем больше людей перейдет по Вашей ссылке, тем больше шансов на победу! 🤑""", reply_markup=Markups.MainBttnsPanel(False))
        print("Message sended")
#----------------------------------------------------------FUNCTION----------------------------------------------------------#

@dp.message_handler(commands=['start'])
async def cmd_start(msg : types.Message):
    await CheckSubsMembers()
    member = await bot.get_chat_member(ChannelID, msg.from_user.id)
    balance = 0
    NumInvited = 0
    if db.sql(f"SELECT UserName FROM Subs WHERE userID = {msg.from_user.id}") != []:
        NumInvited, balance = db.sql(f"SELECT Scars, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
    personalLink = f"https://t.me/{BotName}?start={msg.from_user.id}"
    if db.sql(f"SELECT UserID FROM Subs WHERE UserID = {msg.from_user.id}") == []:
        try:
            userID = msg.text.split(' ')[1]
            InsertData(msg.from_user.id,userID)
        except IndexError:
            InsertData(msg.from_user.id)
    else:
        try:
            print("IS is BD")
            userID = msg.text.split(' ')[1]
            db.sql(f"UPDATE Subs SET UsedLinkID = '{userID}' WHERE UserID = {msg.from_user.id}")
            print("LINK IS SETED")
        except IndexError:
            print("ENDEX ERROR")
    if db.sql(f"SELECT UserName FROM Subs WHERE UserID = {msg.from_user.id}")[0][0] == None or db.sql(f"SELECT UserName FROM Subs WHERE UserID = {msg.from_user.id}")[0][0] == '':
        db.sql(f"UPDATE Subs SET UserName = '{str(msg.from_user.mention)}' WHERE UserID = {msg.from_user.id}")
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.Participal, parse_mode="Markdown")
    else:
        Scars = db.sql(f"SELECT Scars FROM Subs WHERE userID={msg.from_user.id}")[0][0] if db.sql(f"SELECT Scars FROM Subs WHERE userID={msg.from_user.id}")[0][0] != None else 0
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.MainPanel(member.is_chat_creator(), Scars >= 1, member.is_chat_member()), parse_mode="Markdown")

@dp.message_handler(commands=['sql'])
async def sqlCommand(sql : types.Message):
    user = await bot.get_chat_member(ChannelID, sql.from_user.id)
    if user.is_chat_creator():
        await sql.answer(db.sql(' '.join(sql.text.split(' ')[1::])))
#------------------------------------------------------------------------#

@dp.message_handler(state=Form.walletCode)
async def WalletCode(msg : types.Message, state : FSMContext):
    await state.finish()
    personalLink = f"https://t.me/{BotName}?start={msg.from_user.id}"
    user = await bot.get_chat_member(ChannelID, msg.from_user.id)
    if msg.text == "Главное меню" or msg.text == '/start':
        balance = 0
        NumInvited = 0
        Scars = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {msg.from_user.id}")[0][0]
        if db.sql(f"SELECT UserName FROM Subs WHERE userID = {msg.from_user.id}")[0][0] != None:
            NumInvited, balance = db.sql(f"SELECT Scars, Balance FROM Subs WHERE userID = {msg.from_user.id} LIMIT 1")[0]
        await msg.answer(db.MainText.format(msg.from_user.first_name, balance, NumInvited, personalLink), reply_markup=Markups.MainPanel(False, Scars >= 1, user.is_chat_member()))
        return
    db.sql(f"UPDATE Subs SET WalletCode = '{msg.text}' WHERE UserID = {msg.from_user.id}")
    LinkID = '' if db.sql(f"SELECT UsedLinkID FROM Subs WHERE UserID = {msg.from_user.id}") == [] else db.sql(f"SELECT UsedLinkID FROM Subs WHERE UserID = {msg.from_user.id}")[0][0]
    print(LinkID, "Send to SET SCARS")
    await SetScars(LinkID, msg.from_user.id)
    await msg.answer(db.Form3Text, reply_markup=Markups.MainPanel(user.is_chat_creator()), parse_mode="Markdown")

@dp.message_handler()
async def Functions(msg : types.Message):
    if msg.text == "Мои баллы":
        Scars = 0 if db.sql(f"SELECT Scars FROM Subs WHERE UserID = {msg.from_user.id}") == [] else db.sql(f"SELECT Scars FROM Subs WHERE UserID = {msg.from_user.id}")[0][0]
        await msg.answer(f"Кол-во ваших баллов : {Scars}")
    elif msg.text == "Изменить Wallet code":
        await msg.answer("Введите новий Wallet Code:")
        await Form.walletCode.set()
    elif msg.text == "Моя реферальная ссылка":
        refLink = f"https://t.me/{BotName}?start={msg.from_user.id}"
        await msg.answer(f"Ваша реферальная ссылка :\n{refLink}\n*для участия в конкурсе, пригласите минимум 1 человека")
    await CheckSubsMembers()
#----------------------------------------------------------CALL-BACK-BTTN-CLICK----------------------------------------------------------#

@dp.callback_query_handler(text=["CheckSub", "CheckMyScars", "ChangeWalletCode", "MyReffLink", "GoToMainMenu", "list"])
async def callback(call : types.CallbackQuery):
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
            print(1)
            if db.sql(f"SELECT UserName FROM Subs WHERE UserID = {user.user.id}")[0][0] != None:
                await bot.send_photo(call.message.chat.id, open('photo.jpg', 'rb'), caption=db.ValidText, parse_mode="Markdown")
                await Form.walletCode.set()
                return
            url = f"https://t.me/{BotName}?start={user.user.id}"
            print(2)
            if db.sql(f"SELECT UserName FROM Subs WHERE UserID = {user.user.id}")[0][0] == None:
                db.sql(f"UPDATE Subs SET Scars = 0,Balance = 0, UserName = '{str(user.user.mention)}', WalletCode = '' WHERE UserID = {call.from_user.id}")

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
        await call.message.answer("Введите новий Wallet Code:")
        await Form.walletCode.set()

    elif call.data == "MyReffLink":
        refLink = f"https://t.me/{BotName}?start={call.from_user.id}"
        await call.message.answer(f"Ваша реферальная ссылка :\n{refLink}\n*для участия в конкурсе, пригласите минимум 1 человека")
    elif call.data == "list":
        with open("MembersList.txt", 'a', encoding='utf8') as file:
            file.truncate(0)
            for name, WalletCode, Scars in db.sql("SELECT UserName, WalletCode, Scars FROM Subs ORDER BY Scars DESC"):
                file.write(f"[ {name} ] , {WalletCode} - {Scars}\n")
        with open(file.name, 'rb') as f:
            try:
                await bot.send_document(call.from_user.id, f)
            except aiogram.utils.exceptions.BadRequest:
                await bot.send_message(call.from_user.id, "Файл пустой")
    else:
        Scars = db.sql(f"SELECT Scars FROM Subs WHERE UserID = {call.from_user.id}")[0][0]
        await call.message.answer(f"Кол-во ваших баллов : {Scars}")

#---------------------------------RUN-THE-BOT-------------------------------------#

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)