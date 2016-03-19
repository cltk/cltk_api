"""
For a given input string and scansion value, return a line of HTML with
<span>s around syllables and syllable-long and syllable-short classes
"""

import re
import string
import sys

class ScansionToHTML:

	def __init__(self, line, scansion):
		"""

		"""

		return

	def scansion_to_html(self, line, scansion):
		"""
		For a given input string and scansion, generate an HTML response of syllables wrapped in
		<span> elements with classes denoting long and short syllables.
        :param line: str
        :param scansion: Line scansion (needs to be reworked to be like the CLTK scansion)
		:return html_line: str (formatted HTML string)
		"""

		while len( self.scansion ) > 0:
			foot = self.scansion[0]
			while len( foot ) > 0:
				syll = foot[0]

				if self.line.lower().startswith( syll['s'] ):
					len_syll_s = len( syll['s'] )

					if syll['l']:
						#long
						html_line += "<span class='scansion-syllable syllable-long'>" + self.line[0:len_syll_s] + "</span>"

					else:
						#short
						html_line += "<span class='scansion-syllable syllable-short'>" + self.line[0:len_syll_s] + "</span>"

					self.line = self.line[len_syll_s:]

					# finally remove the syll
					foot.remove( syll )


				else:
					# skip one forward (spaces, punct, &c.)
					if len(self.line) > 0:
						html_line += self.line[0]
						self.line = self.line[1:]
					else:
						foot = []
						self.scansion = []
						print(" -- error with transfering to html for", self.line_orig, html_line)
						break

			# If there's more scansion
			if len(self.scansion):
				# Remove the empty foot
				self.scansion.remove(foot)

				# If scansion length is now no more
				if len(self.scansion) == 0:
					# add the remainder of line (final punctuation!!)
					html_line += self.line


		return html_line
