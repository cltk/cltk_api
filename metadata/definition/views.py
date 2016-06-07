from flask_restful import Resource
import json
import os

# File name suffix for the json files
DATA_FILE_SUFFFIX = "-analyses.json"

def get_cltk_treebank_dir(lang, corpus='perseus'):
    """Take relative filepath, return absolute"""
    cltk_home = os.path.expanduser('~/cltk_data')
    treebank_path =  lang.casefold() + '_treebank_' + corpus;
    treebank_dir = os.path.join(cltk_home, lang.casefold(), 'treebank', treebank_path, treebank_path)
    return treebank_dir

class Definition(Resource):

	'''
	GET 	/lang/<string:lang>/define/<string:word>
			Return the available definitions for a word of given language
	'''
	def get(self, lang, word):
		# File name would something like "latin-analyses.json"
		filename = lang + DATA_FILE_SUFFFIX
		_dir = get_cltk_treebank_dir(lang)
		file = os.path.join(_dir, filename)
		with open(file, "r") as infile:
			word_list = json.load(infile)
		try:
			return word_list[word]
		except KeyError as e:
			return []
