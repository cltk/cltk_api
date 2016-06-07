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
            corpus_importer.import_corpus('latin_models_cltk')
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

    def test_core_stem(self):
        response = self.app.get('/core/stem/Est interdum praestare mercaturis rem quaerere, nisi tam periculosum sit, et item foenerari, si tam honestum. Maiores nostri sic habuerunt et ita in legibus posiuerunt: furem dupli condemnari, foeneratorem quadrupli. Quanto peiorem ciuem existimarint foeneratorem quam furem, hinc licet existimare. Et uirum bonum quom laudabant, ita laudabant: bonum agricolam bonumque colonum; amplissime laudari existimabatur qui ita laudabatur. Mercatorem autem strenuum studiosumque rei quaerendae existimo, uerum, ut supra dixi, periculosum et calamitosum. At ex agricolis et uiri fortissimi et milites strenuissimi gignuntur, maximeque pius quaestus stabilissimusque consequitur minimeque inuidiosus, minimeque male cogitantes sunt qui in eo studio occupati sunt. Nunc, ut ad rem redeam, quod promisi institutum principium hoc erit.')
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(eval(response.data)['stemmed_output'], 'est interd praestar mercatur r quaerere, nisi tam periculos sit, et it foenerari, si tam honestum. maior nostr sic habueru et ita in leg posiuerunt: fur dupl condemnari, foenerator quadrupli. quant peior ciu existimari foenerator quam furem, hinc lice existimare. et uir bon quo laudabant, ita laudabant: bon agricol bon colonum; amplissim laudar existimaba qui ita laudabatur. mercator autem strenu studios re quaerend existimo, uerum, ut supr dixi, periculos et calamitosum. at ex agricol et uir fortissim et milit strenuissim gignuntur, maxim p quaest stabilissim consequi minim inuidiosus, minim mal cogitant su qui in e studi occupat sunt. nunc, ut ad r redeam, quod promis institut principi hoc erit. ')

    def test_definition_api(self):
        response = self.app.get('lang/latin/define/abante')
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(eval(response.data)[0]['headword'], 'Abas')
        self.assertEqual(eval(response.data)[0]['definition'], 'The twelfth king of Argos, son of Lynceus and Hypermnestra')
        self.assertEqual(eval(response.data)[0]['pos'], 'noun sg masc abl')

if __name__ == '__main__':
    unittest.main()
