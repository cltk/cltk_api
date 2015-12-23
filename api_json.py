"""Open JSON file and serve."""

import json
import os

from flask import Flask
from flask import request  # for getting query string
# eg: request.args.get('user') will get '?user=some-value'
from flask_restful import Resource, Api
from util.jsonp import jsonp


app = Flask(__name__)
api = Api(app)


# example
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


# example
class TodoSimple(Resource):
    def get(self, todo_id):
        return {'example with token': todo_id}


def open_json(fp):
    """Open json file, return json."""
    with open(fp) as fo:
        return json.load(fo)


def get_cltk_text_dir(lang):
    """Take relative filepath, return absolute"""
    cltk_home = os.path.expanduser('~/cltk_data')
    text_dir = os.path.join(cltk_home, lang.casefold(), 'text', lang.casefold() + '_text_perseus', 'json')
    return text_dir


class Text(Resource):

    def get(self, lang, corpus, author, work):

        _dir = get_cltk_text_dir(lang)

        files = os.listdir(_dir)
        for file in files:
            if file.startswith(author) and file.endswith(work + '.json'):
                file_author, file_work = file.split('__')

                if file_author == author and file_work[:-5] == work:
                    json_fp = os.path.join(_dir, file)

                file_dict = open_json(json_fp)
                text = file_dict['text']

                chunk1 = request.args.get('chunk1')
                chunk2 = request.args.get('chunk2')
                chunk3 = request.args.get('chunk3')

                if chunk1:
                    text = text[chunk1]

                if chunk2:
                    text = text[chunk2]

                if chunk3:
                    text = text[chunk3]

                return {'language': lang,
                        'corpus': corpus,
                        'author': author,
                        'work': work,
                        'text': text,
                        'meta': file_dict['meta'],
                        }


class Lang(Resource):
    def get(self):

        cltk_home = os.path.expanduser('~/cltk_data')
        dirs = os.listdir(cltk_home)
        langs_with_perseus_corpus = []
        for _dir_lang in dirs:
            is_perseus_corpus = get_cltk_text_dir(_dir_lang)
            if os.path.isdir(is_perseus_corpus):
                langs_with_perseus_corpus.append(_dir_lang)

        return {'languages': langs_with_perseus_corpus}


class Corpus(Resource):

    def get(self, lang):

        possible_perseus_corpora_json = get_cltk_text_dir(lang)
        possible_perseus_corpora = os.path.split(possible_perseus_corpora_json)[0]
        is_perseus = os.path.isdir(possible_perseus_corpora)
        corpora = []
        if is_perseus and possible_perseus_corpora.endswith('_perseus'):
            corpus_name = os.path.split(possible_perseus_corpora)[1]
            corpora.append('perseus')

        return {'language': lang,
                'corpora': corpora}

class Author(Resource):
    def get(self, lang, corpus):
        '''
        _dir = os.path.join('json', lang, corpus)
        dirs = os.listdir(_dir)
        authors_raw = [f[:-5] for f in dirs if f.endswith('.json')]
        authors = {x.split('__')[0] : x.split('__')[1] for x in authors_raw }
        '''

        possible_perseus_corpora_json = get_cltk_text_dir(lang)

        authors = set()   # use set to avoid dupes
        if os.path.isdir(possible_perseus_corpora_json):
            files = os.listdir(possible_perseus_corpora_json)
            for file in files:
                author = file.split('__')[0]
                authors.add(author)
        else:
            print('Corpus not installed into "~/cltk_data".')

        return {'language': lang,
                'authors': list(authors)}  # cast to list, set() not serializable

class Texts(Resource):
    def get(self, lang, corpus, author):
        #! KJ: Start here next, make read from ~/cltk_data
        _dir = os.path.join('json', lang, corpus)
        dirs = os.listdir(_dir)
        authors_raw = [f[:-5] for f in dirs if f.endswith('.json')]
        author_text_list = [x for x in authors_raw if x.startswith(author)]
        texts = [x.split('__')[1] for x in author_text_list]
        return {'language': lang,
                'corpus': corpus,
                'author': author,
                'texts': texts}

# http://localhost:5000/lang/latin/corpus/perseus/author/vergil/text
# http://localhost:5000/lang/greek/corpus/perseus/author/homer/text
api.add_resource(Texts, '/lang/<string:lang>/corpus/<string:corpus>/author/<string:author>/text')

# http://localhost:5000/lang/latin/corpus/perseus/author
api.add_resource(Author, '/lang/<string:lang>/corpus/<string:corpus>/author')

# http://localhost:5000/lang/latin/corpus
api.add_resource(Corpus, '/lang/<string:lang>/corpus')


# http://localhost:5000/lang
api.add_resource(Lang, '/lang')


# http://localhost:5000/lang/greek/corpus/perseus/author/achilles_tatius/text/leucippe_et_clitophon?chunk1=1&chunk2=1&chunk3=1
# http://localhost:5000/lang/greek/corpus/perseus/author/homer/text/odyssey
# http://localhost:5000/lang/greek/corpus/perseus/author/homer/text/odyssey?chunk1=1&chunk2=1
api.add_resource(Text, '/lang/<string:lang>/corpus/<string:corpus>/author/<string:author>/text/<string:work>')
#api.add_resource(Text, '/lang/<string:lang>/corpus/<string:corpus>/author/<string:author>/text/<string:work>/<string:chunk1>')

# simple examples
api.add_resource(TodoSimple, '/todo/<string:todo_id>')
api.add_resource(HelloWorld, '/hello')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0')
