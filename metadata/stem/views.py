from cltk.stem.latin.stem import Stemmer
from flask_restful import Resource

class Stem(Resource):
    """
    GET     /core/stem/<string:sentence>
            Takes sentence input and strips suffix using CLTK's core Stemmer
    """

    def get(self, sentence):
        stemmer = Stemmer()
        return {'stemmed_output': stemmer.stem(sentence.lower())}
