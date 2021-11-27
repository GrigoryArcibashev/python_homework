#!/usr/bin/env python3

import argparse
import os.path
import struct
import sys
from pathlib import Path
from typing import NamedTuple


class TarParser:
    _HEADER_FMT1 = '100s8s8s8s12s12s8sc100s255s'  # 10(9)8
    _HEADER_FMT2 = '6s2s32s32s8s8s155s12s'  # 8   15
    _HEADER_FMT3 = '6s2s32s32s8s8s12s12s112s31x'  # 10
    _READ_BLOCK = 16 * 2 ** 20
    _RECORD_SIZE = 512

    _FILE_TYPES = {
            b'0': 'Regular file',
            b'1': 'Hard link',
            b'2': 'Symbolic link',
            b'3': 'Character device node',
            b'4': 'Block device node',
            b'5': 'Directory',
            b'6': 'FIFO node',
            b'7': 'Reserved',
            b'D': 'Directory entry',
            b'K': 'Long linkname',
            b'L': 'Long pathname',
            b'M': 'Continue of last file',
            b'N': 'Rename/symlink command',
            b'S': "`sparse' regular file",
            b'V': "`name' is tape/volume header name"
            }

    def __init__(self, filename):
        """
        Открывает tar-архив 'filename' и производит его предобработку
        (если требуется)
        """
        self._archive_name = filename
        self._files_stat = dict()
        with open(filename, 'rb') as arch:
            record = arch.read(self._RECORD_SIZE)
            while self._decode(record):
                header = self._get_full_header(record)
                if self._FILE_TYPES[header[7]] == 'Regular file':
                    self._files_stat[self._decode(header[0])] = header
                file_size = convert_to_dec_from_oct(self._decode(header[4]))
                if file_size % self._RECORD_SIZE != 0:
                    file_size += \
                        self._RECORD_SIZE - file_size % self._RECORD_SIZE
                arch.seek(file_size, 1)
                record = arch.read(self._RECORD_SIZE)

    def extract(self, dest=os.getcwd()):
        """
        Распаковывает данный tar-архив в каталог 'dest'
        """

        with open(self._archive_name, 'rb') as arch:
            record = arch.read(self._RECORD_SIZE)
            while self._decode(record):
                header = self._get_full_header(record)
                filename = self._decode(header[0])
                file_size = convert_to_dec_from_oct(self._decode(header[4]))
                path = Path(dest + '\\' + filename)
                if self._FILE_TYPES[header[7]] == 'Directory':
                    Path.mkdir(path)
                    arch.seek(file_size, 1)
                else:
                    with open(path, 'wb') as file:
                        r = arch.read(file_size)
                        file.write(r.strip(b'\x00'))
                if file_size % self._RECORD_SIZE != 0:
                    arch.seek(
                            self._RECORD_SIZE - file_size % self._RECORD_SIZE,
                            1)
                record = arch.read(self._RECORD_SIZE)

    def files(self):
        """
        Возвращает итератор имён файлов (с путями) в архиве
        """
        for filename in self._files_stat.keys():
            yield filename

    def file_stat(self, filename):
        """
        Возвращает информацию о файле 'filename' в архиве.

        Пример (некоторые поля могут отсутствовать, подробности см. в описании
        формата tar):
        [
            ('Filename', '/NSimulator'),
            ('Type', 'Directory'),
            ('Mode', '0000755'),
            ('UID', '1000'),
            ('GID', '1000'),
            ('Size', '0'),
            ('Modification time', '29 Mar 2014 03:52:45'),
            ('Checksum', '5492'),
            ('User name', 'victor'),
            ('Group name', 'victor')
        ]
        """
        if filename not in self.files():
            raise ValueError(filename)

        info = [('Filename', filename)]

        # TODO

        return info

    def _get_full_header(self, headers):
        headers = struct.unpack(self._HEADER_FMT1, headers)
        header_part2 = headers[-1]
        if header_part2.startswith(b'ustar\x00'):
            header_part2 = struct.unpack(self._HEADER_FMT2, header_part2)
        elif header_part2.startswith(b'ustar '):
            header_part2 = struct.unpack(self._HEADER_FMT3, header_part2)
        else:
            return headers[:-1]
        return headers[:-1] + header_part2

    @staticmethod
    def _decode(coded):
        return coded.strip(b'\x00').decode()


class TarHeader(NamedTuple):
    file_name: str
    file_mode: str
    UID: str
    GID: str
    file_size: str
    last_modification_time: str
    checksum: str
    link_indicator: str
    name_of_linked_file: str
    extends: str


def convert_to_dec_from_oct(num: str):
    if num.startswith('0o'):
        return int(num, 8)
    return int('0o' + num, 8)


def print_file_info(stat, f=sys.stdout):
    max_width = max(map(lambda s: len(s[0]), stat))
    for field in stat:
        print("{{:>{}}} : {{}}".format(max_width).format(*field), file=f)


def main():
    parser = argparse.ArgumentParser(
            usage='{} [OPTIONS] FILE'.format(os.path.basename(sys.argv[0])),
            description='Tar extractor')
    parser.add_argument(
            '-l', '--list', action='store_true', dest='ls',
            help='list the contents of an archive')
    parser.add_argument(
            '-x', '--extract', action='store_true', dest='extract',
            help='extract files from an archive')
    parser.add_argument(
            '-i', '--info', action='store_true', dest='info',
            help='get information about files in an archive')
    parser.add_argument(
            'fn', metavar='FILE',
            help='name of an archive')

    args = parser.parse_args()
    if not (args.ls or args.extract or args.info):
        sys.exit("Error: action must be specified")

    try:
        tar = TarParser(args.fn)

        if args.info:
            for fn in sorted(tar.files()):
                print_file_info(tar.file_stat(fn))
                print()
        elif args.ls:
            for fn in sorted(tar.files()):
                print(fn)

        if args.extract:
            tar.extract()
    except Exception as e:
        sys.exit(e)


if __name__ == '__main__':
    main()
    # my_main()
