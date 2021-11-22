import random  # random.random()
import math


def uniform():
    return random.random()


def exp(l):
    x = random.random()
    return -1 / l * math.log(x)


def normal(miu, var):
    sd = math.sqrt(var)
    return std_normal() * sd + miu


def std_normal():
    y1 = 1
    y2 = 0
    while y2 - (y1 - 1) ** 2 / 2 <= 0:
        y1 = exp(1)
        y2 = exp(1)

    x = random.random()
    solve = y1
    if x > 1 / 2:
        solve *= -1
    return solve
