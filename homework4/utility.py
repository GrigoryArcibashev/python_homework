import os
import os.path
import sys
from enum import Enum

MODES = Enum('MODES', 'POPULAR_RESOURCE POPULAR_USER HELP')


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
        report_error('Файл {} не найден'.format(filepath), 2)


def report_error(error_message: str, error_code: int):
    """
    Информирует об оишбке, после чего аварийно завершает выполнение программы
    """
    print(
            '%s.\n' % error_message +
            'Об использовании утилиты можно ' +
            'узнать с помощью команды help:\n' +
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


def read_lines(file_path: str, start_byte: int, max_bytes: int):
    """
    Возвращает список строк из файла и указатель на следующий
    непрочитанный байт в файле. Первая строка начинается
    с позиции start_byte. Будет возвращено минимальное количество строк,
    чья суммарная длина состовялет не меньше max_bytes.
    """
    with open(file_path, 'r', encoding='cp1251') as file:
        def safe_line_reading():
            try:
                return file.readline()
            except UnicodeDecodeError:
                report_error('Ошибка при чтении файла с логами', 3)

        file.seek(start_byte)
        lines = list()
        number_of_bytes_read = 0
        line = safe_line_reading()
        while line and number_of_bytes_read < max_bytes:
            lines.append(line)
            number_of_bytes_read += len(line)
            line = safe_line_reading()
        return lines if lines else None, start_byte + number_of_bytes_read


def find_most_popular_resource(file_path: str):
    """
    Возвращает самый популярный ресурс.
    Если найти такой не получилось, возвращает None.
    """
    return get_max_of_column_from_file(file_path, -2)


def find_most_active_user(file_path: str):
    """
    Возвращает самого активного клиента.
    Если найти такого не получилось, возвращает None.
    """
    return get_max_of_column_from_file(file_path, 0)


def get_max_of_column_from_file(file_path: str, column_number: int):
    """
    Возвращает максимальный элемент из столбца в указнном файле лога.
    Если найти такой не получилось, возвращает None.
    """
    stat = dict()
    buffer_size = 10 * 1024 * 1024
    lines, start_byte = read_lines(file_path, 0, buffer_size)
    while lines is not None:
        for line in lines:
            columns = list(
                    filter(
                            lambda l: len(l) > 0,
                            map(lambda l: l.strip(), line.split(','))))
            if len(columns) == 15:
                try:
                    stat[columns[column_number]] += 1
                except KeyError:
                    stat[columns[column_number]] = 1
        lines, start_byte = read_lines(file_path, start_byte, buffer_size)
    return max(stat, key=lambda k: stat[k]) if stat else None


def get_help():
    """
    Возвращает помощь по использованию утилиты
    """
    return """
    Утилита, которая по данному логу, согласно параметрам, выдаёт одну 
    из статистик: самый популярный ресурс и самый активный клиент.
    
    python {0} [path_to_log_file] help
       Помощь по использованию утилиты
       Если лог указан, он игнорируется
    
    python {0} path_to_log_file popular_resource
        Выдать самый популярный ресурс
        
    python {0} path_to_log_file popular_user
        Выдать самого активного клиента
    """.format(sys.argv[0])


def print_result_of_work(result: str):
    if result:
        print(result)
    else:
        report_error('Не удалось получить результат', 0)


def main():
    file_path, mode = get_arguments()
    if mode is MODES.POPULAR_RESOURCE:
        print_result_of_work(find_most_popular_resource(file_path))
    elif mode is MODES.POPULAR_USER:
        print_result_of_work(find_most_active_user(file_path))
    else:
        print_result_of_work(get_help())


if __name__ == '__main__':
    main()
