"""Main API file for backend CLTK webapp."""

import os

from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

todos = {}
class TodoSimple(Resource):
    def get(self, todo_id):
        return {'asdasd': 'asdasd'}

perseus_latin_authors = []
class Authors(Resource):
    def get(self):
        p = os.path.expanduser('~/cltk_data/latin/text/latin_text_perseus/')
        _list = os.listdir(p)
        _list.remove('README.md')
        _list.remove('.git')
        return {'authors': _list}

api.add_resource(Authors, '/<string:lang>/authors')
api.add_resource(TodoSimple, '/todo/<string:todo_id>')
api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
