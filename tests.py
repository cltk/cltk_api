import os
import unittest
import api_json
import json
from cltk.corpus.utils.importer import CorpusImporter
from metadata.pos.constants import POS_METHODS

class TestAPIMethods(unittest.TestCase):
    """Requires latin_text_perseus folder in ~/cltk_data/latin/text/latin_text_perseus"""

    def setUp(self):
        file_rel = os.path.join('~/cltk_data/latin/text/latin_text_perseus/README.md')
        file = os.path.expanduser(file_rel)
        if not os.path.isfile(file):
            corpus_importer = CorpusImporter('latin')
            corpus_importer.import_corpus('latin_text_perseus')
            file_exists = os.path.isfile(file)
            self.assertTrue(file_exists)

        self.app = api_json.app.test_client()
        self.headers = [('Content-Type', 'application/json')]

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status, '404 NOT FOUND')

    def test_hello_api(self):
        response = self.app.get('/hello')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data), dict(hello='world'))

    def test_todo_api(self):
        response = self.app.get('/todo/cltk_testing')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data), {'example with token': 'cltk_testing'})

    def test_lang_api(self):
        response = self.app.get('/lang')
        self.assertEqual(response.status, '200 OK')
        response_lang = eval(response.data)['languages']
        self.assertTrue('latin' in response_lang)

    def test_corpus_api(self):
        response = self.app.get('/lang/latin/corpus')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data)['language'], 'latin')
        self.assertTrue('perseus' in eval(response.data)['corpora'])

    def test_author_api(self):
        response = self.app.get('/lang/latin/corpus/perseus/author')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data)['language'], 'latin')
        self.assertTrue('glass' in eval(response.data)['authors'])

    def test_texts_api(self):
        response = self.app.get('/lang/latin/corpus/perseus/author/glass/text')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data)['language'], 'latin')
        self.assertEqual(eval(response.data)['corpus'], 'perseus')
        self.assertEqual(eval(response.data)['author'], 'glass')
        self.assertTrue('washingtonii_vita' in eval(response.data)['texts'])

    def test_text_api(self):
        response = self.app.get('/lang/latin/corpus/perseus/author/tacitus/text/germania')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data)['language'], 'latin')
        self.assertEqual(eval(response.data)['corpus'], 'perseus')
        self.assertEqual(eval(response.data)['author'], 'tacitus')
        self.assertEqual(eval(response.data)['meta'], 'book-chapter')
        self.assertEqual(eval(response.data)['work'], 'germania')
        self.assertEqual(eval(response.data)['text']['2']['1'].strip(), 'Ipsos Germanos indigenas crediderim minimeque aliarum gentium adventibus et hospitiis mixtos, quia nec terra olim sed classibus advehebantur qui mutare sedes quaerebant, et immensus ultra utque sic dixerim adversus Oceanus raris ab orbe nostro navibus aditur.')

        response_chunk1 = self.app.get('/lang/latin/corpus/perseus/author/tacitus/text/germania?chunk1=2')
        self.assertEqual(response_chunk1.status, '200 OK')
        self.assertEqual(eval(response_chunk1.data)['text']['2'].strip(), 'quis porro, praeter periculum horridi et ignoti maris, Asia aut Africa aut Italia relicta Germaniam peteret, informem terris, asperam caelo, tristem cultu aspectuque nisi si patria sit?')

        response_chunk2 = self.app.get('/lang/latin/corpus/perseus/author/tacitus/text/germania?chunk1=2&chunk2=4')
        self.assertEqual(response_chunk2.status, '200 OK')
        self.assertEqual(eval(response_chunk2.data)['text'].strip(), 'quidam, ut in licentia vetustatis, plures deo ortos pluresque gentis appellationes, Marsos Gambrivios Suebos Vandilios adfirmant, eaque vera et antiqua nomina.')

        response_chunk3 = self.app.get('/lang/latin/corpus/perseus/author/tacitus/text/germania?chunk1=2&chunk2=4&chunk3=1')
        self.assertEqual(response_chunk3.status, '500 INTERNAL SERVER ERROR')

    def test_pos_latin_ngram123(self):
        # test GET response
        response = self.app.get('/core/pos')
        expected_response = {'methods': POS_METHODS}
        self.assertEqual(eval(response.data), expected_response)

        # test POST response
        data = json.dumps({'string': 'Gallia est omnis divisa in partes tres',
                           'lang': 'latin',
                           'method': 'ngram123'})
        response = self.app.post('/core/pos', data=data, headers=self.headers)
        expected_response = {u'tags': [{'word': 'Gallia', 'tag': 'None'},
                                       {'word': 'est', 'tag': 'V3SPIA---'},
                                       {'word': 'omnis', 'tag': 'A-S---MN-'},
                                       {'word': 'divisa', 'tag': 'T-PRPPNN-'},
                                       {'word': 'in', 'tag': 'R--------'},
                                       {'word': 'partes', 'tag': 'N-P---FA-'},
                                       {'word': 'tres', 'tag': 'M--------'}]}
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data), expected_response)

if __name__ == '__main__':
    unittest.main()
