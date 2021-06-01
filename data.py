
import requests
import pandas as pd
import sys
from bs4 import BeautifulSoup
import numpy as np
import re
import random

DATA_SOURCE = 'https://bit.ly/3wGaAA0'

def getDataAndHint():
   db, hints, customers, products  = [], set(), set(), set()
   times = ['today', 'tomorrow']
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
      
      hints.update([route, product, customer])
      customers.add(customer)
      products.add(product)

      db.append([date, quantity, route, product, customer, dayref])

   headers = ['Date', 'Quantity', 'Route', 'Product', 'Customer', 'Dayref']
   orderDF = pd.DataFrame(db, columns = headers)

   # Add more hints
   hints.update([str(i) for i in range(11)])
   # Custom hint 
   hints.update(['order'])
   # Generate questions
   questionsList = []
   # customerOrder intent questions
   # what is scout order for tomorrow?
   for customer in customers:
      for time in times:
         questions = []
         prefix = ['what is ', 'tell me about ', 'I want to know ', 'do you know ']
         for p in prefix:
               question = p + customer + 'orders for ' + time
               questions.append(question)

         for q in questions:
               questionsList.append(['customerOrder', q])

   # productOrder intent questions
   # "what is mini croissant order for tomorrow"
   for product in products:
      for time in times:
         questions = []
         prefix = ['what is ', 'tell me about ', 'I want to know ', 'do you know ', 'can you tell me ']
         for p in prefix:
               question = p + product + 'orders for ' + time
               questions.append(question)

         for q in questions:
               questionsList.append(['productOrder', q])

   # who intent question
   # "Who gets 10 plain croissants today"
   for product in products:
      for time in times:
         questions = []
         prefix = ['who ', 'tell me who ', 'I want to know who ', 'do you know who ']
         for p in prefix:
               question = p + 'gets ' + str(random.randint(1, 10))  + ' ' + product + ' ' + time
               questions.append(question)
         for q in questions:
               questionsList.append(['who', q])

   # quantity intent question
   # "How many baguettes does Novo get today."
   count = 0
   for customer in customers:
      for product in products:
         for time in times:
               questions = []
               prefix = ['how many ', 'tell me how many ']
               for p in prefix:
                  question = p + product + ' does ' + customer + ' get ' + time
                  questions.append(question)
               for q in questions:
                  questionsList.append(['quantity', q])
                  count += 1
      # stop generating question if we reach 450, so it is balanced with other questions
      if(count >= 450):
         break

   headers = ['class', 'question']
   questionDF = pd.DataFrame(questionsList, columns = headers)

   return orderDF, hints, customers, products, times, questionDF
