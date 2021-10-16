#!/usr/bin/env python3
import re
from collections import deque
from itertools import groupby
from urllib.request import urlopen
from urllib.parse import quote, unquote
from urllib.error import URLError, HTTPError

BASE_URL = 'http://ru.wikipedia.org/wiki/'
_pattern_for_links = re.compile(r'/wiki/([^#:.]+?)["\']', re.DOTALL)
_pattern_for_content = re.compile(r'content-text.+?catlinks"')
_content_of_articles = dict()


def get_content(name: str):
    """
    Функция возвращает содержимое вики-страницы name из русской Википедии.
    В случае ошибки загрузки или отсутствия страницы возвращается None.
    """
    try:
        with urlopen(BASE_URL + quote(name)) as page:
            content = page.read().decode('utf-8')
            return content
    except (URLError, HTTPError):
        return None


def extract_content(page: str):
    """
    Функция принимает на вход содержимое страницы и возвращает 2-элементный
    tuple, первый элемент которого — номер позиции, с которой начинается
    содержимое статьи, второй элемент — номер позиции, на котором заканчивается
    содержимое статьи.
    Если содержимое отсутствует, возвращается (0, 0).
    """
    extracted_content = re.search(_pattern_for_content, page)
    return (extracted_content.start(), extracted_content.end()) \
        if extracted_content is not None \
        else (0, 0)


def extract_links(page: str, begin: int, end: int):
    """
    Функция принимает на вход содержимое страницы и начало и конец интервала,
    задающего позицию содержимого статьи на странице и возвращает все имеющиеся
    ссылки на другие вики-страницы без повторений и с учётом регистра.
    """
    links = re.findall(_pattern_for_links, page[begin:end])
    return [unquote(link) for link, _ in groupby(links)]


def find_chain(start: str, finish: str):
    """
    Функция принимает на вход название начальной и конечной статьи и возвращает
    список переходов, позволяющий добраться из начальной статьи в конечную.
    Первым элементом результата должен быть start, последним — finish.
    Если построить переходы невозможно, возвращается None.
    """
    chains_of_links_of_articles = dict()
    chains_of_links_of_articles[start] = None
    articles = deque()
    articles.append(start)
    while len(articles) > 0:
        article = articles.popleft()
        if article == finish:
            return make_chain(article, chains_of_links_of_articles)
        links_in_article = get_links_in_article(article)
        if links_in_article is None:
            continue
        for link in links_in_article:
            if link not in chains_of_links_of_articles.keys():
                articles.append(link)
                chains_of_links_of_articles[link] = article
    return None


def get_links_in_article(article: str):
    try:
        content = _content_of_articles[article]
    except KeyError:
        content = get_content(article)
        _content_of_articles[article] = content
    if content is None:
        return None
    start_of_content, end_of_content = extract_content(content)
    return extract_links(content, start_of_content, end_of_content)


def make_chain(article: str, chains_of_links_of_articles: dict):
    chain = [article]
    article = chains_of_links_of_articles[article]
    while article is not None:
        chain.append(article)
        article = chains_of_links_of_articles[article]
    return list(reversed(chain))


def main():
    pass


if __name__ == '__main__':
    main()
