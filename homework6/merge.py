#!/usr/bin/env python3

import unittest
import re
from datetime import datetime

REGEX = re.compile(
        r'\[(\d{1,2})/([a-zA-Z]+?)/(\d{4}):(\d{1,2}):(\d{1,2}):(\d{1,2}).*?]',
        re.DOTALL)


def merge(*iterables, key=None):
    """Функция склеивает упорядоченные по ключу `key` и порядку «меньше»
    коллекции из `iterables`.

    Результат — итератор на упорядоченные данные.
    В случае равенства данных следует их упорядочить в порядке следования
    коллекций"""
    items = [item for iterable in iterables for item in iterable]
    items.sort(key=key)
    return iter(items)


def log_key(s):
    """Функция по строке лога возвращает ключ для её сравнения по времени"""
    return datetime.strptime(
            ' '.join(re.findall(REGEX, s)[0]),
            '%d %b %Y %H %M %S')


class TestTest(unittest.TestCase):
    def setUp(self):
        several_iterables = list()
        several_iterables.append(([1, 2], [[2, 1], []]))
        several_iterables.append(([1, 2, 3, 4], [[2, 1], [3, 4]]))
        several_iterables.append(([1, 1, 1, 2], [[2, 1], [1, 1]]))
        several_iterables.append(([1, 2, 3, 4, 5], [[2, 1], [3, 5, 4]]))
        several_iterables.append(
                ([1, 1, 2, 3, 4, 5, 6, 7], [[2, 1, 1], [3, ], [4, 5, 6, 7]]))
        self.several_iterables = several_iterables

    def _check(self, expected: iter, actual: iter):
        self.assertListEqual(list(expected), list(actual))

    def test_one_empty_iterable(self):
        self._check(iter([]), [])

    def test_one_not_empty_iterable(self):
        self._check(iter([1, 2, 3]), merge([3, 1, 2]))

    def test_several_iterables(self):
        for expected, actual in self.several_iterables:
            with self.subTest(expected=expected, input=actual):
                self._check(iter(expected), merge(*actual))

    def test_using_key(self):
        self._check(iter([4, 3, 2, 1]), merge([1, 2, 4, 3], key=lambda x: -x))
