import aiy.voice.tts
from aiy.board import Board
from aiy.cloudspeech import CloudSpeechClient

from data import getData

def main():
    data = getData()
    # response = customerOrderTime(data, 'ascendo los osos', 'today')
    # response = makeOrderTime(data, 'blueberry muffin', 'today')
    # response = whoGetOrderTime(data, '6', 'baguette', 'today')
    response = getQuantityOrderTime(data, 'dutch stick', 'bpb extras', 'today')
    client = CloudSpeechClient()
    with Board() as board:
        while True:
            print('Say something or repeat after me or bye')
            text = client.recognize()
            if text is None:
                print('You said nothing.')
                continue
            print('You said', text)
            text = text.lower()
            if 'repeat after me' in text:
                aiy.voice.tts.say(response)
            elif 'goodbye' in text:
                break

# Sample question: What is Sandos order for tomorrow?
# Sample answer: "Sandos gets 30 mini dutch, 12 french sticks, and 2 bags of brioche buns tomorrow"
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

# Sample question: "Who gets 10 croissants today"
# Sample Answer: "Sally Loos gets 10 croissants today and Kreuzberg gets 10 croissants today"
def whoGetOrderTime(df, quantity, product, time):
    filter = (df['Dayref'] == time) & (df['Product'] == product) & (df['Quantity'] == quantity)
    table = df.loc[filter]
    
    response = ''
    for ind in table.index:
        response += table['Customer'][ind] + ' gets ' + table['Quantity'][ind] +  \
            ' ' + table['Product'][ind] + ' ' + table['Dayref'][ind]

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
if __name__ == '__main__':
    main()