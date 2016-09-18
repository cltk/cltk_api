"""Install CLTK corpora that can be served by the API."""

import os

from cltk.corpus.utils.importer import CorpusImporter

__author__ = ['Chaitanya Sai Alaparthi <achaitanyasai@gmail.com>']
__license__ = 'MIT License. See LICENSE'


def check_corpus_presence(lang, corpus):
    root = os.path.expanduser('~/cltk_data')
    _dir = os.path.join(root, lang, 'text', corpus, 'json')
    return os.path.isdir(_dir)


def main():
    lang = 'latin'
    corpus = 'latin_text_perseus'
    corpus_present = check_corpus_presence(lang, corpus)
    if not corpus_present:
        corpus_importer = CorpusImporter(lang)
        corpus_importer.import_corpus(corpus)

    lang = 'greek'
    corpus = 'greek_text_perseus'
    corpus_present = check_corpus_presence(lang, corpus)
    if not corpus_present:
        corpus_importer = CorpusImporter(lang)
        corpus_importer.import_corpus(corpus)


if __name__ == '__main__':
    main()
