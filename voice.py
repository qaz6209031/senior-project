import aiy.voice.tts
from aiy.board import Board
from aiy.cloudspeech import CloudSpeechClient
from bs4 import BeautifulSoup
import pandas as pd
import requests
import sys

DATA_SOURCE = 'https://bit.ly/3wGaAA0'
def main():
    data = getData()
    print(data)
#    client = CloudSpeechClient()
#    with Board() as board:
#        while True:
#            print('Say something or repeat after me or bye')
#            text = client.recognize()
#            if text is None:
#                print('You said nothing.')
#                continue
#            print('You said', text)
#            text = text.lower()
#            if 'repeat after me' in text:
#                # Remove "repeat after me" from the text to be repeated
#                to_repeat = text.replace('repeat after me', '', 1)
#                aiy.voice.tts.say(to_repeat)
#            elif 'goodbye' in text:
#                break

def getData():
    db = []
    try:
        page = requests.get(DATA_SOURCE)
    except requests.exceptions.RequestException as err:
        sys.exit('Connection error')

    soup = BeautifulSoup(page.text, 'html.parser')
    rows = soup.find('tbody').find_all('tr')

    for row in rows:
        datas = row.find_all('td')

        date = datas[0].text
        quantity = datas[2].text
        route = datas[6].text.lower()
        product = datas[7].text.lower()
        customer = datas[8].text.lower()
        dayref = datas[11].text.lower()

        db.append([date, quantity, route, product, customer, dayref])

    headers = ['Date', 'Quantity', 'Route', 'Product', 'Customer', 'Dayref']
    df = pd.DataFrame(db, columns = headers)
    
    return df
if __name__ == '__main__':
    main()
