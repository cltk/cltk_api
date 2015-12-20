"""Import commentary from TEI texts"""


import optparse
import pymongo
import re
from bs4 import BeautifulSoup, Tag
from cltk_api.util.db import mongo

class CommentaryIngestXML:

	def __init__(self, settings):

		self.db = mongo(settings.dbname)
		self.fname = settings.fname

		self.work = settings.work
		self.subwork = int( settings.subwork )
		self.author = settings.author
		self.source = settings.source

		if settings.do_reset:
			self.reset_db()

		self.ingest()

		return

	def ingest(self):
		comment = ''

		with open(self.fname, 'r') as f:
			data = f.read()
			soup = BeautifulSoup( data )
			for comment in soup.select("div2"):

				self._save_comment( comment )

		return

	def _save_comment(self, comment):

		# Should look like this:
		# 	commentary :	[	{
		#	source : "Gow",
		#	work : "Georgics",
		#	book : "I",
		#	ref : "1-3",
		#	comment : "Nam cum et nostrae rei publicae detrimenta considero et maximarum civitatum veteres animo calamitates colligo, non minimam video per disertissimos homines invectam partem incommodorum; cum autem res ab nostra memoria propter vetustatem remotas ex litterarum monumentis repetere instituo, multas urbes constitutas, plurima bella restincta, firmissimas societates, sanctissimas amicitias intellego cum animi ratione tum facilius eloquentia comparatas."
		#	} ]

		ref = self._get_comment_ref( comment )
		comment = self._process_comment( comment )

		query = {
			'work' : self.work,
			'subwork.n' : self.subwork
		}

		obj = {
			'source' : self.source,
			'ref' : ref['text'],
			'comment' : comment
		}

		for line_n in ref['lines']:
			query['line.n'] = line_n
			print(line_n, obj)
			self.db.lines.update( query, {'$addToSet': {"commentary" : obj } } )

		return


	def _get_comment_ref(self, comment):
		"""
		For a comment applying to lines 1, 2, and 3
		Ref text is 1-3
		Ref lines is [1,2,3]
		"""
		ref = {
			'text' : '',
			'lines' : []
		}

		ref['text'] = comment.attrs['n']
		if self._try_parse_int( ref['text'] ):
			ref['lines'] = [ int( comment.attrs['n'] ) ]
		elif ref['text'] == "intro":
			ref['text'] = "Introduction"
			ref['lines'] = [1]

		else:

			l_n_range = ref['text'].split("-")
			if len( l_n_range ) > 1 and self._try_parse_int( l_n_range[0] ) and self._try_parse_int( l_n_range[1] ):
				ref['lines'] = [ x for x in range( int( l_n_range[0] ), int( l_n_range[1] ) ) ]

			elif len( l_n_range ) > 0 and self._try_parse_int( l_n_range[0] ):
				ref['lines'] = [ int( l_n_range[0] ) ]

			else:
				# No lines were added, no comment will be inserted
				l_n_range = ref['text'].split(",")
				for x in l_n_range:
					x = x.strip()
				if len( l_n_range ) > 1 and self._try_parse_int( l_n_range[0] ) and self._try_parse_int( l_n_range[1] ):
					ref['lines'] = [ x for x in range( int( l_n_range[0] ), int( l_n_range[1] ) ) ]

				elif len( l_n_range ) > 0 and self._try_parse_int( l_n_range[0] ):
					ref['lines'] = [ int( l_n_range[0] ) ]



		return ref

	def _process_comment(self, comment):
		"""
		Comment enters as a bs4 Tag and returns as a string

		"""
		comment_string = comment.__str__()

		#quote
		comment_string = re.sub('<quote>', '<span class="quote">', comment_string)
		comment_string = re.sub('</quote>', '</span>', comment_string)

		#line
		comment_string = re.sub('<l>', '<span class="in-comment-line">', comment_string)
		comment_string = re.sub('<l>', '</span>', comment_string)

		comment_soup = BeautifulSoup( comment_string )
		comment = ""
		VALID_TAGS = ["div2", "span"]
		for tag in comment_soup.findAll(True):
			if tag.name not in VALID_TAGS:
				tag.hidden = True
		comment = comment_soup.renderContents().decode("utf-8")

		# <br>'s for \n's
		comment = re.sub("\n", " ", comment)
		comment = re.sub("  ", " ", comment)
		comment = re.sub("<div2[^<]+?>", "", comment)
		comment = re.sub("</div2>", "", comment)
		comment = comment.strip()

		return comment

	def _try_parse_int(self, s, val=None):

		try:
			return int(s)
		except ValueError:
			return val

	def reset_db(self):

		for line in self.db.lines.find():
			self.db.lines.update({
					'_id' : line['_id']
				},{
					'$set' : {
						'commentary' : []
					}
				})

		return
