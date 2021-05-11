import threading as t
import tkcalculator.converters as tc
import random
import time

conv = tc.CurrencyConverter()
conv.set_currencies('INR', 'USD')


def func1():
    while True:
        i = random.randrange(1, 10000000)
        print(f'from `func1`: cube of {i} is {i ** 3}')
        time.sleep(2)

def func2():
    while True:
        i = random.randrange(1, 19999999)
        print(f"from `func2`: square of {i} is {i **2}")
        time.sleep(2)

p1 = t.Thread(target=conv.update_currencies)
p2 = t.Thread(target=func1)
p3 = t.Thread(target=func2)
p1.start()
p2.start()
p3.start()
