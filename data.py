
import requests
import pandas as pd
import sys
from bs4 import BeautifulSoup
import numpy as np
import re


DATA_SOURCE = 'https://bit.ly/3wGaAA0'

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
      raw_product = datas[7].text.lower()
      # Remove the text inside of paranthesis 
      product = re.sub(r"\([^()]*\)", "", raw_product).strip()
      customer = datas[8].text.lower()
      dayref = datas[11].text.lower()

      if dayref == '#n/a':
         dayref = np.nan

      db.append([date, quantity, route, product, customer, dayref])

   headers = ['Date', 'Quantity', 'Route', 'Product', 'Customer', 'Dayref']
   df = pd.DataFrame(db, columns = headers)

   return df