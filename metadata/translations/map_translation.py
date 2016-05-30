"""

Map a translation of a Latin document to the original Latin document

Must already have definitions ingested for this to work

"""


import optparse
import pymongo
import re
import copy
import string
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


class MapTranslation:

	def __init__(self, settings):


		# What data to import and where to put it
		self.trans_fname = settings.fname
		self.work = settings.work
		self.subwork = { 'n' : int( settings.subwork ) }
		self.translators = [ settings.author ]
		self.edition_slug = settings.author

		# Get the length of the original work
		self.len_orig = 0

		# Get the length of the translation
		self.len_trans = 0

		# Threshold settings for association
		self.r = 5 # range to search in lines before/after
		self.si_thresh = 0.0 # must have a higher similarity index than this to save

		# Helps
		self.punctuation_transtable = {ord(c): " " for c in string.punctuation}
		self.stops = stopwords.words("english")
		self.lmtzr = WordNetLemmatizer()

		# Load translation and map
		self.load_trans()
		self.map_trans()

		return



	def load_trans(self):

		self.translation = []

		with open( self.trans_fname, "r" ) as f:

			trans = f.readlines()

			for i, line in enumerate( trans ):
				if len( line ):
					self.translation.append( line.strip() )

			self.len_trans = len( self.translation )

		return


	def map_trans(self):

		# calculate the ratio of the length of the original to the translation
		self.ratio = self.len_orig / self.len_trans

		for i, text_unit in enumerate( self.translation ):

			# nix 'd
			text_unit_orig = text_unit
			text_unit = text_unit.replace("'d", "")

			# strip punctuation
			text_unit = text_unit.translate(self.punctuation_transtable).lower()
			text_unit = text_unit.replace("—", " ")

			# split at words
			words = text_unit.split(" ")

			# lemmas
			lemmas = []
			for word in words:
				if len(word):
					word = self.lmtzr.lemmatize(word)

					if word not in self.stops:
						lemmas.append(word)

			# syns
			syns = []
			for lemma in lemmas:
				synsets = wn.synsets(lemma)

				word_syns = []
				for syn in synsets:
					word_syns = word_syns + syn.lemma_names()

				syns = syns + word_syns

			syns = dedupe_list( syns )
			self._map_unit( i, syns, text_unit_orig )



		return

	def _map_unit( self, i, syns, text_unit_orig ):


		target_n = self.ratio * i
		l_n_min = np.floor( target_n - self.r )
		l_n_max = np.ceil( target_n + self.r )

		# This is where we need to load lines from the original work
		lines = []

		line_ms = []
		for line in lines:

			line_senses = []
			line_defs_lemmas = []
			line_defs_syns = []
			m = 0

			# Flatten the line definition senses
			for word in line['definitions']:
				for definition in word['defs']:
					line_senses = line_senses + definition['senses']

			# Build list of lemmas from the word definitions
			for sense in line_senses:
				# nix 'd
				sense = sense.replace("'d", "")

				# strip punctuation
				sense = sense.translate(self.punctuation_transtable).lower()
				sense = sense.replace("—", " ")

				# split at words
				sense_words = sense.split(" ")

				# lemmatize and check stoplist
				for word in sense_words:
					if len(word):
						word = self.lmtzr.lemmatize(word)
						if word not in self.stops:
							line_defs_lemmas.append(word)
			# syns
			line_defs_lemmas = dedupe_list( line_defs_lemmas)
			for lemma in line_defs_lemmas:
				synsets = wn.synsets(lemma)
				word_syns = []
				for syn in synsets:
					word_syns = word_syns + syn.lemma_names()
				line_defs_syns = line_defs_syns + word_syns
			line_defs_syns = dedupe_list( line_defs_syns )

			# Compare the line definiton senses to our syn list
			for lem_syn in syns:
				for lem_def in line_defs_syns:
					if lem_syn == lem_def:
						m += 1

			# Adjust m for the total number of syns compared
			m_rel = m / ( len( syns ) + len( line_defs_syns ) )

			# Finally, add the comparison matching to the
			line_ms.append( [ m, m_rel ] )


		# Figure the min/max, rel * 100
		m_max = 0
		m_min = 100
		for m_ls in line_ms:
			m_ls[1] = m_ls[1] * 100
			m_rel = m_ls[1]

			if m_rel > m_max:
				m_max = m_ls[1]
			if m_rel < m_min:
				m_min = m_ls[1]

		# Scale m_rel and if above significance thresh, add to line nos
		trans_l_ns = []
		for m_i, m_ls in enumerate( line_ms ):
			# rel is scaled to min/max (20%)
			if ( m_max - m_min ) > 0:
				m_ls[1] = ( ( m_ls[1] - m_min ) / ( m_max - m_min ) ) * 0.20
			# Final adjust for bigger rels (80%)
			m_ls[1] = m_ls[1] + ( ( m_ls[0] / 100 ) * 0.80 )

			if m_ls[1] >= self.si_thresh:
				line_n = int( l_n_min + m_i )

				if( l_n_min < 0 ):
					line_n = int( l_n_min + m_i ) + self.r
				elif ( l_n_min > self.len_orig ):
					line_n = int( l_n_min + m_i )

				# Append for base-1 counting
				trans_l_ns.append( line_n + 1 )

		return trans_l_ns
