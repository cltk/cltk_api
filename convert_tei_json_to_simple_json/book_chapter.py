"""Example: Ammianus"""

import json
import os

from book_line import file_to_dict
from book_line import dict_to_file



def book_chapter_convert(fp):
    """Take filepath, try to make new file.
    {'author': author_name,
      'text': [
        {'book': 1,
         'chapters':
           [{'chapter': 1, 'text': real_text}, …]
        }
      ]
    }
    """
    final_file_dict = {}
    books_list = []
    file_dict = file_to_dict(fp)

    tei = file_dict['TEI.2']  # dict
    text = tei['text']  # dict
    header = tei['teiHeader']  # dict
    encoding = header['encodingDesc']  # dict
    body = text['body']  # dict
    div1 = body['div1']  # list of dict
    #print(len(div1))  # eg 12 for Aeneid, 24 for Iliad
    for div1_dict in div1:  # !Book loop
        #print(div1_dict.keys())
        book_dict = {}
        div1_dict_div2 = div1_dict['div2']  # list of dict; where the text at
        div1_dict_type = div1_dict['@type']   # book
        try:
            div1_dict_pb = div1_dict['pb']  # dict or list of dict: [{'@id': 'v2.p.16'}, {'@id': 'v2.p.30'}, {'@id': 'v2.p.68'}]
        except KeyError:
            div1_dict_pb = None
        div1_dict_head = div1_dict['head']  # str, eg: 'Liber XVII'
        div1_dict_number = div1_dict['@n']  # str, eg: 17, 'val1'
        book_number = div1_dict_number
        #print('Book:', book_number)
        book_dict['book'] = book_number

        chapters_list = []  # a list of {<chp_number>: <chptr text>}
        for div2 in div1_dict_div2:  # !Chapter Loop

            chapter_dict = {}
            chapter_text = []
            #print(type(div2))  # dict
            div2_type = div2['@type']  # str: chapter
            div2_number = div2['@n']  # 6, 12, 4
            chapter_number = div2_number
            #print('Chapter:', chapter_number)
            try:
                div2_argument = div2['argument']  # dict: {'p': 'Quo patre natus sit, et quas res princeps gesserit.'} (text in here)
                div2_text_section = div2_argument['p']  # ! Summary text here, not useful (I think)
                #print('div2_text_section', div2_text_section)
                if type(div2_text_section) is dict:
                    #print(div2_text_section.keys())  # ['note', '#text'] or ['corr', '#text']
                    div2_text_section_note = div2_text_section['note']  # summaries
                    div2_text_section_text = div2_text_section['text']  # empty
                    div2_text_section_corr = div2_text_section['corr']  # empty
                elif type(div2_text_section) is str:
                    pass
                    #print(div2_text_section)  # ! real text here! (I think)
            except KeyError:
                div2_argument = None
            div2_ps = div2['p']  # list of dicts or dict (text in here)
            if type(div2_ps) is dict:
                #print(div2_ps.keys())  # ['note', 'quote', 'milestone', 'pb', '#text']
                try:
                    div2_ps_note = div2_ps['note']  # [{'hi': {'#text': 'et ad molliora,', '@rend': 'italics'}, '#text': 'added in G; V omits.'}, … ]
                except KeyError:
                    div2_ps_note = None
                try:
                    div2_ps_quote = div2_ps['quote']  # ['Nemo', 'vereatur: habeo firmiter quod tenebam.', {'@rend': 'blockquote', 'l': [{'foreign': {'@lang': 'greek', '#text': 'Zeu\\s o(/tan ei)s platu\\ te/rma mo/lh| klutou= u(droxo/oio,'}}, … ]
                except KeyError:
                    div2_ps_quote = None
                div2_ps_milestone = div2_ps['milestone']
                try:
                    div2_ps_pb = div2_ps['pb']  # [{'@id': 'v3.p.316'}, {'@id': 'v3.p.318'}] or {'@id': 'v2.p.190'}
                except KeyError:
                    div2_ps_pb = None
                div2_ps_text = div2_ps['#text']  # ! actual text!
                real_text = div2_ps_text
                chapter_text.append(real_text)
                #print('div2_ps_text', div2_ps_text)
            elif type(div2_ps) is list:
                for div2_ps_item in div2_ps:  # all dicts
                    #print(div2_ps_item.keys())  # ['pb', 'milestone', 'note', '#text', 'quote']
                    #div2_ps_item_pb = div2_ps_item['pb']
                    #div2_ps_item_milestone = div2_ps_item['milestone']
                    #div2_ps_item_note = div2_ps_item['note']
                    try:
                        div2_ps_item_text = div2_ps_item['#text']  # ! real text here
                        real_text = div2_ps_item_text
                        chapter_text.append(real_text)
                        #print(div2_ps_item_text)
                    except KeyError:
                        div2_ps_item_text = None
                    #div2_ps_item_quote = div2_ps_item['quote']
            chapter_text_str = ' '.join(chapter_text)
            chapter_dict[chapter_number] = chapter_text_str
            chapters_list.append(chapter_dict)
        book_dict['book'] = book_number
        book_dict['chapters']= chapters_list
        books_list.append(book_dict)

    # Get author name from 'latin_key.json'
    key_fp = os.path.expanduser('~/cltk_data/latin/text/latin_text_perseus/latin_key.json')
    with open(key_fp) as fo:
        meta_authors = json.load(fo)
    for meta_author in meta_authors:
        orig_filename = meta_author['title']
        if orig_filename == os.path.split(fp)[1]:
            author_name = meta_author['name']
            #print(author_name)
            structure_meta = meta_author['encoding']['state']
            #book_dict['structure_meta'] = structure_meta
            #final_file_dict['structure_meta'] = structure_meta
            #book_dict['author_name'] = author_name
            final_file_dict['author'] = author_name
            break

    final_file_dict['text'] = books_list


    author_dir, author_file = os.path.split(fp)[0], os.path.split(fp)[1]
    author_file = author_file.replace('xml.', '')
    opensource_dir = os.path.split(author_dir)[0]
    perseus_root = os.path.split(opensource_dir)[0]
    # next write new perseus dir and put in there; check if present
    cltk_perseus_dir = 'cltk_formatted'
    cltk_perseus_path = os.path.expanduser(os.path.join(perseus_root, cltk_perseus_dir, author_name.casefold() + '_' + author_file))
    print('Wrote new file to: "{}".'.format(cltk_perseus_path))
    try:
        dict_to_file(final_file_dict, cltk_perseus_path)
    except FileNotFoundError:
        _dir = os.path.split(cltk_perseus_path)[0]
        os.mkdir(_dir)
        dict_to_file(final_file_dict, cltk_perseus_path)


if __name__ == "__main__":
    fp = '/Users/kyle/cltk_data/latin/text/latin_text_perseus/Ammianus/opensource/amm_lat.xml.json'
    book_line_convert(fp)

