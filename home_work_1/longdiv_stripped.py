#!/usr/bin/env python3


def long_division(dividend, divider):
    """
    Вернуть строку с процедурой деления «уголком» чисел dividend и divider.
    Формат вывода приведён на примерах ниже.

    Примеры:
    >>> 12345÷25
    12345|25
    100  |493
     234
     225
       95
       75
       20

    >>> 1234÷1423
    1234|1423
    1234|0

    >>> 24600÷123
    24600|123
    246  |200
      0

    >>> 246001÷123
    246001|123
    246   |2000
         1
    """
    result = [str(dividend) + '|' + str(divider) + '\n']
    digits_of_dividend = get_digits_of_number(dividend)
    # shift1 - расстояние от начала столбика до первой цифры в текущей строке
    shift1 = 0
    first_iteration = True
    while True:
        if len(digits_of_dividend) > 0 and digits_of_dividend[0] == 0:
            del digits_of_dividend[0]
            shift1 += 1
            continue

        current_dividend = 0
        pos_of_next_digit = 0

        current_dividend, pos_of_next_digit = get_next_divedend(
            current_dividend,
            digits_of_dividend,
            divider,
            pos_of_next_digit)

        remainder_of_division = current_dividend % divider
        length_of_current_dividend = len(get_digits_of_number(current_dividend))
        result_of_dividing_current_dividend = current_dividend - remainder_of_division
        # shift2 = {длина current_dividend} - {длина result_of_dividing_current_dividend}
        # shift3 = {длина dividend} - shift1 - {длина current_dividend}
        shift2 = length_of_current_dividend - len(get_digits_of_number(result_of_dividing_current_dividend))
        shift3 = len(get_digits_of_number(dividend)) - shift1 - length_of_current_dividend

        if result_of_dividing_current_dividend > 0:
            if first_iteration:
                first_iteration = False
            else:
                result.append(' ' * shift1 + str(current_dividend) + ' ' * shift3 + '|\n')
        if result_of_dividing_current_dividend > 0:
            result.append(' ' * (shift1 + shift2) + str(result_of_dividing_current_dividend) + ' ' * shift3 + '|\n')
        else:
            shift2 = 0

        shift1 = change_shift1(
            digits_of_dividend,
            length_of_current_dividend,
            pos_of_next_digit,
            remainder_of_division,
            shift1)

        current_dividend %= divider

        if current_dividend < divider and list_is_filled_with_zeros(digits_of_dividend[pos_of_next_digit:]):
            return finish_forming_response(current_dividend, dividend, divider, result, shift1, shift2, shift3)

        digits_of_dividend = (get_digits_of_number(current_dividend)
                              if current_dividend != 0 else []) + digits_of_dividend[pos_of_next_digit:]

        if list_is_filled_with_zeros(digits_of_dividend):
            return finish_forming_response(current_dividend, dividend, divider, result, shift1, shift2, shift3)


def change_shift1(digits_of_dividend, length_of_current_dividend, pos_of_next_digit, remainder_of_division, shift1):
    shift1 += length_of_current_dividend - len(get_digits_of_number(remainder_of_division))
    if remainder_of_division == 0 and not list_is_filled_with_zeros(digits_of_dividend[pos_of_next_digit:]):
        shift1 += len(get_digits_of_number(remainder_of_division))
    return shift1


def get_next_divedend(current_dividend, digits_of_dividend, divider, pos_of_next_digit):
    while current_dividend < divider and pos_of_next_digit < len(digits_of_dividend):
        current_dividend = current_dividend * 10 + digits_of_dividend[pos_of_next_digit]
        pos_of_next_digit += 1
    return current_dividend, pos_of_next_digit


def finish_forming_response(current_dividend, dividend, divider, result, shift1, shift2, shift3):
    result.append(' ' * (shift1 + shift2) + str(current_dividend) + ' ' * shift3)
    if result[1][-1] == '\n':
        result[1] = result[1][:-1]
    else:
        result[1] = result[1] + '|'
    result[1] = result[1] + str(dividend // divider) + '\n'
    return make_string_from_list(result)


def make_string_from_list(_list: list):
    result = ''
    for i in _list:
        result += i
    return result


def get_digits_of_number(number: int):
    digits = []
    while number > 0:
        digits.append(number % 10)
        number //= 10
    else:
        if len(digits) == 0:
            digits.append(0)
    digits.reverse()
    return digits


def list_is_filled_with_zeros(_list: list):
    for i in _list:
        if i != 0:
            return False
    return True


def main():
    print(long_division(123, 123))
    print()
    print(long_division(1, 1))
    print()
    print(long_division(15, 3))
    print()
    print(long_division(3, 15))
    print()
    print(long_division(12345, 25))
    print()
    print(long_division(1234, 1423))
    print()
    print(long_division(87654532, 1))
    print()
    print(long_division(24600, 123))
    print()
    print(long_division(4567, 1234567))
    print()
    print(long_division(246001, 123))
    print()
    print(long_division(100000, 50))
    print()
    print(long_division(123456789, 531))
    print()
    print(long_division(425934261694251, 12345678))


if __name__ == '__main__':
    main()
