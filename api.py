"""Main API file for backend CLTK webapp.

The Texts class parses files to get their metadata. This is super cludgy and needs to be redone somehow.
"""

import os
from flask import Flask
from flask import request  # for getting query string
from flask import json, jsonify
# eg: request.args.get('user') will get '?user=some-value'
from flask_restful import Resource, Api
from flask.ext.pymongo import PyMongo
from ingest.resources import Ingest
from api.resources import Query
from util.jsonp import jsonp

app = Flask(__name__)
mongo = PyMongo(app)
api = Api(app)


class Authors(Resource):

    @jsonp
    def get(self, lang, corpus_name):
        # assert lang in ['greek', 'latin']
        text_path = os.path.expanduser('~/cltk_data/' + lang + '/text/' + lang + '_text_' + corpus_name)

        dir_contents = os.listdir(text_path)

        # Sulpicia dir has no Latin texts
        # Isocrates dir has no Greek texts
        remove_files = ['README.md', '.git', 'LICENSE.md', 'perseus_compiler.py', '.DS_Store', 'Sulpicia' , 'Isocrates']

        dir_contents = [f for f in dir_contents if f not in remove_files]

        return {'authors': sorted(dir_contents) }


class Texts(Resource):

    @jsonp
    def get(self, lang, corpus_name, author_name):
        text_path = os.path.expanduser(
            '~/cltk_data/' + lang + '/text/' + lang + '_text_' + corpus_name + '/' + author_name.casefold() + '/opensource')  # casefold() prob not nec
        dir_contents = os.listdir(text_path)
        ending = ''
        if corpus_name == 'perseus' and lang == 'greek':
            ending = '_gk.xml.json'
            if author_name.casefold() == 'aratus':
                ending = '.xml.json'
            elif author_name.casefold() == 'jebborators':
                ending = '.xml.json'
            elif author_name.casefold() == 'lucretius':
                ending = '_lat.xml.json'
            elif author_name.casefold() == 'lycophron':
                ending = '.xml.json'
            elif author_name.casefold() == 'nonnos':
                ending = '.xml.json'
            elif author_name.casefold() == 'tryphiodorus':
                ending = '.xml.json'
            elif author_name.casefold() == 'callimachus':
                ending = '.xml.json'
        elif corpus_name == 'perseus' and lang == 'latin':
            ending = '_lat.xml.json'
            # weird exceptions
            if author_name.casefold() == 'histaugust':
                ending = '.xml.json'
            elif author_name.casefold() == 'quintus':
                ending = '.xml.json'
        dir_contents = [f for f in dir_contents if f.endswith(ending)]
        dir_contents = [f.casefold() for f in dir_contents]  # this probably isn't nec
        return json.dumps( {'texts': sorted(dir_contents)} )


