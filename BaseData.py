import sqlite3

class BaseData:

    MainText = """{0}, рад тебя видеть. 

У нас тут конкурс. 
Разыгрываем Qredo токены в количестве 500 штук🔥

Оценочная стоимость более 400 TON (примерно 1500$)🔥

Условия: 
 1. Быть подписанными на @Qredo_Russian
 2. Создать Qredo Fund (https://t.me/Qredo_Russian/6084) и указать в боте Wallet code
 3. Пригласить людей по реферальной ссылке.
 
 Твой баланс : {1}
 Кол-во приглашённых : {2}

 Твоя персональная ссылка : 
 {3}
 
 """

    ValidText = """текст
    інструкція
    текст
    інструкція
    і знову текст)"""

    ReffLink = """Referral link
    Tom and jerry))))"""


    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.curson = self.connection.cursor()
    def sql(self, sql):
        with self.connection:
            return self.curson.execute(sql).fetchall()