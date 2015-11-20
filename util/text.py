"""
Sundry utility functions for sanitizing textual data
"""
import re
import unicodedata as ud

class TextUtil:

	def is_latin(self, uchr):
		try: return self.latin_letters[uchr]
		except KeyError:
			return self.latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))

	def only_roman_chars(self, unistr):
		return all(self.is_latin(uchr)
			for uchr in unistr
			if uchr.isalpha())

	def only_iso88591(self, string):
		flag = True
		try:
			string.encode("iso-8859-1")
		except UnicodeEncodeError:
			flag = False

		return flag



