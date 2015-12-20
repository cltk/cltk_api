"""

Map original lines to the translations based on the translation associations from MapTranslation

"""

import optparse
import pymongo
import re
import string
import numpy as np
from cltk_api.util.db import mongo

class MapOriginal:

	def __init__(self, settings):


		self.dbname = "segetes_dev"


		self.map_orig()

		return

	def map_orig(self):


		self.db = mongo( self.dbname )

		for line in self.db.lines.find():

			trans_list = []

			translations = self.db.translations.find({
					'work' : line['work'],
					'subwork.n' : line['subwork']['n'],
					'orig_l_ns' : line['line']['n']
				})

			for trans in translations:

				is_in_trans_list = False
				for t in trans_list:
					if trans['edition']['slug'] == t['edition']['slug']:
						is_in_trans_list = True
						t['l_ns'].append( trans['line']['n'] )

				if not is_in_trans_list:
					trans_list.append({
							'edition' : {
									'slug' : trans['edition']['slug']
								},
							'l_ns' : [
									trans['line']['n']
								]
						})

			self._save_trans_map( line, trans_list )

		return

	def _save_trans_map( self, line, trans_list ):

		query = {
				'work' : line['work'],
				'subwork.n' : line['subwork']['n'],
				'line.n' : line['line']['n']
			}

		print(" -- Line", line['line']['n'] )

		self.db.lines.update(query, {'$set' : { 'translations' :trans_list } })

		return