class Text(Resource):

    @jsonp
    def get(self, lang, corpus_name, author_name, fname):

        text_path = os.path.expanduser(
            '~/cltk_data/') + lang + '/text/' + lang + '_text_' + corpus_name + '/' + author_name + '/opensource/' + fname
        ending = ''
        if corpus_name == 'perseus' and lang == 'greek':
            ending = '_gk.xml.json'
            if author_name.casefold() == 'aratus':
                ending = '.xml.json'
            elif author_name.casefold() == 'jebborators':
                ending = '.xml.json'
            elif author_name.casefold() == 'lucretius':
                ending = '_lat.xml.json'
            elif author_name.casefold() == 'lycophron':
                ending = '.xml.json'
            elif author_name.casefold() == 'nonnos':
                ending = '.xml.json'
            elif author_name.casefold() == 'tryphiodorus':
                ending = '.xml.json'
            elif author_name.casefold() == 'callimachus':
                if fname.startswith('call_0'):
                    ending = '.xml.json'
        elif corpus_name == 'perseus' and lang == 'latin':
            ending = '_lat.xml.json'
            # weird exceptions
            if author_name.casefold() == 'histaugust' or author_name.casefold() == 'quintus':
                ending = '.xml.json'

        text_path += ending
        with open(text_path, "r") as f:  # TODO: use json.loads() for all this
            file_string = f.read()
        file_json = json.loads(file_string)

        # Some files are odd
        if author_name.casefold() in ['quintus', 'aratus', 'callimachus', 'colluthus', 'lycophron', 'nonnos', 'tryphiodorus']:
            encoding_desc = file_json['TEI.2']['teiHeader']['encodingDesc']
            if type(encoding_desc) is list:
                for desc in encoding_desc:
                    try:
                        quintus = True
                        refs_decls = desc.get('refsDecl')
                        break
                    except Exception:
                        pass
        # everyone else
        else:
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
                    step = refs_decl['step']
                    unit = step['@refunit']
                    section_types.append([unit])
            elif refs_decl.get('@doctype') != 'TEI.2' and 'step' in refs_decl:
                print('*' * 40)
                steps = refs_decl['step']
                if type(steps) is list:
                    units = []
                    for state in steps:
                        unit = state['@refunit']
                        units.append(unit)
                    section_types = [units]
                elif type(steps) is dict:
                    step = refs_decl['step']
                    unit = step['@refunit']
                    section_types.append([unit])

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


        # Parse query strings
        q_section_1 = request.args.get('section_1')
        q_section_2 = request.args.get('section_2')
        q_section_3 = request.args.get('section_3')
        q_section_4 = request.args.get('section_4')
        q_section_5 = request.args.get('section_5')

        # If no query string, return text object
        if not q_section_1:
            return {'refs_decl': refs_decls,
                    'filepath': text_path,
                    'section_types': section_types,
                    'text': file_json['TEI.2']['text']
                    }

        # Parse text according to query string
        section_1_object = file_json['TEI.2']['text']['body']['div1']

        if type(section_1_object) is list:
            for section_1 in section_1_object:
                try:
                    section_1_number = section_1['@n']  # str
                except KeyError:
                    # http://localhost:5000/lang/greek/corpus/perseus/author/Aeschylus/text/aesch.ag?section_1=1
                    # Something funny. Redefine section_1 to s.th. deeper embedded
                    #! This pathway is broke and I don't know if I want to make this more convoluted than it is. Dammit.
                    section_1 = section_1['div2']['sp']

                if section_1_number == q_section_1:
                    section_1_object = section_1['l']  # list

                    # cleanup lines
                    return_section_1_object = []
                    for line in section_1_object:
                        if type(line) is dict:
                            line = line['#text']
                        return_section_1_object.append(line)

                    if not q_section_2:
                        # http://localhost:5000/lang/latin/corpus/perseus/author/Vergil/text/verg.a?section_1=12
                        # http://localhost:5000/lang/greek/corpus/perseus/author/Homer/text/hom.od?section_1=1
                        return {'refs_decl': refs_decls,
                                'filepath': text_path,
                                'section_types': section_types,
                                'text': return_section_1_object
                                }

                    for counter, section_2_item in enumerate(section_1_object):
                        if type(section_2_item) is dict:
                            section_2_item = section_2_item['#text']
                        if counter + 1 == int(q_section_2):
                            returned_text = section_2_item

            if not q_section_3:
                return {'refs_decl': refs_decls,
                        'filepath': text_path,
                        'section_types': section_types,
                        'text': returned_text,
                        }

        elif type(section_1_object) is dict:
            # http://localhost:5000/lang/greek/corpus/perseus/author/Hesiod/text/hes.th?section_1=1
            section_1_type = section_1_object['@type']
            section_1_number = section_1_object['@n']
            section_1_list = section_1_object['l']

            # cleanup lines
            return_section_1_object = []
            for line in section_1_list:
                if type(line) is dict:
                    line = line['#text']
                return_section_1_object.append(line)

            for counter, section_1_item in enumerate(section_1_list):
                if type(section_1_item) is dict:
                    section_1_item = section_1_item['#text']
                if counter + 1 == int(q_section_1):
                    returned_text = section_1_item

            return {'refs_decl': refs_decls,
                    'filepath': text_path,
                    'section_types': section_types,
                    'text': returned_text
                    }


# http://localhost:5000/lang/greek/corpus/perseus/authors
api.add_resource(Authors, '/lang/<string:lang>/corpus/<string:corpus_name>/authors')

# http://localhost:5000/lang/greek/corpus/perseus/author/Homer/texts
api.add_resource(Texts, '/lang/<string:lang>/corpus/<string:corpus_name>/author/<string:author_name>/texts')

# http://localhost:5000/lang/latin/corpus/perseus/author/Vergil/text/verg.a
# http://localhost:5000/lang/greek/corpus/perseus/author/Homer/text/hom.od

# http://localhost:5000/lang/latin/corpus/perseus/author/Vergil/text/verg.a?section_1=1&section_2=1
# http://localhost:5000/lang/greek/corpus/perseus/author/Homer/text/hom.od?section_1=1&section_2=1
api.add_resource(Text,
                 '/lang/<string:lang>/corpus/<string:corpus_name>/author/<string:author_name>/text/<string:fname>')

# Trigger new document ingest
api.add_resource(Ingest, '/ingest')

# Feed GET params to query to DB
api.add_resource(Query, '/query')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0')
