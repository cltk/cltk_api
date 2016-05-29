from flask_restful import Resource
import json
import os

class Definition(Resource):

	# Directory where the definitions json file will be present
	BASE_DIR = ""
	# File name suffix for the json files
	DATA_FILE_SUFFFIX = "-analyses.json"

	'''
	GET 	/lang/<string:lang>/define/<string:word>
			Return the available definitions for a word of given language
	'''
	def get(self, lang, word):
		# File name would something like "latin-analyses.json"
		filename = lang + self.DATA_FILE_SUFFFIX
		file = os.path.join(self.BASE_DIR, filename)
		with open(file, "r") as infile:
			word_list = json.load(infile)
		try:
			return word_list[word]
		except KeyError as e:
			return "No definitions available"
