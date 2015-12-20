from cltk.util.syllabifier import Syllabifier
import string
import re

Patterns = {
		'dactylic_hexameter' : {
			'n_feet' : 6,
			'feet' : [[1,0,0],[1,1]],
			'pattern' :[
						[[1,0,0],[1,1]],
						[[1,0,0],[1,1]],
						[[1,0,0],[1,1]],
						[[1,0,0],[1,1]],
						[[1,0,0],[1,1]],
						[[1,1]]
					]
		},
		'elegiac_pentameter' : {
			'n_feet' : 5,
			'feet' : [[1,0,0],[1,1]],
			'pattern' :[
						[[1,0,0],[1,1]],
						[[1,0,0],[1,1]],
						[[1]],
						[[1,0,0]],
						[[1,0,0]],
						[[1]]
					]
		}

	}

Latin = {

		'diphthongs' : ["ae", "au", "ei", "eu", "oe"],
		'two_consonants' : ["x", "z"],
		'digraphs' : ["ch", "ph", "th", "qu", "gu", "su"],
		'mute_consonants_and_f' : ['b', 'c', 'd', 'g', 'p', 't', 'f'],
		'liquid_consonants' : ['l', 'r'],
		'vowels' : [
						'a', 'e', 'i', 'o', 'u',
						'á', 'é', 'í', 'ó', 'ú',
						'æ', 'œ',
						'ǽ',  # no accented œ in unicode?
						'y'   # y is treated as a vowel; not native to Latin but useful for words borrowed from Greek
					]

	}

