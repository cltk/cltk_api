import re
import string
import sys

class ScansionToHTML:

	def __init__(self, line, scansion):

		self.scansion = scansion
		self.html_line = ""
		self.line_orig = line
		self.line = line
		self.scansion_to_html()

		return

	def scansion_to_html(self):

		while len( self.scansion ) > 0:
			foot = self.scansion[0]
			while len( foot ) > 0:
				syll = foot[0]

				if self.line.lower().startswith( syll['s'] ):
					len_syll_s = len( syll['s'] )

					if syll['l']:
						#long
						self.html_line += "<span class='scansion-syllable syllable-long'>" + self.line[0:len_syll_s] + "</span>"

					else:
						#short
						self.html_line += "<span class='scansion-syllable syllable-short'>" + self.line[0:len_syll_s] + "</span>"

					self.line = self.line[len_syll_s:]

					# finally remove the syll
					foot.remove( syll )


				else:
					# skip one forward (spaces, punct, &c.)
					if len(self.line) > 0:
						self.html_line += self.line[0]
						self.line = self.line[1:]
					else:
						foot = []
						self.scansion = []
						print(" -- error with transfering to html for", self.line_orig, self.html_line)
						break

			# If there's more scansion
			if len(self.scansion):
				# Remove the empty foot
				self.scansion.remove(foot)

				# If scansion length is now no more
				if len(self.scansion) == 0:
					# add the remainder of line (final punctuation!!)
					self.html_line += self.line


		return

	def scansion_for_tei(self):

		return

def main():
	parser = optparse.OptionParser()
	parser.add_option("--do_reset", dest="do_reset", help="", default=False)
	parser.add_option("-d", "--dbname", dest="dbname", help="", default=False)
	parser.add_option("-f", "--fname", dest="fname", help="", default=False)
	parser.add_option("-w", "--work", dest="work", help="", default=False)
	parser.add_option("-s", "--subwork", dest="subwork", help="", default=False)
	parser.add_option("-a", "--author", dest="author", help="", default=False)
	parser.add_option("-r", "--source", dest="source", help="", default=False)
	(options, args) = parser.parse_args()

	CommentaryIngest(options)

	return


if __name__ == "__main__":
	main()
