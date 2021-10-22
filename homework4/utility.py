import sys
import os
import os.path
from pathlib import Path
from enum import Enum

MODES = Enum('MODES', 'POPRES POPUSER HELP')


def get_arguments():
    """
    Возвращает путь до файла с логами и режим работы
    """
    arguments = sys.argv[1:]
    check_arguments_for_errors(arguments)
    if len(arguments) > 1:
        return arguments[0], get_mode_by_name(arguments[1])
    return None, get_mode_by_name(arguments[0])


def check_arguments_for_errors(arguments: list):
    """
    Проверяет переданные аргументы на корректность
    """
    if len(arguments) == 0:
        report_error('Не указан путь до файла с логами', 1)
    elif len(arguments) == 1:
        mode = get_mode_by_name(arguments[0])
        if mode is MODES.HELP:
            return
        elif mode is None:
            report_error('Не указан режим работы утилиты', 1)
        else:
            report_error('Не указан путь до файла с логами', 1)
    mode_name = arguments[1]
    mode = get_mode_by_name(mode_name)
    if mode is None:
        report_error('Неизвестный параметр {}\n'.format(mode_name), 1)
    elif mode is MODES.HELP:
        return
    filepath = arguments[0]
    if not (os.path.exists(filepath) and os.path.isfile(filepath)):
        report_error('Файл {} не найден'.format(filepath), 1)


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
    mode_name = mode_name.lower()
    for mode in MODES:
        if mode.name.lower() == mode_name:
            return mode
    return None


def get_lines_from_file(file_path: str, start_byte: int, max_bytes: int):
    with open(file_path, 'r') as file:
        file.seek(start_byte)
        start_outside_file = not bool(file.read(1))
        if start_outside_file:
            return None
        file.seek(file.tell() - 1)
        t = file.tell()
        while t > 0 and file.read(1) != '\n':
            file.seek(t - 2)
            t = file.tell()
        if file.read(1) != '\n':
            file.seek(file.tell() - 1)
        t = file.tell()
        read = file.read(max_bytes)
        if '\n' in read or len(read) <= max_bytes:
            lines = read.split('\n')
        else:
            lines = ''
        lines = list(filter(lambda line: len(line) > 0, lines))
        if len(lines) > 0 \
                and lines[-1][-1] != '\n' \
                and not len(read) <= max_bytes:
            # file.seek(file.tell() - len(lines[-1]) + 1)
            lines = lines[:-1]
        return list(
            map(lambda line: line.strip(), lines)), start_byte + max_bytes


def find_most_popular_resource():
    return None


def find_most_active_user():
    return None


def get_help():
    return """
    Утилита, которая по данному логу, согласно параметрам, выдаёт одну 
    из статистик: самый популярный ресурс и самый активный клиент.
    
    python {0} [path_to_log_file] help
       Помощь по использованию утилиты
       Если лог указан, он игнорируется
    
    python {0} path_to_log_file popres
        Выдать самый популярный ресурс
        
    python {0} path_to_log_file popuser
        Выдать самого активного клиента
    """.format(sys.argv[0])


def main():
    file_path, mode = get_arguments()
    if mode is MODES.POPRES:
        result = find_most_popular_resource()
        print(result if result is not None else 'Не удалось выполнить команду')
    elif mode is MODES.POPUSER:
        result = find_most_active_user()
        print(result if result is not None else 'Не удалось выполнить команду')
    else:
        print(get_help())


if __name__ == '__main__':
    # main()
    c = 0
    lns, c = get_lines_from_file('t.txt', c, 15)
    while lns is not None:
        lns, c = get_lines_from_file('t.txt', c, 15)
        print(lns)
