import random

from num2words import num2words

def numerical_string_challenge():
    number = random.randrange(1000)
    s = num2words(number, lang='fr')
    return s, str(number)

