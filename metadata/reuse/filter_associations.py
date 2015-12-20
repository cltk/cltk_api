"""Filter and import associations based on input threshold"""
import optparse
import pdb
import pymongo
from cltk_api.util.db import mongo

class FilterAssociations:


	def __init__(self, settings):


		# db with comparisons
		self.source_dbname = settings.source_dbname
		self.source_db = mongo(self.source_dbname)

		# db with lines to save in "Related Passages"
		self.target_dbname = settings.target_dbname
		self.target_db = mongo(self.target_dbname)

		# Threshold for filter
		self.prob_thresh = int( settings.prob_thresh )


		# If we need to reset the related passages
		if settings.do_reset:
			self.reset_related_passages()

		# start migration
		self.migrate_associations()

		return


	def migrate_associations(self):

		# proceed 1000 at a time to check / migrate associations
		total_comparisons = self.source_db.comparisons.count()

		for index, comparison in enumerate( self.source_db.comparisons.find() ):
			#for index, comparison in range(0, total_comparisons):
			if index % 1000 == 0:
				print(' -- -- -- @', index, '-', index+1000, 'of', total_comparisons)

			#for comparison in self.comparisons:
			if comparison['prob'] >= self.prob_thresh:
				self.save_comparison( comparison )

		return

	def save_comparison(self, comparison):


		# Needs to look like this
		# related_passages: [
		#		{
		#			lemma : ["dique deaeque omnes, quibus est tutela per agros,"],
		#			author : "Propertius",
		#			work : "Elegies",
		#			book : "IV",
		#			poem : "8",
		#			lines : "37"
		#		}
		#	]

		# Query for finding the source line in the target_db
		query = {
			'work' : comparison['line']['work'],
			'subwork.n' :  comparison['line']['subwork']['n'],
			'line.n' : comparison['line']['line']['n']
		}

		# Related passage metadata to add
		passage = {
					'lemma' : [ comparison['text']['chunk']['text'] ],
					'author' : comparison['text']['author'],
					'work' : comparison['text']['title'].replace("Machine readable text", ""),
					'book' : "",
					'lines' : "",
					'alpha' : comparison['prob']
				}

		self.target_db.lines.update(query, {'$addToSet' : { 'related_passages' : passage } })

		return

	def reset_related_passages(self):

		self.target_db.lines.update({},{
				'$set' : { 'related_passages' : [] }
			}, multi=True)

		return
