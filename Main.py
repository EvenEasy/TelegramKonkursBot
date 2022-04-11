import config, logging, Markups
from aiogram import Dispatcher, Bot, types, executor
from BaseData import BaseData


logging.basicConfig(level=logging.INFO)
bot = Bot(config.TOKEN)
dp = Dispatcher(bot)
ChannelID = "@testchnbot"

db = BaseData("basedata.db")

@dp.message_handler(commands=['start'])
async def cmd_start(msg : types.Message):
    balance = 0 #+ db.sql(f"SELECT Balance FROM Subs WHERE userID = {msg.from_user.id}")[0][0]
    NumInvited = 0 #+ db.sql(f"SELECT UsersUsesLink FROM Subs WHERE userID = {msg.from_user.id}")[0][0]
    personalLink = f"https://t.me/EvenEasyBot?start={msg.from_user.id}"
    ref = msg.text.split(' ')[1]
    db.sql(f"UPDATE Subs SET UsersUsesLink += 1 WHERE userID={ref}")
    msg1 = f"""{msg.from_user.first_name}, рад тебя видеть. 

У нас тут конкурс. 
Разыгрываем Qredo токены в количестве 500 штук🔥

Оценочная стоимость более 400 TON (примерно 1500$)🔥

Условия: 
 1. Быть подписанными на @Qredo_Russian
 2. Создать Qredo Fund (https://t.me/Qredo_Russian/6084) и указать в боте Wallet code
 3. Пригласить людей по реферальной ссылке.
 
 Твой баланс : {balance}
 Кол-во приглашённых : {NumInvited}

 Твоя персональная ссылка : {personalLink}
 
 """
    await msg.answer(msg1, reply_markup=Markups.Participal)

@dp.callback_query_handler(text=["Participal"])
async def callback(call : types.CallbackQuery):
    try:
        url = await bot.create_chat_invite_link(ChannelID)
        user = await bot.get_chat_member(ChannelID, call.from_user.id)
        print(db.sql(f"SELECT userID FROM Subs WHERE UserID = {user.user.id}"))
        if db.sql(f"SELECT userID FROM Subs WHERE UserID = {user.user.id}") == []:
            db.sql(f"INSERT INTO Subs VALUES ({user.user.id}, '{url.name}' ,0, 0)")
        await call.answer("ℹ️ Вы уже являетесь пользователем этого бота")
    except Exception as E:
        await call.answer("❌ Вы не Подписаны.")
        print(f"ERROR - {E}")
    

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)