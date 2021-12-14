import argparse
import os
import pathlib
import random
import re
import signal
import sys
import threading
import urllib.request
from types import FrameType
from typing import Optional
from urllib.error import URLError, HTTPError


class Scraper:
    def __init__(self):
        self._init_regexp()
        self._bad_symbols = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', '.')
        self._domain = 'https://habr.com'
        self._links_to_articles = list()
        self._taking_article = threading.Lock()
        self._need_to_shutdown = threading.Event()
        self._register_signal_handler()

    def _init_regexp(self) -> None:
        """Инициализирует регулярные выражения"""
        self._articles_regexp = re.compile(
                r'<div class="tm-article-snippet">.+?h2.+?href="(.+?)".+?/h2',
                re.DOTALL)
        self._content_with_images_regexp = re.compile(
                r'id="post-content-body".+?tm-article-presenter__meta',
                re.DOTALL)
        self._images_regexp = re.compile(r'<img.+?data-src="(.+?)"', re.DOTALL)
        self._article_name_regexp = re.compile(
                ''.join(
                        (
                                r'tm-article-snippet__title ',
                                r'tm-article-snippet__title_h1',
                                r'.+?<span>(.+?)</span>')),
                re.DOTALL)

    def _notify_threads(
            self, signum: signal.Signals, frame: FrameType) -> None:
        """
        Вызывается при получении сигнала от ОС
        Уведомляет все потоки от том, что пришел сигнал
        """
        print(f'Signal number: {signum}\nFrame: {frame}')
        print('Наши полномочия на этом все')
        self._need_to_shutdown.set()
        exit(-1)

    def _register_signal_handler(self) -> None:
        """Регистрирует метод-обработчик сигнала от ОС"""
        signals = signal.valid_signals()
        for sig in signals:
            signal.signal(sig, self._notify_threads)

    def run(
            self,
            threads: int,
            number_of_articles: int,
            out_dir: pathlib.Path) -> None:
        """Запускает скрапер"""
        self._links_to_articles = self._extract_links_to_articles(
                number_of_articles)
        self._start_article_handling(threads, out_dir)

    def _start_article_handling(
            self,
            threads: int,
            out_dir: pathlib.Path) -> None:
        """Обрабатывает статьи в threads потоков"""
        pool = list()
        for _ in range(threads):
            th = threading.Thread(
                    target=self._handle_articles, args=(out_dir,))
            th.start()
            pool.append(th)
        # Так можно сгенерировать случайный сигнал
        # throw_random_signal()
        for th in pool:
            th.join()

    def _extract_links_to_articles(self, number_of_articles: int) -> list:
        """Возвращает список ссылок на статьи"""
        next_page_number = 1
        content = self._get_page_content(next_page_number)
        links_to_articles = self._extract_links_to_articles_from_page(content)
        while len(links_to_articles) < number_of_articles:
            next_page_number += 1
            content = self._get_page_content(next_page_number)
            links_to_articles.extend(
                    self._extract_links_to_articles_from_page(content))
        return links_to_articles[:number_of_articles]

    def _extract_links_to_articles_from_page(self, content: str) -> list:
        """Возвращает список ссылок на статьи с одной станицы (content)"""
        links = re.findall(self._articles_regexp, content)
        return list(map(lambda link: f'{self._domain}{link}', links))

    def _get_page_content(self, page_number: int) -> str:
        """Возвращает содержимое страницы с номером page_number"""
        return load_content_as_string(self._get_link_to_page(page_number))

    def _get_link_to_page(self, page_number: int) -> str:
        """Возвращает url страницы с номером page_number"""
        return f'{self._domain}/ru/all/page{page_number}/'

    def _handle_articles(self, out_dir: pathlib.Path) -> None:
        """Сохраняет изображения из статЕЙ в указанную директорию"""
        while True:
            if self._need_to_shutdown.is_set():
                exit(-1)
            with self._taking_article:
                if not self._links_to_articles:
                    exit(0)
                link = self._links_to_articles.pop()
            self._handle_article(link, out_dir)

    def _handle_article(
            self, link_to_article: str, out_dir: pathlib.Path) -> None:
        """Сохраняет изображения из статьИ в указанную директорию"""
        content = load_content_as_string(link_to_article)
        links_to_images = self._extract_links_to_images_from_article(content)
        if links_to_images:
            name_of_new_dir = self._delete_bad_symbols(
                    self._get_article_name(content))
            out = out_dir.joinpath(name_of_new_dir)
            os.mkdir(out)
            self._save_images(links_to_images, out)

    def _get_article_name(self, article_content: str) -> str:
        """Возвращает имя статьи, извлекая его из ее содержимого"""
        return re.findall(self._article_name_regexp, article_content)[0]

    def _delete_bad_symbols(self, path: str) -> str:
        for symbol in self._bad_symbols:
            path = path.replace(symbol, ' ')
        return path.strip()

    def _extract_links_to_images_from_article(
            self, article_content: str) -> list:
        """Возвращает список ссылок на изображения из статьи"""
        content_with_images = re.findall(
                self._content_with_images_regexp, article_content)[0]
        return re.findall(self._images_regexp, content_with_images)

    def _save_images(
            self,
            links_to_images: list,
            out_dir: pathlib.Path) -> None:
        """Сохраняет изображения из links_to_images в директорию out_dir"""
        img_name = 1
        for link in links_to_images:
            self._save_image(link, out_dir.joinpath(f'{img_name}.jpg'))
            img_name += 1

    @staticmethod
    def _save_image(link_to_image: str, out_file: pathlib.Path) -> None:
        """Сохраняет изображение из link_to_image в файл out_file"""
        image = load_content(link_to_image)
        with open(out_file, 'wb') as out:
            out.write(image)


def load_content(url: str) -> Optional[bytes]:
    try:
        return urllib.request.urlopen(url, timeout=10).read()
    except (HTTPError, URLError):
        return None


def load_content_as_string(url: str) -> str:
    return load_content(url).decode('utf-8')


def throw_random_signal():
    rnd_sig = random.choice(list(signal.valid_signals()))
    signal.raise_signal(rnd_sig)


def main():
    script_name = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
            usage=' '.join(
                    (f'{script_name}',
                     '[ARTICLES_NUMBER] THREAD_NUMBER OUT_DIRECTORY')),
            description='Habr parser',
            )
    parser.add_argument(
            '-n', type=int, default=25,
            help='Number of articles to be processed',
            )
    parser.add_argument(
            'threads', type=int, help='Number of threads to be run',
            )
    parser.add_argument(
            'out_dir', type=pathlib.Path,
            help='Directory to download habr images',
            )
    args = parser.parse_args()
    Scraper().run(args.threads, args.n, args.out_dir)


if __name__ == '__main__':
    main()
