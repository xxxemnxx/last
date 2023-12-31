from pyrogram import Client, filters
from bs4 import BeautifulSoup
import requests

API_ID = "16723398"
API_HASH = "9e07dd89d2f39bfadfd59798705e4662"
BOT_TOKEN = "6815920860:AAF6M1HA3ubMB1kTMjUjTlbzE-UNX5zVQ0E"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
def start(_, message):
    message.reply_text('Salam, günlük mərc təxminlərinə xoş gəldiniz. Aşağıdakı dəqiq hesablara əsasən alt  üst oyanaya bilərsiniz.Daha qazanclı bitirmək üçün günü, 2-1 ortalaması və üzəri olan oyunlara minimum 1.5üst atmağınız məsləhətdir. Əmr /goster.')

@app.on_message(filters.command("goster"))
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
            prediction_with_teams = f"{index}) {teams_text} - Dəqiq hesab {prediction_text}"
            predictions.append(prediction_with_teams)

    if predictions:
        message.reply_text('\n'.join(predictions))
    else:
        message.reply_text('Xəta.')

app.run()
