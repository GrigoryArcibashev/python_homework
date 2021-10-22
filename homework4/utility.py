import sys
import os
import os.path
from pathlib import Path
from enum import Enum

MODES = Enum('MODES', 'POPRES POPUSER HELP')


def read_arguments():
    """
    Возвращает путь до файла с логами и режим работы
    """
    arguments = sys.argv[1:]
    check_arguments_for_errors(arguments)
    return arguments[0], get_mode_by_name(arguments[1])


def check_arguments_for_errors(arguments: list):
    """
    Проверяет переданные аргументы на корректность
    """
    if len(arguments) == 0:
        report_error('Не указан путь до файла с логами', 1)
    elif len(arguments) == 1:
        report_error('Не указан режим работы утилиты', 1)
    filepath = str(arguments[0])
    if not (os.path.exists(filepath) and os.path.isfile(filepath)):
        report_error('Файл %s не найден.' % filepath, 1)
    mode = str(arguments[1])
    if mode.upper() not in [m.name for m in MODES]:
        report_error('Неизвестный параметр %s.\n' % mode, 1)


def report_error(error_message: str, error_code: int):
    """
    Информирует об оишбке, после чего аварийно завершает выполнение программы
    """
    print('%s.\n' % error_message +
          'Подробнее об использовании утилиты ' +
          'можно узнать с помощью команды help:\n' +
          'python %s help' % sys.argv[0])
    exit(error_code)


def get_mode_by_name(mode_name: str):
    """
    Возвращает элемент перечисления MODES по имени
    """
    mode_name = mode_name.upper()
    for mode in MODES:
        if mode.name == mode_name:
            return mode
    return None


def get_next_lines(max_bytes: int):
    pass


def find_most_popular_resource():
    pass


def find_most_active_user():
    pass


def get_help():
    return \
        """a"""


def main():
    file_path, mode = read_arguments()
    if mode is MODES.POPRES:
        find_most_popular_resource()
    elif mode is MODES.POPUSER:
        find_most_active_user()
    else:
        print(get_help())


if __name__ == '__main__':
    main()
