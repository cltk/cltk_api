"""Import commentary from OCR texts"""

import optparse
import re
from cltk_api.util.db import mongo

class CommentaryIngestOCR:

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

			for line in f:

				# If the line starts a new comment, process old comment, start new
				if self._starts_new_comment( line ):
					# If length to old comment, write old comment, start new comment
					if len(comment) > 0:
						self._save_comment( comment )

					comment = line

				# Otherwise, keep adding the comment to itself
				else:
					comment = comment + line

			# Write the final comment
			if len(comment) > 0:
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

		comment, ref = self._get_comment_ref( comment )
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

	def _starts_new_comment(self, line):
		# If line starts with 1-4 digits followed by a single .
		return re.match("^\d{1,4}", line)

	def _get_comment_ref(self, comment):
		ref = {
			'text' : '',
			'lines' : []
		}

		if comment.startswith("\ufeff1. intro"):
			ref['text'] = "Introduction"
			ref['lines'] = [1]
			comment = comment.lstrip("\ufeff1. intro.").strip()

		elif comment.startswith("1. intro"):
			ref['text'] = "Introduction"
			ref['lines'] = [1]
			comment = comment.lstrip("1. intro.").strip()

		elif comment.startswith("1. book"):
			ref['text'] = "About the Book"
			ref['lines'] = [1]
			comment = comment.lstrip("1. book.").strip()

		else:
			# Get the ref from the start of the comment
			match = re.match("^\d{1,4}", comment)
			target_s = comment[ match.start(): match.end() ]

			# if target is a range
			next_char = comment[ match.end() ]
			if next_char in [ "-", "–", "—" ]:

				# Remove the first range value
				comment = re.sub("^\d{1,4}", "", comment)
				comment = comment.lstrip("-–—")

				# Extract and remove the second range.value
				match = re.match("^\d{1,4}", comment)
				target_t = comment[ match.start(): match.end() ]
				comment = re.sub("^[a-z0-9]{1,4}\.", "", comment)

				# Try to get ints from the extracted refs
				ref_int_s = self._try_parse_int( target_s )
				ref_int_t = self._try_parse_int( target_t )

				# Set the ref text with the targets (even if they aren't ints)
				ref['text'] = target_s + "-" + target_t

				# Set the line range if the second range is an int,
				if ref_int_t:
					ref['lines'] = [ x for x in range( ref_int_s, ref_int_t + 1 )]

				# otherwise just set the single line as the range
				elif ref_int_s:
					ref['lines'] = [ ref_int_s ]

			else:
				comment = re.sub("^\d{1,4}\.", "", comment)

				# Set the ref target text
				ref['text'] = target_s

				# Set the ref target range
				ref_int_s = self._try_parse_int( target_s )
				if ref_int_s:
					ref['lines'] = [ ref_int_s ]


		return comment, ref

	def _process_comment(self, comment):
		comment = comment.strip()

		# <br>'s for \n's
		comment = re.sub("\n", "<br>", comment)

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
