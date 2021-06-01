# import aiy.voice.tts
# from aiy.board import Board
# from aiy.cloudspeech import CloudSpeechClient
from nltk.stem import PorterStemmer
from data import getData
from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

print('Retrieving the data')
DATA, HINTS, CUSTOMERS, PRODUCTS, TIMES, QUESTION_DF = getData()
print('Data loaded')

def main():
    # Train the intent classifier
    clf, count_vect = naive_algo()
    print(QUESTION_DF.question)
   
    # client = CloudSpeechClient()
    # with Board() as board:
    #     while True:
    #         print('Say something or repeat after me or bye')
    #         query = client.recognize(hint_phrases = HINTS)
    #         if query is None:
    #             print('You said nothing.')
    #             continue
    #         if 'goodbye' in query:
    #             break
    #         print('Query is', query.lower())
    #         print('Genrating response...')
    #         response = mapToFunction(query, clf, count_vect)
    #         print('Response', response)
    #         aiy.voice.tts.say(response)

# Sample question: what is scout order for tomorrow?
# Sample answer: scout gets 0 country batard 15 mini croissant 8 ham and cheese croissant 6 chocolate croissant 21 morning bun tomorrow
def customerOrder(query):
    customer, time, product, quantity = extractEntity(query)
    print('Time: ', time, 'Customer: ', customer)
    if not time or not customer:
        return 'I do not understand, please ask me another question'
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
def productOrder(query):
    customer, time, product, quantity = extractEntity(query)
    print('Time: ', time, 'Product ', product) 
    if not time or not product:
        return 'I do not understand, please ask me another question'
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
def who(query):
    customer, time, product, quantity = extractEntity(query)
    print('Time: ', time, 'Product: ', product, 'Quantity: ', quantity)
    if not time or not product or not quantity:
        return 'I do not understand, please ask me another question'
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
def quantity(query):
    customer, time, product, quantity = extractEntity(query)
    print('Time: ', time, 'Product: ', product, 'Customer: ', customer)
    if not time or not product or not customer:
        return 'I do not understand, please ask me another question'
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

# Map query to function
def mapToFunction(rawQuery, clf, count_vect):
    response = ''
    query = rawQuery.lower()
    res = predict(query, clf, count_vect)
    query = normalizedQuery(query)
    if res == 'customerOrder':
        response = customerOrder(query)
    elif res == 'productOrder':
        response = productOrder(query)
    elif res == 'who':
        response = who(query)
    elif res == 'quantity':
        response = quantity(query)
    return response

# Extract entity from query, return in the order of customer, time, product, quantity
def extractEntity(query):
    customer, time, product, quantity = '', '', '', ''
    customer = containSimilarSubstring(query, CUSTOMERS)
    product = containSimilarSubstring(query, PRODUCTS)
    # Check if time exist
    for t in TIMES:
        if t in query:
            time = t
            break

    # Check if quantity exist:
    words = query.split()
    for word in words:
        if word.isnumeric():
            quantity = word
            break
    
    return customer, time, product, quantity

# Refer the concept from https://towardsdatascience.com/multi-label-intent-classification-1cdd4859b93
def naive_algo():
    tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
    features = tfidf.fit_transform(QUESTION_DF.question).toarray()
    X_train, X_test, y_train, y_test = train_test_split(QUESTION_DF['question'], QUESTION_DF['class'], random_state = 0)
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(X_train)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    clf = MultinomialNB().fit(X_train_tfidf, y_train)
    return clf,count_vect

def predict(question, clf, count_vect):
    intent=clf.predict(count_vect.transform([question]))
    intent=str(intent).strip("['']")
    print('Intent is', intent)
    return intent
    
if __name__ == '__main__':
    main()
