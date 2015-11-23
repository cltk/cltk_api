"""Take the JSON conversion of the original Perseus XML, then convert it into
 easier-to-parse JSON.

TODO: Perhaps get full author name and work name out of XML.
"""

import json
import os
import sys


def file_to_dict(fp):
    """Open a json file and return Python dict."""
    with open(os.path.expanduser(fp)) as fo:
        return json.load(fo)


def dict_to_file(obj, fp):
    """Write dict to json file."""
    with open(os.path.expanduser(fp), 'w') as fo:
        json.dump(obj, fo)


def book_line_convert(fp):
    """Take filepath, try to make new file.
    new_object{'meta': ['book', 'line'],
      'text': [
        {'book': 1,
         'line': ['aaaaa', 'bbbbb', 'cccc']}
    ]}
    """
    final_file_dict = {}
    text_books_list = []
    file_dict = file_to_dict(fp)

    tei = file_dict['TEI.2']  # dict
    text = tei['text']  # dict
    header = tei['teiHeader']  # dict
    encoding = header['encodingDesc']  # dict
    body = text['body']  # dict
    div1 = body['div1']  # list of dict
    #print(len(div1))  # eg 12 for Aeneid, 24 for Iliad
    for div1_dict in div1:
        book_object = {}
        text_lines = []
        milestone = div1_dict['milestone']  # list, not useful
        _type = div1_dict['@type']  # str, 'Book'
        book_number = int(div1_dict['@n'])  # str cast as int
        div1_dict_list = div1_dict['l']  # list of str or dict
        for counter, div1_dict_list_object in enumerate(div1_dict_list, start=1):
            if type(div1_dict_list_object) is dict:
                try:
                    div1_dict_list_object_number = div1_dict_list_object['@n']  # str
                except KeyError:
                    div1_dict_list_object_number = None
                try:
                    div1_dict_list_object_milestone = div1_dict_list_object['milestone']  # dict, eg Aen and Il: {'@ed': 'P', '@unit': 'para'}
                except KeyError:
                    div1_dict_list_object_milestone = None
                div1_dict_list_object_text = div1_dict_list_object['#text']  # the actual text
                div1_dict_list_object = div1_dict_list_object_text  # str
            else:
                pass
            #print(book_number, counter, div1_dict_list_object)
            text_lines.append(div1_dict_list_object)
        book_object['text'] = text_lines
        book_object['book'] = book_number

        # Get author name from 'latin_key.json'
        key_fp = os.path.expanduser('~/cltk_data/latin/text/latin_text_perseus/latin_key.json')
        with open(key_fp) as fo:
            meta_authors = json.load(fo)
        for meta_author in meta_authors:
            orig_filename = meta_author['title']
            if orig_filename == os.path.split(fp)[1]:
                author_name = meta_author['name']
                #structure_meta = meta_author['encoding']['state']
                #book_object['structure_meta'] = structure_meta
                #book_object['author_name'] = author_name
                final_file_dict['author'] = author_name
                break

        text_books_list.append(book_object)
    #print(len(text_books_list))  # eg 12 for Aen, 4 for Georgics, 24 for Od

    final_file_dict['text'] = text_books_list

    author_dir, author_file = os.path.split(fp)[0], os.path.split(fp)[1]
    author_file = author_file.replace('xml.', '')
    opensource_dir = os.path.split(author_dir)[0]
    perseus_root = os.path.split(opensource_dir)[0]
    # next write new perseus dir and put in there; check if present
    cltk_perseus_dir = 'cltk_formatted'
    cltk_perseus_path = os.path.expanduser(os.path.join(perseus_root, cltk_perseus_dir, author_file))
    print('Wrote new file to: "{}".'.format(cltk_perseus_path))
    try:
        dict_to_file(final_file_dict, cltk_perseus_path)
    except FileNotFoundError:
        _dir = os.path.split(cltk_perseus_path)[0]
        os.mkdir(_dir)
        dict_to_file(final_file_dict, cltk_perseus_path)

if __name__ == "__main__":

    examples_files = ['~/cltk_data/latin/text/latin_text_perseus/Vergil/opensource/verg.a_lat.xml.json',
                      #'~/cltk_data/latin/text/latin_text_perseus/Vergil/opensource/verg.ecl_lat.xml.json',  # KeyError: 'milestone'
                      '~/cltk_data/latin/text/latin_text_perseus/Vergil/opensource/verg.g_lat.xml.json',
                      '~/cltk_data/latin/text/latin_text_perseus/Ovid/opensource/ovid.met_lat.xml.json',
                      #'~/cltk_data/latin/text/latin_text_perseus/Ovid/opensource/ovid.am_lat.xml.json',  # KeyError: 'body'
                      #'~/cltk_data/latin/text/latin_text_perseus/Ovid/opensource/ovid.fast_lat.xml.json',  # KeyError: 'milestone'
                      #'~/cltk_data/latin/text/latin_text_perseus/Ovid/opensource/ovid.ibis_lat.xml.json',  # TypeError: string indices must be integers
                      #'~/cltk_data/latin/text/latin_text_perseus/Ovid/opensource/ovid.pont_lat.xml.json',  # KeyError: 'milestone'
                      #'~/cltk_data/latin/text/latin_text_perseus/Ovid/opensource/ovid.tr_lat.xml.json',  # KeyError: 'milestone'
                      '~/cltk_data/greek/text/greek_text_perseus/Homer/opensource/hom.il_gk.xml.json',
                      '~/cltk_data/greek/text/greek_text_perseus/Homer/opensource/hom.od_gk.xml.json'
                      ]

    for fp in examples_files:
        book_line_convert(fp)