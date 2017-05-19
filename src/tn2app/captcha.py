import random

from num2words import num2words

def numerical_string_challenge():
    number = random.randrange(1000)
    s = num2words(number, lang='fr')
    if len(s) > 32: # maximum challenge length in django-simple-captcha is 32
        return numerical_string_challenge()
    return s, str(number)

