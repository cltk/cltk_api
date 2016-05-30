from .constants import POS_METHODS, DEFAULT_POS_METHOD
from cltk.tag.pos import POSTag
from flask_restful import Resource, reqparse

"""
    GET     /core/pos                           View available POS tagging methods

    POST    /core/pos                           Return POS tags for the given string
            Data: {'string': string to tag,     using the specified langauge and
                   'lang':   language           tagging method.
                   'method': tagging method}
"""
class POSTagger(Resource):
    def get(self):
        return {'methods': POS_METHODS}

    def post(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('string', required=True)
        self.reqparse.add_argument('lang', required=True, choices=POS_METHODS.keys())
        self.reqparse.add_argument('method', required=False,
                                   default=DEFAULT_POS_METHOD)

        args = self.reqparse.parse_args()
        string = args['string']
        lang = args['lang']
        method = args['method']

        if method not in POS_METHODS[lang]:
            return {'message': {'method': method + ' is not a valid choice'}}

        tagger = POSTag(lang)
        tagged = []
        if method == 'unigram':
            tagged = tagger.tag_unigram(string)
        elif method == 'bigram':
            tagged = tagger.tag_bigram(string)
        elif method == 'trigram':
            tagged = tagger.tag_trigram(string)
        elif method == 'ngram123':
            tagged = tagger.tag_ngram_123_backoff(string)
        elif method == 'tnt':
            tagged = tagger.tag_tnt(string)

        return {'tags': [{'word': word, 'tag': tag}
                         if tag is not None else {'word': word, 'tag': 'None'}
                         for word, tag in tagged]}
