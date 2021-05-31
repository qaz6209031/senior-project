import aiy.voice.tts
from aiy.board import Board
from aiy.cloudspeech import CloudSpeechClient
from nltk.stem import PorterStemmer
from data import getDataAndHint

def main():
    print('Retrieving the data')
    data, hints, customers, products = getDataAndHint()
    print('Data loaded')

    client = CloudSpeechClient()
    with Board() as board:
        while True:
            print('Say something or repeat after me or bye')
            text = client.recognize(hint_phrases=hints)
            if text is None:
                print('You said nothing.')
                continue
            if 'goodbye' in text:
                break
            query = text.lower()
            query = normalizedQuery(query)
            print('Query is', text)
            print('Genrating response...')
            response = classifyQuery(query, data, customers, products)
            print('Response', response)
            aiy.voice.tts.say(response)

# Sample question: what is scout order for tomorrow?
# Sample answer: scout gets 0 country batard 15 mini croissant 8 ham and cheese croissant 6 chocolate croissant 21 morning bun tomorrow
def customerOrderTime(df, customer, time):
    # Get the result based on customer and time
    filter = (df['Dayref'] == time) & (df['Customer'] == customer)
    table = df.loc[filter]
    print(table)

    # Construct reponse
    response = ''
    for ind in table.index:
        response += table['Quantity'][ind] + ' ' + table['Product'][ind] + ' '

    if not response:
        response = 'nothing '
    response = customer + ' gets ' + response + time
    return response


# Sample question: "What are morning bun orders for tomorrow"
# Sample Answer: "Tomorrow bun orders are Scout 30 Linnaea's 4 Kreuzberg 10 Kraken 12 Coastal Peaks 6"
def makeOrderTime(df, product, time):
    # Get the result based on customer and time
    filter = (df['Dayref'] == time) & (df['Product'] == product)
    table = df.loc[filter]

    response = ''
    for ind in table.index:
        response += table['Customer'][ind] + ' ' + table['Quantity'][ind] + ' '
    if not response:
        response = 'nothing'

    response = time + ' ' + product + ' orders are ' + response       

    return response

# Sample question: "Who gets 10 plain croissants today"
# Sample Answer: "Sally Loos gets 10 croissants today and Kreuzberg gets 10 croissants today"
def whoGetOrderTime(df, quantity, product, time):
    filter = (df['Dayref'] == time) & (df['Product'] == product) & (df['Quantity'] == quantity)
    table = df.loc[filter]
    
    response = ''
    for ind in table.index:
        response += table['Customer'][ind] + ' gets ' + table['Quantity'][ind] +  \
            ' ' + table['Product'][ind] + ' ' + table['Dayref'][ind] + ' '

    if not response:
        response = 'no one gets ' + quantity + ' ' + product + ' ' + time
   
    return response

#Sample question:  "How many baguettes does Novo get today."
#Sample answer:  "Novo gets 10 baguettes today"
def getQuantityOrderTime(df, product, customer, time):
    filter = (df['Dayref'] == time) & (df['Product'] == product) & (df['Customer'] == customer)
    table = df.loc[filter]

    # Assume the table only returns one row
    if table.empty:
        response = customer + ' gets 0 ' + product + ' ' + time
    else:
        # Get the first element of series 
        response = customer + ' gets ' + table['Quantity'].iloc[0]  + ' ' + product + ' ' + time
    return response

def normalizedQuery(query):
    ps = PorterStemmer()
    # Stemming query
    stemmedQuery = [ps.stem(word) for word in query.split()]
    # Reconstruct query
    query = ' '.join(stemmedQuery)
    return query

# Decides which function does the query maps to
def classifyQuery(query, data, customers, products):
    customer, time, product, quantity = '', '', '', ''
    response = ''
    times = ['today', 'tomorrow']

    # Check if customer exist
    for c in customers:
        if c in query:
            customer = c
            break
    
    # Check if product exist
    for p in products:
        if p in query:
            product = p
            break

    # Check if time exist
    for t in times:
        if t in query:
            time = t
            break
    
    # Check if quantity exist:
    words = query.split()
    for word in words:
        if word.isnumeric():
            quantity = word
            break

    if customer and time and product:
        print('Call getQuantityOrderTime')
        response = getQuantityOrderTime(data, product, customer, time)
    elif time and product and quantity:
        print('Call whoGetOrderTime')
        response = whoGetOrderTime(data, quantity, product, time)
    elif time and product:
        print('Call makeOrderTime')
        response = makeOrderTime(data, product, time)
    elif customer and time:
        print('Call customerOrderTime')
        response = customerOrderTime(data, customer, time)
    else:
        response = "Sorry I don't recognize this question, please ask another one"

    return response

if __name__ == '__main__':
    main()
