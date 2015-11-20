"""Main API file for backend CLTK webapp."""

import os
import pdb

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# example
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

# example
todos = {}
class TodoSimple(Resource):
    def get(self, todo_id):
        return {'example with token': todo_id}


class Authors(Resource):
    def get(self, lang):
        #assert lang in ['greek', 'latin']
        text_path = os.path.expanduser('~/cltk_data/' + lang + '/text/' + lang + '_text_perseus/')
        dir_contents = os.listdir(text_path)
        remove_files = ['README.md', '.git', 'LICENSE.md', 'perseus_compiler.py', '.DS_Store']
        dir_contents = [f for f in dir_contents if f not in remove_files]
        return {'authors': sorted(dir_contents)}


class Texts(Resource):
    def get(self, lang, author_name):
        text_path = os.path.expanduser('~/cltk_data/' + lang + '/text/' + lang + '_text_perseus/' + author_name.casefold() + '/opensource')  # casefold() prob not nec
        dir_contents = os.listdir(text_path)
        if lang == 'greek':
            ending = '_gk.xml.json'
        elif lang == 'latin':
            ending = '_lat.xml.json'
        dir_contents = [f for f in dir_contents if f.endswith(ending)]
        dir_contents = [f.casefold() for f in dir_contents]  # this probably isn't nec
        return {'texts': sorted(dir_contents)}

class Text(Resource):
    def get(self, lang, author_name, fname):
        print(True)
        text_path = os.path.expanduser('~') + '/cltk_data/' + lang + '/text/' + lang + '_text_perseus/' + author_name + '/opensource/' + fname
        if lang == 'greek':
            ending = '_gk.xml.json'
        elif lang == 'latin':
            ending = '_lat.xml.json'

        text_path += ending

        print( '********', text_path )
        with open( text_path, "r" ) as f:

            file_string = f.read()

        return { fname : file_string }

api.add_resource(Authors, '/<string:lang>/authors')
api.add_resource(Texts, '/<string:lang>/author/<string:author_name>/texts')
api.add_resource(Text, '/<string:lang>/author/<string:author_name>/text/<string:fname>')  # Luke is doing
api.add_resource(TodoSimple, '/todo/<string:todo_id>')
api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
