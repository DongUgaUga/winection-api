import re
from kiwipiepy import Kiwi

kiwi = Kiwi()

REMOVE_WORDS = {'요', '이다'}
REPLACE_WORDS = {'저': '나', '해보다': '하다'}

def text_to_word(text):
    text = re.sub(r'[^\w\s]', '', text)
    tokens = kiwi.analyze(text)[0][0]

    filtered_words = []
    negation_flag = False

    for word, tag, _, _ in tokens:
        if word in REMOVE_WORDS or tag in ['J', 'E', 'XSV', 'XSA']:
            continue
        if word in REPLACE_WORDS:
            word = REPLACE_WORDS[word]
        if tag in ['VV', 'VA']:
            word += '다'
        if tag in ['VX', 'MAG'] and word in ['안', '못']:
            if not negation_flag:
                filtered_words.append('안')
                negation_flag = True
            continue
        if tag in ['NNG', 'NNP', 'VV', 'VA']:
            filtered_words.append(word)
            negation_flag = False 

    return filtered_words