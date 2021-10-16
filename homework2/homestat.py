#!/usr/bin/env python3
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

_global_stat = None


def make_stat(filename):
    """
    Функция вычисляет статистику по именам за каждый год с учётом пола.
    """
    global _global_stat
    if _global_stat is None:
        url = 'http://shannon.usu.edu.ru/ftp/python/hw2/' + filename
        page_content = get_page_content(url)
        if page_content is None:
            print('failed to download html page: {}'.format(url))
            return None
        _global_stat = parse_page_content(page_content)
    return _global_stat


def extract_years(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список годов,
    упорядоченный по возрастанию.
    """
    return list(sorted(stat.keys()))


def extract_general(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для всех имён.
    Список должен быть отсортирован по убыванию количества.
    """
    return get_frequency_of_names_for_years_in_descending_order(
        stat,
        stat.keys())


def get_frequency_of_names_for_years_in_descending_order(
        stat,
        years,
        male_names=True,
        female_names=True):
    def is_sex_female(sex):
        return not sex

    name_counter = dict()
    for year in years:
        for name in stat[year]:
            if not (male_names and not is_sex_female(name[1])) \
                    and not (female_names and is_sex_female(name[1])):
                continue
            try:
                name_counter[name[0]] += 1
            except KeyError:
                name_counter[name[0]] = 1
    return sorted(
        list(name_counter.items()),
        key=lambda pair: pair[1],
        reverse=True)


def extract_general_male(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён мальчиков.
    Список должен быть отсортирован по убыванию количества.
    """
    return get_frequency_of_names_for_years_in_descending_order(
        stat,
        stat.keys(),
        female_names=False)


def extract_general_female(stat):
    """
    Функция принимает на вход вычисленную статистику и выдаёт список tuple'ов
    (имя, количество) общей статистики для имён девочек.
    Список должен быть отсортирован по убыванию количества.
    """
    return get_frequency_of_names_for_years_in_descending_order(
        stat,
        stat.keys(),
        male_names=False)


def extract_year(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return get_frequency_of_names_for_years_in_descending_order(stat, [year])


def extract_year_male(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён мальчиков в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return get_frequency_of_names_for_years_in_descending_order(
        stat,
        [year],
        female_names=False)


def extract_year_female(stat, year):
    """
    Функция принимает на вход вычисленную статистику и год.
    Результат — список tuple'ов (имя, количество) общей статистики для всех
    имён девочек в указанном году.
    Список должен быть отсортирован по убыванию количества.
    """
    return get_frequency_of_names_for_years_in_descending_order(
        stat,
        [year],
        male_names=False)


def get_page_content(url):
    """
    Функция скачивает html-файл по указанному url,
    после чего возвращает его содержимое в виде строки
    """
    try:
        with urlopen(url) as page:
            content = page.read().decode('Windows-1251')
        return content
    except (URLError, HTTPError):
        return None


def parse_page_content(html_code):
    result = dict()
    current_year = None
    for line in html_code.split('\n'):
        name_position = line.find('</a>')
        if name_position != -1:
            start_of_name = name_position
            while start_of_name >= 0 and line[start_of_name] != '>':
                start_of_name -= 1
            full_name = line[start_of_name + 1: name_position].split(' ')
            sex = is_sex_male(*full_name)
            if current_year is not None:
                result[current_year].append((full_name[1], sex))
            continue

        year_position = line.find('<h3>')
        if year_position != -1:
            year = line[year_position + 4: year_position + 8]
            current_year = year
            result[year] = []
    return result


def is_sex_male(last_name, first_name):
    """
    Возвращает:
        True, если пол мужской,
        False, если пол женский
    """
    male_endings_for_last_name = ('ов', 'ев', 'ёв', 'ын', 'ин', 'ский', 'цкий')
    male_endings_for_first_name = ('ёва', 'ий', 'рь', 'ман', 'рилл', 'дро',
                                   'ег', 'он', 'ел', 'фей', 'ндр', 'ий', 'ил',
                                   'ей', 'ём', 'тор', 'ис', 'ван', 'дим',
                                   'сей', 'лав', 'еб', 'сим', 'лай')
    is_last_name_male = False
    for ending in male_endings_for_last_name:
        if len(last_name) >= len(ending) \
                and last_name[-len(ending):] == ending:
            is_last_name_male = True
            break

    is_first_name_male = False
    for ending in male_endings_for_first_name:
        if len(first_name) >= len(ending) \
                and first_name[-len(ending):] == ending:
            is_first_name_male = True
            break
    return is_last_name_male or is_first_name_male


if __name__ == '__main__':
    pass
