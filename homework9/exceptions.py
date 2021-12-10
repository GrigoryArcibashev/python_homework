#!/usr/bin/env python

import math
import sys


def f0():
    # raise BaseException
    sys.exit(1)


def f1():
    # raise Exception
    return 'a' ** 2


def f2():
    # raise ArithmeticError
    return 0 / 0


def f3():
    raise FloatingPointError
    # Вот если бы мы писали на <3.7, то можно было бы импортировать модуль
    # fpectl и использовать его для получения этой ошибки, но в нынешних
    # версиях питона этого модуля нет, так шо задача нерешаема?


def f4():
    # raise OverflowError
    return math.e ** 1000


def f5():
    # raise ZeroDivisionError
    return 0 / 0


def f6():
    # raise AssertionError
    assert False


def f7():
    # raise AttributeError
    return int().aaaaaaaa


def f8():
    # raise EnvironmentError
    open('', 'r')


def f9():
    # raise ImportError
    import by_order_of_the_peaky_plinders


def f10():
    # raise LookupError
    return tuple()[-1]


def f11():
    # raise IndexError
    return list()[-1]


def f12():
    # raise KeyError
    return dict()['first']


def f13():
    # raise NameError
    print(variable)


def f14():
    # raise SyntaxError
    eval('a = 1 2')


def f15():
    # raise ValueError
    math.sqrt(-1)


def f16():
    # raise UnicodeError
    'ъ'.encode('ascii')


def check_exception(f, exception):
    try:
        f()
    except exception:
        pass
    else:
        print("Bad luck, no exception caught: %s" % exception)
        sys.exit(1)


check_exception(f0, BaseException)
check_exception(f1, Exception)
check_exception(f2, ArithmeticError)
check_exception(f3, FloatingPointError)
check_exception(f4, OverflowError)
check_exception(f5, ZeroDivisionError)
check_exception(f6, AssertionError)
check_exception(f7, AttributeError)
check_exception(f8, EnvironmentError)
check_exception(f9, ImportError)
check_exception(f10, LookupError)
check_exception(f11, IndexError)
check_exception(f12, KeyError)
check_exception(f13, NameError)
check_exception(f14, SyntaxError)
check_exception(f15, ValueError)
check_exception(f16, UnicodeError)

print("Congratulations, you made it!")
