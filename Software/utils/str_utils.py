from random import choice
from string import ascii_letters

def reduce_str(str_text, separator ,max_length):
    toreduce = str_text
    while len(toreduce) > max_length:
        splited = toreduce.rsplit(separator, 1)
        if len(splited) == 1:
            toreduce = toreduce[0:max_length]
        else:
            toreduce = splited[0]
    return toreduce

def generate_randomstr(size):
    return ''.join(choice(ascii_letters) for _ in range(size))