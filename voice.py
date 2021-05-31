import aiy.voice.tts
from aiy.board import Board
from aiy.cloudspeech import CloudSpeechClient
from nltk.stem import PorterStemmer
from data import getDataAndHint
from difflib import SequenceMatcher

print('Retrieving the data')
DATA, HINTS, CUSTOMERS, PRODUCTS = getDataAndHint()
print('Data loaded')

def main():
    client = CloudSpeechClient()
    with Board() as board:
        while True:
            print('Say something or repeat after me or bye')
            text = client.recognize(hint_phrases = HINTS)
            if text is None:
                print('You said nothing.')
                continue
            if 'goodbye' in text:
                break
            query = text.lower()
            query = normalizedQuery(query)
            print('Query is', query)
            print('Genrating response...')
            response = classifyQuery(query)
            print('Response', response)
            aiy.voice.tts.say(response)

# Sample question: what is scout order for tomorrow?
# Sample answer: scout gets 0 country batard 15 mini croissant 8 ham and cheese croissant 6 chocolate croissant 21 morning bun tomorrow
def customerOrderTime(customer, time):
    # Get the result based on customer and time
    filter = (DATA['Dayref'] == time) & (DATA['Customer'] == customer)
    table = DATA.loc[filter]

    # Construct reponse
    response = ''
    for ind in table.index:
        response += table['Quantity'][ind] + ' ' + table['Product'][ind] + ' '

    if not response:
        response = 'nothing '
    response = customer + ' gets ' + response + time
    return response


# Q: "what is mini croissant order for tomorrow"
# A: "tomorrow mini croissant orders are scout 2 with 45 orders and scout with 15 orders"
def makeOrderTime(product, time):
    # Get the result based on customer and times
    filter = (DATA['Dayref'] == time) & (DATA['Product'] == product)
    table = DATA.loc[filter]

    response = ' and '.join([table['Customer'][ind] + ' with ' + table['Quantity'][ind] + ' orders' for ind in table.index])
    if not response:
        response = 'nothing'

    response = time + ' ' + product + ' orders are ' + response       

    return response

# Sample question: "Who gets 10 plain croissants today"
# Sample Answer: "Sally Loos gets 10 croissants today and Kreuzberg gets 10 croissants today"
def whoGetOrderTime(quantity, product, time):
    filter = (DATA['Dayref'] == time) & (DATA['Product'] == product) & (DATA['Quantity'] == quantity)
    table = DATA.loc[filter]
    
    response = ''
    for ind in table.index:
        response += table['Customer'][ind] + ' gets ' + table['Quantity'][ind] +  \
            ' ' + table['Product'][ind] + ' ' + table['Dayref'][ind] + ' '

    if not response:
        response = 'no one gets ' + quantity + ' ' + product + ' ' + time
   
    return response

#Sample question:  "How many baguettes does Novo get today."
#Sample answer:  "Novo gets 10 baguettes today"
def getQuantityOrderTime(product, customer, time):
    filter = (DATA['Dayref'] == time) & (DATA['Product'] == product) & (DATA['Customer'] == customer)
    table = DATA.loc[filter]

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

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def ngrams(inp, n):
    inp = inp.split(' ')
    output = []
    for i in range(len(inp)-n+1):
        output.append(inp[i:i+n])
    return output

def containSimilarSubstring(query ,items):
    # Check if product exist
    for i in items:
        # find the length of p
        length = len(i.split())
        ngramList = [' '.join(x) for x in ngrams(query, length)]
        for ngram in ngramList:
            if similar(ngram, i) > 0.85:
                return i
    return ''


# Decides which function does the query maps to
def classifyQuery(query):
    customer, time, product, quantity = '', '', '', ''
    response = ''
    times = ['today', 'tomorrow']

    # Check if query contains string that similar to one of our product
    customer = containSimilarSubstring(query, CUSTOMERS)

    # Check if query contains string that similar to one of our product
    product = containSimilarSubstring(query, PRODUCTS)

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
        response = getQuantityOrderTime(product, customer, time)
    elif time and product and quantity:
        print('Call whoGetOrderTime')
        response = whoGetOrderTime(quantity, product, time)
    elif time and product:
        print('Call makeOrderTime')
        response = makeOrderTime(product, time)
    elif customer and time:
        print('Call customerOrderTime')
        response = customerOrderTime(customer, time)
    else:
        response = "Sorry I don't recognize this question, please ask another one"

    return response

if __name__ == '__main__':
    main()