class Scansion(object):
	"""Predict scansion for a line of classical Greek or Latin poetry"""

	def __init__(self, patterns=Patterns, language=Latin):

		self.patterns = patterns
		self.language = language
		self.punctuation_transtable = {ord(c): " " for c in string.punctuation}
		self.line = []

		return

	def scan(self, line, pattern="dactylic_hexameter"):
		"""Input a line of poetry and receive an array of booleans indicating open or closed syllables"""

		s = Syllabifier()
		line_sylls = []
		scansion = []
		# Strip any punctuation and lower
		line = line.translate(self.punctuation_transtable).lower()
		line = line.replace("—", " ")


		# Build list of line syllables
		line = line.split()
		for word in line:
			if len( word ):
				line_sylls.extend( s.syllabify( word ) )

		# Build scansion for syllables, based on pattern
		# If a syllable is not long, it is short
		sylls_len = len(line_sylls)
		for i, syll in enumerate(line_sylls):
			scansion.append({
					's' : syll,
					'l' : 0
				})

			if i < sylls_len - 1 and self._is_elided( syll, line_sylls[ i + 1 ], line ):
				scansion[i]['l'] = "-"
				#scansion[i]['r'] = "elided"
				continue

			elif self._long_by_nature( i, syll, line_sylls, line ):
				scansion[i]['l'] = 1
				#scansion[i]['r'] = "by nature"
				continue

			elif i < sylls_len - 1 and self._long_by_position( syll, line_sylls[ i + 1 ] ):
				scansion[i]['l'] = 1
				#scansion[i]['r'] = "by position"
				continue

		# For next step, remove elided syllables
		for syll in scansion:
			if syll['l'] == "-":
				scansion.remove(syll)

		# Compare scansion against selected pattern
		scansion = self._scan_against_pattern( pattern, scansion, line )

		return scansion

	def _scan_against_pattern(self, pattern, scansion, line, depth=0):
		"""Make judgements about feet regularized to pattern"""

		# Load permissible feet for scansion pattern
		feet = self.patterns[ pattern ]['feet']
		n_feet = self.patterns[ pattern ]['n_feet']
		ft_cos = self._find_feet_commonalities(feet)
		new_scansion = []

		if depth == 1:
			scansion = self._check_synizesis(scansion)

		# Make a copy of the input scansion
		prev_scansion = scansion[:]

		# Primary loop for checking scansion against pattern feet
		while len(scansion) > 0:
			match = False

			# First, check if a foot matches the start of syllable list
			for foot in feet:
				#foot.reverse()
				has_elided = 0
				sylls = scansion[:len(foot)]

				# If the syllable list starts with a foot
				if self._comp_syll_foot( sylls, foot ):

					# Add the syllables to the scansion foot
					#sylls.reverse()
					new_scansion.append(sylls)

					# And remove the syllables from the original scansion list
					for sy in sylls:
						scansion.remove(sy)

					match = True
					break

			# If we don't have a match from the feet in our allowed feet
			if not match:
				# Apply common rules among the feet to syllables at start of list
				for c in ft_cos:
					scansion[c['i']]['l'] = c['val']
					#scansion[c['i']]['r'] = "commonality between feet"

				# If short between two longs (and no iambic foot from earlier loop), make that short long
				if len(scansion) > 2:
					if scansion[0]['l'] == 1 and scansion[2]['l'] == 1:
						scansion[1]['l'] = 1
						#scansion[1]['r'] = "scansion context"
				# If long short at the end of the line (and no iambic foot), make that short long
				elif len(scansion) == 2:
					scansion[1]['l'] = 1
					#scansion[1]['r'] = "end of line"

				# Catch the remainder to prevent inf loop
				else:
					# Add the syllables to the scansion foot
					new_scansion.append(scansion)
					# And remove the syllables from the original scansion list
					scansion = []

		# If there's more feet in the new scansion than are allowed in the meter
		scan_len = len(new_scansion)
		new_scansion = {'scansion':new_scansion}
		if n_feet < scan_len:
			new_scansion['error'] = "too many"
			if depth == 0:
				new_scansion = self._scan_against_pattern(pattern, prev_scansion, line, depth + 1)

		elif n_feet > scan_len:
			new_scansion['error'] = "too few"
			if depth == 0:
				new_scansion = self._scan_against_pattern(pattern, prev_scansion, line, depth + 1)

		# Return the scansion with feet in the correct order
		#new_scansion.reverse()
		return new_scansion

	def _comp_syll_foot(self, sylls, pattern):
		"""Check if the possible pattern for the foot matches syllables"""
		match = []
		if len(sylls) == len(pattern):
			for p_index, value in enumerate(pattern):
				if value == sylls[ p_index ]['l']:
					match.append(True)
				else:
					match.append(False)

		if len(match):
			return all(item==True for item in match)
		else:
			return False

	def _find_feet_commonalities(self, scansion_feet):
		"""Find the commonalities between the feet: e.g. dactyl and spondee have commonality of long syllable in first position"""
		commonalities = []
		for i_foot, foot in enumerate(scansion_feet):
			for i, val in enumerate(foot):
				common = True

				for i_comp_foot, comp_foot in enumerate(scansion_feet):
					if i >= len(comp_foot) or comp_foot[i] != val:
						common = False

				if common == True:
					c = {'i':i, 'val':val}
					included = False
					for comp_c in commonalities:
						if c['i'] == comp_c['i'] and c['val'] == comp_c['val']:
							included = True
					if not included:
						commonalities.append({'i':i,'val':val})

		return commonalities

	def _is_elided(self, syll, next_syll, line):
		"""Is the syllable elided based its ending and the next syllable's beginning"""
		is_elided = False
		line_len = len(line)

		# Only check the syllables that are at word boundaries (not interior syllables)
		for i, word in enumerate(line):
			if word.endswith(syll):
				if 	(
						(
						# If the target syllable ends with 'm' or a vowel
							syll.endswith("m")
						or self._is_vowel( syll[-1] )
						)
					and
						(
						# And if the next word exists and it starts with the next syllable
							i < line_len - 1
						and line[i + 1].startswith( next_syll )
						)
					):

						# And next word starts with a vowel or 'h'
						if	(
								self._is_vowel( next_syll[0] )
							or next_syll[0] == "h"
							):

							# And if the next word starts with an i, and the i isn't a consonant
							if next_syll[0] == "i":
								if len( next_syll ) > 1 and not self._is_vowel( next_syll[1] ):
									is_elided = True
								elif len( next_syll ) == 1:
									is_elided = True

							else:
								is_elided = True

		return is_elided

	def _long_by_nature(self, i, syll, line_sylls, line):
		"""Is the syllable long by nature"""
		is_long = False
		# Long_ends could also contain o, i, and u
		long_ends = ["as","es","os"]
		syll = syll.lstrip("qu")

		# If it contains a diphthong
		for diphthong in self.language['diphthongs']:
			if diphthong in syll:
				is_long = True
				break

		if not is_long:
			line_len = len(line)
			line_sylls_len = len(line_sylls)

			# If it's a final o, i, u, as, es, or os
			for e in long_ends:
				if syll.endswith(e):

					# Except tibi / mihi
					# If it has a preceding syllable
					if i > 0:
						if syll == "hi" and line_sylls[ i - 1 ] == "mi":
							return is_long

						elif syll == "bi" and line_sylls[ i - 1 ] == "ti":
							return is_long

					# Ensure the syll is an end of a word
					for l_i, word in enumerate(line):
						if word.endswith(syll):

							# If there's a next word and next syllable
							if l_i < line_len - 1:
								# If there's a next syllable
								if i < line_sylls_len - 1:
									if word.endswith( syll ) and line[ l_i + 1 ].startswith( line_sylls[ i + 1 ] ):
										is_long = True

							# Else, if there's not another syllable after it in the line, mark as long
							else:
								if i == line_sylls_len - 1 and word.endswith( syll ):
									is_long = True

		return is_long

	def _long_by_position(self, syll, next_syll):
		"""Is the syllable long by position, with two or more consonants between its vowel and the next"""
		is_long = False

		if syll.endswith("x") or next_syll.startswith("x"):
			is_long = True

		else:
			syll_cvs = self._return_consonants_vowels( syll )
			next_syll_cvs = self._return_consonants_vowels( next_syll )
			if ( syll_cvs.lstrip("c").count("c") + next_syll_cvs.rstrip("c").count("c") ) >= 2:
				is_long = True

			#print(syll, syll_cvs, is_long)
			#print(next_syll, next_syll_cvs)

		return is_long

	def _return_consonants_vowels(self, input_string):
		"""Return a string of Cs and Vs for the consonants and vowels in the string"""
		cvs = ''


		for i, char in enumerate(input_string):
			has_prev_char = i > 0
			has_next_char = i < len(input_string) - 1

			# First check for vowels with the u and i exceptions
			if self._is_vowel(char) and char not in ["u", "i"]:
				cvs = cvs + "v"

			# If it's a 'u', it's a vowel unless preceded by a q, g, or s
			elif char == "u":
				if has_prev_char:
					if not (
							not has_next_char
						and input_string[ i - 1 ] in ["q","g","s"]
						):
						cvs = cvs + "v"
				else:
					cvs = cvs + "v"

			# Handle the i/y/j exception
			elif char == "i":
				if has_next_char and i == 0 and self._is_vowel( input_string[ i + 1 ]):
					cvs = cvs + "c"
				else:
					cvs = cvs + "v"

			# x and z are double consonants
			elif char in ["x","z"]:
				cvs = cvs + "cc"

			# ch, ph, th are single
			elif has_prev_char and char == "h" and input_string[ i - 1 ] in ["c","p","t"]:
				pass

			# mute followed by a liquid is single
			elif has_prev_char and self._is_liquid_consonant( char ) and self._is_mute_consonant_or_f( input_string[ i - 1 ] ):
				pass

			elif char == "h":
				pass

			# failing all of the above, it's a normal consonant
			else:
				cvs = cvs + "c"

		return cvs

	def _check_synizesis(self, scansion):
		new_scansion = []
		remove_next_syll = False
		for i, syll in enumerate(scansion):

			len_scansion = len(scansion)
			has_next_syll = i < len_scansion - 1
			has_prev_syll = i > 0

			if remove_next_syll:
				remove_next_syll = False
				continue

			if has_next_syll:
				next_syll = scansion[i + 1]
				if syll["s"].endswith("u"):
					if next_syll["s"].startswith("u") or next_syll["s"].startswith("i") or next_syll["s"].startswith("e"):
						syll["s"] = syll['s'] + next_syll["s"][1:]
						remove_next_syll = True

			if "uu" in syll['s']:
				syll['s'] = syll['s'].replace("uu","u")
			elif "ui" in syll['s']:
				syll['s'] = syll['s'].replace("ui","u")
			elif "ue" in syll['s']:
				syll['s'] = syll['s'].replace("ue","u")

			new_scansion.append(syll)

		return new_scansion[:]

	def _is_consonant(self, char):
		"""Checks if char is in the list of vowels in the language"""
		return not char in self.language['vowels']

	def _is_vowel(self, char):
		"""Checks if char is in the list of vowels in the language"""
		return char in self.language['vowels']

	def _is_mute_consonant_or_f(self, char):
		"""Checks if char is in the mute_consonants_and_f list"""
		return char in self.language['mute_consonants_and_f']

	def _is_liquid_consonant(self, char):
		"""Checks if char is in the mute_consonants_and_f list"""
		return char in self.language['liquid_consonants']
