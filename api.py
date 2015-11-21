"""Main API file for backend CLTK webapp."""

import json
import os
# import pdb

from flask import Flask
from flask import request  # for getting query string
# eg: request.args.get('user') will get '?user=some-value'
from flask_restful import Resource, Api

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


class Authors(Resource):
    def get(self, lang, corpus_name):
        # assert lang in ['greek', 'latin']
        text_path = os.path.expanduser('~/cltk_data/' + lang + '/text/' + lang + '_text_' + corpus_name)
        dir_contents = os.listdir(text_path)
        remove_files = ['README.md', '.git', 'LICENSE.md', 'perseus_compiler.py', '.DS_Store']
        dir_contents = [f for f in dir_contents if f not in remove_files]
        return {'authors': sorted(dir_contents)}


class Texts(Resource):
    def get(self, lang, corpus_name, author_name):
        text_path = os.path.expanduser(
            '~/cltk_data/' + lang + '/text/' + lang + '_text_' + corpus_name + '/' + author_name.casefold() + '/opensource')  # casefold() prob not nec
        dir_contents = os.listdir(text_path)
        ending = ''
        if corpus_name == 'perseus' and lang == 'greek':
            ending = '_gk.xml.json'
        elif corpus_name == 'perseus' and lang == 'latin':
            ending = '_lat.xml.json'
            # weird exceptions
            if author_name.casefold() == 'histaugust':
                ending = '.xml.json'
        dir_contents = [f for f in dir_contents if f.endswith(ending)]
        dir_contents = [f.casefold() for f in dir_contents]  # this probably isn't nec
        return {'texts': sorted(dir_contents)}


class Text(Resource):
    def get(self, lang, corpus_name, author_name, fname):

        text_path = os.path.expanduser(
            '~/cltk_data/') + lang + '/text/' + lang + '_text_' + corpus_name + '/' + author_name + '/opensource/' + fname
        ending = ''
        if corpus_name == 'perseus' and lang == 'greek':
            ending = '_gk.xml.json'
        elif corpus_name == 'perseus' and lang == 'latin':
            ending = '_lat.xml.json'
            # weird exceptions
            if author_name.casefold() == 'histaugust':
                ending = '.xml.json'


        text_path += ending
        with open(text_path, "r") as f:
            file_string = f.read()

        file_json = json.loads(file_string)

        refs_decls = file_json['TEI.2']['teiHeader']['encodingDesc']['refsDecl']
        section_types = []  # list of lists
        if type(refs_decls) is list:
            for refs_decl in refs_decls:
                if refs_decl.get('@doctype') == 'TEI.2' and 'state' in refs_decl:
                    states = refs_decl['state']
                    if type(states) is list:
                        units = []
                        for state in states:
                            unit = state['@unit']
                            units.append(unit)
                        section_types.append(units)
                    elif type(states) is dict:
                        state = states
                        unit = state['@unit']
                        section_types.append([unit])
                elif 'state' in refs_decl:
                    states = refs_decl['state']
                    if type(states) is list:
                        units = []
                        for state in states:
                            unit = state['@unit']
                            units.append(unit)
                        section_types.append(units)

        elif type(refs_decls) is dict:
            refs_decl = refs_decls
            if refs_decl.get('@doctype') == 'TEI.2' and 'state' in refs_decl:
                states = refs_decl['state']
                if type(states) is list:
                    units = []
                    for state in states:
                        unit = state['@unit']
                        units.append(unit)
                    section_types = [units]
                elif type(states) is dict:
                    state = refs_decl['state']
                    unit = state['@unit']
                    section_types.append([unit])
            elif refs_decl.get('@doctype') == 'TEI.2' and 'step' in refs_decl:
                steps = refs_decl['step']
                if type(steps) is list:
                    units = []
                    for state in steps:
                        unit = state['@refunit']
                        units.append(unit)
                    section_types = [units]
                elif type(steps) is dict:
                    print('dict')
            # Some entries missing `{'@doctype': 'TEI.2'}` (eg, Pliny's `pliny.min.letters`)
            elif refs_decl.get('@doctype') != 'TEI.2' and 'state' in refs_decl:
                states = refs_decl['state']
                if type(states) is list:
                    units = []
                    for state in states:
                        unit = state['@unit']
                        units.append(unit)
                    section_types = [units]
                elif type(states) is dict:
                    state = refs_decl['state']
                    unit = state['@unit']
                    section_types.append([unit])




        return {'refs_decl': refs_decls,
                'filepath': text_path,
                'section_types': section_types,
                }

# http://localhost:5000/lang/greek/corpus/perseus/authors
api.add_resource(Authors, '/lang/<string:lang>/corpus/<string:corpus_name>/authors')

# http://localhost:5000/lang/greek/corpus/perseus/author/Homer/texts
api.add_resource(Texts, '/lang/<string:lang>/corpus/<string:corpus_name>/author/<string:author_name>/texts')

# http://localhost:5000/lang/latin/corpus/perseus/author/Vergil/text/verg.a
# http://localhost:5000/lang/greek/corpus/perseus/author/Homer/text/hom.od
api.add_resource(Text,
                 '/lang/<string:lang>/corpus/<string:corpus_name>/author/<string:author_name>/text/<string:fname>')  # Luke is doing

# simple examples
api.add_resource(TodoSimple, '/todo/<string:todo_id>')
api.add_resource(HelloWorld, '/hello')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0')
