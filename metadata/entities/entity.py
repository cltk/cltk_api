import string
import os
import json
import re
import random
from time import sleep
from urllib.request import urlopen, urlretrieve
from urllib import error
from bs4 import BeautifulSoup
from open_words.get_stems import get_stems
from cltk_api.util.db import mongo


class Entity:

	def __init__(self, db_name, en_name, l_names):

		self.en_name = en_name.lower()
		self.l_names = l_names.lower().split(",")
		self.db = mongo( db_name )
		self.id = self.upsert_entity()
		self.punctuation_transtable = {ord(c): None for c in string.punctuation}


		return

	def upsert_entity(self):
		print(" -- Upserting entity for", self.en_name, "-", self.l_names)
		res =  self.db.entities.update({
				'en_name' : self.en_name,
				'l_names' : self.l_names
			},{
				"$set":{
					'en_name' : self.en_name,
					'l_names' : self.l_names,
					#'thumbnail' : '',
					#'desc' : '',
					#'link' : '',
					#'images' : [],
					#'lines' : [],
					#'events' : []
				}
			}, upsert=True)

		try:
			return res['upserted']
		except:
			eid = False
			en = [ x for x in self.db.entities.find({
				'en_name' : self.en_name,
				'l_names' : self.l_names
			})]
			if len( en ) > 0:
				eid = en[0]['_id']
			return eid

	def fetch_wikipedia(self):


		def _to_wikiq(name):
			new_name = ''
			name = name.split(" ")
			for w in name:
				new_name = new_name + w.capitalize() + " "
			new_name = new_name.strip()
			return new_name.replace(" ","_")

		def _get_desc(doc):
			desc = ""
			ps = doc.select("#bodyContent p")
			if len( ps ):
				desc = ps[0].text

			return desc

		def _is_disam_page(doc):
			# if the first p of #bodyContent doesn't contain "may refer to"
			if len( desc ) and "may refer to" in desc:
					return True
			else:
				return False


		error_str = "Wikipedia does not have an article with this exact name."
		url = "http://en.wikipedia.org/wiki/"
		extra_ending = "_(mythology)"

		self.link = url + _to_wikiq( self.en_name )
		print(" -- -- Querying", self.link )

		try:
			resp = urlopen( self.link )
			doc = BeautifulSoup(resp)
			text = doc.text
			desc = _get_desc( doc )

		except  error.HTTPError as e:
			print(" -- -- Got error", e.reason)
			text = ''
			desc = ''


		# There wasn't a page with the english name, try alternative names
		if not len( text ) or ( error_str in text ) or _is_disam_page( desc ):
			still_not_found = True

			# query with all latin names
			for l_name in self.l_names:

				# wait before making next query
				self.link = url + _to_wikiq( l_name )
				print(" -- -- Querying", self.link )
				sleep( random.randint( 2, 5 ) )

				try:
					resp = urlopen( self.link )
					doc = BeautifulSoup(resp)
					text = doc.text
					desc = _get_desc( doc )

				except error.HTTPError as e:
					print(" -- -- Got error", e.reason)
					text = ''
					desc = ''

				if len( text ) and (not error_str in text) and not _is_disam_page( desc ):
					# found a page!
					still_not_found = False
					break


			# If still not found, try with the _mythology extra ending
			if still_not_found:

				self.link = url + _to_wikiq( self.en_name ) + extra_ending
				print(" -- -- Querying", self.link )
				sleep( random.randint( 2, 5 ) )
				try:
					resp = urlopen( self.link )
					doc = BeautifulSoup(resp)
					text = doc.text
					desc = _get_desc( doc )

				except  error.HTTPError as e:
					print(" -- -- Got error", e.reason)
					text = ''
					desc = ''

				if len( text ) and (not error_str in text) and not _is_disam_page( desc ):
					# found a page!
					still_not_found = False



			# If really still not found, print error and return.
			if still_not_found:
				print(" -- Error with querying Wikipedia (no article?)")
				return


		# If we have a doc, parse it and extract necessary data
		self._parse_wiki_data( doc, desc )

		return

	def comp_lines(self):

		print(" -- comparing entity stems against all lines")
		self.n_lines = self.db.lines.count()

		for l_name in self.l_names:
			for l_n in l_name.split(" "):
				stems = [stem.lower() for stem in get_stems( l_n ) if len(stem)]
				n_m = 0
				line_ids = []

				for i, line in enumerate( self.db.lines.find() ):

					word_update_happened = False
					comp_line = line['line']['text'].translate(self.punctuation_transtable).split(" ")
					comp_words = [word for word in comp_line if len(word) and word[0].isupper()]

					for word in comp_words:
						# stem each upper word in the line
						# see if any stems in the line match the word stems

						word_stems = [stem.lower() for stem in get_stems( word ) if len(stem)]

						match = any(s in word_stems for s in stems)
						if match:
							n_m += 1
							line_ids.append( line['_id'] )


					if i % 1000 == 0:
						print(' -- -- -- @', i, '-', i+1000, 'of', self.n_lines)

		self.db.entities.update({
				'_id' : self.id
			},{
				'$set' : {
					'lines' : line_ids
				}
			})

		return

	def _parse_wiki_data(self, doc, desc):

		self.desc = desc
		self.image_path = "./data/images/"
		self.thumb_path = "/img/"

		# images in the body content
		imgs = doc.select("#bodyContent img")
		if len( imgs ):
			thumbnail_img = imgs[0]

			# Make this:
			#   http://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Aeneas%27_Flight_from_Troy_by_Federico_Barocci.jpg/280px-Aeneas%27_Flight_from_Troy_by_Federico_Barocci.jpg
			# Look like this:
			#   http://upload.wikimedia.org/wikipedia/commons/f/f7/Aeneas%27_Flight_from_Troy_by_Federico_Barocci.jpg
			thumb_src = thumbnail_img.attrs['src']

			if (
					thumb_src == "//upload.wikimedia.org/wikipedia/en/thumb/9/99/Question_book-new.svg/50px-Question_book-new.svg.png"
				or thumb_src == "//upload.wikimedia.org/wikipedia/en/thumb/6/62/PD-icon.svg/12px-PD-icon.svg.png"
				or thumb_src == "//upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Text_document_with_red_question_mark.svg/40px-Text_document_with_red_question_mark.svg.png"
				or thumb_src == "//upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Padlock-silver.svg/20px-Padlock-silver.svg.png"
				):
				if len( imgs ) > 1:
					thumbnail_img = imgs[1]
					thumb_src = thumbnail_img.attrs['src']

					if thumb_src.startswith( "//en.wikipedia.org/wiki/Special:CentralAutoLogin" ):
						print(" -- -- no thumbnail", thumb_src)
						return

				else:
					print(" -- -- no thumbnail", thumb_src)
					return

			thumb_src = thumb_src.replace("/thumb/", "/")
			thumb_uri_list = thumb_src.split("/")
			thumb_src = thumb_src.replace( "/" + thumb_uri_list[-1], "")
			thumb_ext = thumb_uri_list[-2].split(".")[-1]
			thumb_new_fname = "entity_" + self.en_name.replace(" ", "_") + "." + thumb_ext

			sleep( random.randint( 2, 5 ) )
			print(" -- -- retreiving thumbnail", thumb_src)

			try:
				urlretrieve( "http:" + thumb_src, self.image_path + thumb_new_fname )
				self.thumbnail = self.thumb_path + thumb_new_fname

			except error.HTTPError as e:
				print(" -- -- Error retrieving thumbnail")
				print(e.reason)
				self.thumbnail = ''


		else:
			print(" -- -- no thumbnail", thumb_src)


		return


	def save_entity(self):

		print(" -- -- Updating entity", self.en_name)

		if not hasattr(self, "thumbnail"):
			self.thumbnail = ""

		if not hasattr(self, "desc"):
			self.desc = ""

		res =  self.db.entities.update({
				'_id' : self.id
			},{
				'$set' : {
					'thumbnail' : self.thumbnail,
					'desc' : self.desc,
					'link' : self.link,
					#'images' : [],
					#'lines' : [],
					#'events' : []
				}
			}, upsert=True)



		return

	def add_work_data(self):


		return
