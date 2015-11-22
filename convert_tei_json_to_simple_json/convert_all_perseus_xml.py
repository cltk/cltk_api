"""Look for all Perseus files, then try to convert with available converters.
 If error rises, then try another converter.

Outputs to: '~/cltk_data/greek/text/greek_text_perseus/cltk_formatted' and
 '~/cltk_data/latin/text/latin_text_perseus/cltk_formatted'.
"""

import os
import sys

from book_line import book_line_convert
from book_chapter import book_chapter_convert


def os_walk(fp, ending='.xml.json'):
    """Recursively find files in path."""
    for dir_path, dir_names, files in os.walk(fp):  # pylint: disable=W0612
        for name in files:
            if name.endswith(ending):
                yield os.path.join(dir_path, name)


if __name__ == "__main__":
    perseus_dirs = ['~/cltk_data/latin/text/latin_text_perseus/', '~/cltk_data/greek/text/greek_text_perseus/']
    xml_converter = [book_line_convert, book_chapter_convert]
    success_count = 0
    fail_count = 0
    for perseus_dir in perseus_dirs:
        for fp in os_walk(os.path.expanduser(perseus_dir)):
            for converter in xml_converter:
                try:
                    book_line_convert(fp)
                    success_count += 1
                    break
                except:
                    pass
            fail_count += 1
    print('Sucess:', success_count)
    print('Fail:', fail_count)