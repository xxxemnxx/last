# -*- coding: utf-8 -*-
# Coded by ayiak.t.me

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient 
from typing import Dict, List, Union

api_id = 19358020 
api_hash = 'de33bd71c8d49212c32af0bc10d67617'
bot_token = "6785681031:AAFrVf0W4c_lwXWcMY0niqC0PGxzm18sLjo" 

app = Client("test", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

MONGO_URI = "mongodb+srv://bossnetworkk10222a:AZE1234AZE@cluster0.jvr876w.mongodb.net/?retryWrites=true&w=majority"
MONGO_DB = "start_checker"  #* veritabanı adı
OWNER_ID = 6587023363 # sahibin idsi
KULLANIM_HAK_SAATI = 24 #* 24 saatlik kullanım hakkı

#! Bu kısmı değiştirmeyin
START_TIMES = {}
AUTHS = []
UNAUTHS = filters.user()

class Database:
    def __init__(self, db_url: str, db_name: str):
        self.db_url = db_url
        self.db_name = db_name
        self.client = AsyncIOMotorClient(self.db_url)
        self.db_ = self.client[self.db_name]
        self.db = self.db_["start_times"]
        self.time_format = "%Y-%m-%d %H:%M:%S"
        self.usage_limit_minutes =  KULLANIM_HAK_SAATI * 60
        
    async def auth(self, id: int) -> None:
        data = await self.db.find_one({"auths": "auths"})
        if not data:
            await self.db.insert_one({"auths": "auths", "ids": [id]})
        else:
            await self.db.update_one({"auths": "auths"}, {"$push": {"ids": id}}, upsert=True)
        if id not in AUTHS:
            AUTHS.append(id)
        if id in UNAUTHS:
            UNAUTHS.remove(id)
        
    async def unauth(self, id: int) -> None:
        data = await self.db.find_one({"auths": "auths"})
        if not data:
            return
        else:
            await self.db.update_one({"auths": "auths"}, {"$pull": {"ids": id}}, upsert=True)
            AUTHS.remove(id)
            UNAUTHS.add(id)
            
    async def is_authed(self, id: int) -> bool:
        data = await self.db.find_one({"auths": "auths"})
        if not data:
            return False
        else:
            AUTHS = data["ids"]
            if id in AUTHS:
                return True
            else:
                return False
            
    async def get_auths(self) -> List[int]:
        data = await self.db.find_one({"auths": "auths"})
        if not data:
            return []
        else:
            AUTHS = data["ids"]
            return AUTHS
                
    async def start(self, id: int) -> None:
        data = await self.db.find_one({"id": id})
        if not data:
            await self.db.insert_one({"id": id, "start_time": datetime.now().strftime(self.time_format)})
        else:
            #await self.db.update_one({"id": id}, {"$set": {"start_time": datetime.now().strftime(self.time_format)}}, upsert=True)
            pass
        START_TIMES[id] = datetime.now()
        
    async def get(self, id: int) -> datetime:
        data = await self.db.find_one({"id": id})
        if not data:
            return None
        else:
            START_TIMES[id] = datetime.strptime(data["start_time"], self.time_format)
            return datetime.strptime(data["start_time"], self.time_format)
 
    async def is_usaged(self, id: int) -> bool:
        data = await self.db.find_one({"id": id})
        if not data:
            return False
        else:
            START_TIMES[id] = datetime.strptime(data["start_time"], self.time_format)
            start_time = datetime.strptime(data["start_time"], self.time_format)
            if (datetime.now() - start_time).seconds / 60 > self.usage_limit_minutes:
                return False
            else:
                return True
            
    async def get_all(self) -> Dict[int, datetime]:
        data = self.db.find() 
        datas = {}
        async for d in data:
            if "id" in d and "start_time" in d:
                datas[d["id"]] = datetime.strptime(d["start_time"], self.time_format)
        return datas     
db = Database(MONGO_URI, MONGO_DB)


def start_time_check(func):
    async def wrapper(_, m: Message):
        if m.from_user.id == OWNER_ID: # SADECE SAHİBİNİN KULLANMASI İÇİN  
            return await func(_, m)
        
        async def checker(id) -> bool:
            if id in AUTHS: 
                return True
            if id in START_TIMES:
                now = datetime.now()
                if (now - START_TIMES[id]).seconds / 60 > db.usage_limit_minutes:
                    return False
                else:
                    return True
            else:
                return None 
            
        statu = await checker(m.from_user.id)
        if statu == False:
            print(f"Test: Command is blocked for {m.from_user.id}")
            return
        elif statu == None:
            await db.start(m.from_user.id)
            print(f"Test: {m.from_user.id} is started")
        print(f"Test: {m.from_user.id} is not blocked")
        return await func(_, m)            
    return wrapper 

# Authorize
@app.on_message(filters.command("auth") & filters.user(OWNER_ID))
async def auth(_, m: Message):
    
    async def loud_auth(id: int) -> Union[bool, str]:
        try:
            await app.send_message(id, "Artık yetkili oldun") # değiştirirsiniz
            return True
        except Exception as e:
            print(f"Test: {e}")
            return str(e)
            
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False
    
    loud = True
    if len(m.command) >= 2:
        if is_int(m.command[1]):
            if len(m.command) == 3:
                if m.command[2] == "-noloud":
                    loud = False 
                else:
                    await m.reply_text("Geçersiz komut")
                    return
            id = int(m.command[1])
            if await db.is_authed(id):
                await m.reply_text("Bu kişi zaten yetkili")
                return
            else:
                await db.auth(id)
                if loud:
                    statu = await loud_auth(id)
                    if statu == True:
                        await m.reply_text(f"{id} yetkili olarak eklendi")
                        return
                    else:
                        await m.reply_text(f"{id} yetkili olarak eklendi ama mesaj gönderilemedi: {statu}") 
                        return
                    
                await m.reply_text(f"{id} yetkili olarak eklendi\nBildirim istenmedi.")
                return
        else:
            await m.reply_text("Geçersiz id")
            return
            
    else:
        await m.reply_text("Geçersiz komut")
        return
        
# Unauthorize
@app.on_message(filters.command("unauth") & filters.user(OWNER_ID))
async def unauth(_, m: Message):
    async def loud_unauth(id: int) -> Union[bool, str]:
        try:
            await app.send_message(id, "Artık yetkili değilsin") # değiştirirsiniz
            return True
        except Exception as e:
            print(f"Test: {e}")
            return str(e)
    
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False
    
    loud = True
    if len(m.command) == 2:
        if is_int(m.command[1]):
            if len(m.command) == 3:
                if m.command[2] == "-noloud":
                    loud = False 
                else:
                    await m.reply_text("Geçersiz komut")
                    return
                
            id = int(m.command[1])
            if await db.is_authed(id):
                await db.unauth(id)
                if loud:
                    statu = await loud_unauth(id)
                    if statu == True:
                        await m.reply_text(f"{id} yetkisiz olarak eklendi")
                        return
                    else:
                        await m.reply_text(f"{id} yetkisiz olarak eklendi ama mesaj gönderilemedi: {statu}")
                        return
                await m.reply_text(f"{id} yetkisiz olarak eklendi\nBildirim istenmedi.")
                return
            else:
                await m.reply_text("Bu kişi zaten yetkisiz")
                return
        else:
            await m.reply_text("Geçersiz id")
            return
            
    else:
        await m.reply_text("Geçersiz komut") 
        return
    
async def load_database():
    DATAS = await db.get_all()
    auths = await db.get_auths()
    UNAUTHS.clear()
    for id, start_time in DATAS.items():  
        START_TIMES[id] = start_time
        now = datetime.now() 
        if (now - start_time).seconds / 60 > db.usage_limit_minutes: 
            if id not in auths:
                UNAUTHS.add(id) 
                
    for id in auths:
        AUTHS.append(id)
        if id not in DATAS:
            UNAUTHS.add(id) 
            
            
async def chech_create_task():
    while True:
        await load_database()
        await asyncio.sleep(5) 


# TEST KOMUTLARI
#! KOMUTLARI AŞAĞIYA EKLE
# Örnekler:
@app.on_message(filters.command("start"))
def start(_, message):
    message.reply_text('Salam, günlük mərc təxminləri botuna xoş gəlmisiniz ! Istifadə üçün əmrləri bilirsinizsə yazaraq davam edin əgər bilmirsinizsə adminlə əlaqə saxlayın. Unutmayın mərcdə 100/100 deyə birşey yoxdur. Bu bot sizin üçün ideal seçimləri analiz edərək istifadəniz üçün verir. Tovsiyyəmiz odur ki, ortalaması 3-0/3-1 olan oyunlara 1.5 ataraq 3-4əmsal yığasınız. Və etdiyiniz mərclərdən, uduzduğunuz oyunlardan biz məsuliyyət daşımırıq.')


@app.on_message(filters.command("hacidayi1213"))
def help_command(client, message):
    help_text = (
       "Salam! Premium üçün olan əmrlərə xoş gəlmisiniz 🫴\n"
       "/send25 - 2.5 alt/üst təxminləri 🗺️\n"
       "/sendqq - Qolqol təxminləri 🗺️\n"
       "/sendscore - Dəqiq hesab 🗺️\n"
       "/12 - Kim qazanacaq 🗺️"
                )
    message.reply_text(help_text)
            
            
    



@app.on_message(filters.command("send25"))
def get_predictions(_, message):
    url = "https://footballpredictions.net/under-over-2-5-goals-betting-tips-predictions"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    predictions = []

    
    match_elements = soup.select('.match-card')
    
    for index, match_element in enumerate(match_elements, start=1):
        teams_element = match_element.select('.team-label')
        prediction_text = match_element.select_one('.prediction').get_text(strip=True)

        teams_text = ' / '.join(team.get_text(strip=True) for team in teams_element)

        if teams_text and prediction_text:
            prediction_with_teams = f"{index}) {teams_text} netice‘‘ {prediction_text}"
            predictions.append(prediction_with_teams)

    
    if predictions:
        message.reply_text('\n'.join(predictions))
    else:
        message.reply_text('Xeta.')
        
@app.on_message(filters.command("12"))
def get_predictions(_, message):
    url = "https://footballpredictions.net/win-draw-win-predictions-full-time-result-betting-tips"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    predictions = []

    
    match_elements = soup.select('.match-card')
    
    for index, match_element in enumerate(match_elements, start=1):
        teams_element = match_element.select('.team-label')
        prediction_text = match_element.select_one('.prediction').get_text(strip=True)

        teams_text = ' / '.join(team.get_text(strip=True) for team in teams_element)

        if teams_text and prediction_text:
            prediction_with_teams = f"{index}) {teams_text} netice˜ {prediction_text}"
            predictions.append(prediction_with_teams)

    
    if predictions:
        message.reply_text('\n'.join(predictions))
    else:
        message.reply_text('xeta.')
        
        
@app.on_message(filters.command("sendqq"))
def get_predictions(_, message):
    url = "https://footballpredictions.net/btts-tips-both-teams-to-score-predictions"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    predictions = []

    
    match_elements = soup.select('.match-card')
    
    for index, match_element in enumerate(match_elements, start=1):
        teams_element = match_element.select('.team-label')
        prediction_text = match_element.select_one('.prediction').get_text(strip=True)

        teams_text = ' / '.join(team.get_text(strip=True) for team in teams_element)

        if teams_text and prediction_text:
            prediction_with_teams = f"{index}) {teams_text} netice˜ {prediction_text}"
            predictions.append(prediction_with_teams)

    
    if predictions:
        message.reply_text('\n'.join(predictions))
    else:
        message.reply_text('xeta.')        
        
        
@app.on_message(filters.command("sendscore"))
def get_predictions(_, message):
    url = "https://footballpredictions.net/correct-score-predictions-betting-tips"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    predictions = []

    
    match_elements = soup.select('.match-card')
    
    for index, match_element in enumerate(match_elements, start=1):
        teams_element = match_element.select('.team-label')
        prediction_text = match_element.select_one('.prediction').get_text(strip=True)

        teams_text = ' / '.join(team.get_text(strip=True) for team in teams_element)

        if teams_text and prediction_text:
            prediction_with_teams = f"{index}) {teams_text} ðŸ‘‘ {prediction_text}"
            predictions.append(prediction_with_teams)

    
    if predictions:
        message.reply_text('\n'.join(predictions))
    else:
        message.reply_text('XÉ™ta.')

app.run()
    

@app.on_message(filters.command("test") &~ UNAUTHS)
@start_time_check
async def test(_, m: Message):
    await m.reply_text("test")



async def start_bot():
    await app.start()
    print(app.me.username, app.me.first_name)
    await asyncio.create_task(chech_create_task())
    await app.idle()
    await app.stop()
    

app.run(start_bot())
