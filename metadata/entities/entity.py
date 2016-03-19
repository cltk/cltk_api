"""
A class for working with Entities retrieved from the NER core functionality
of the CLTK
"""

import string
import os
import json
import re
import random
from time import sleep
from urllib.request import urlopen, urlretrieve
from urllib import error
from bs4 import BeautifulSoup
from cltk_api.metadata.entities.wikipedia import Wikipedia


class Entity:

	def __init__(self, name_english, name_original):

		self.name_english = name_english
		self.name_original = name_original
		self.punctuation_transtable = {ord(c): None for c in string.punctuation}

		# External resources
		self.wikipedia_entity = {}

		return

	def fetch_wikipedia(self):
		"""
		Fetch metadata, images, and summaries about an entity from Wikipedia
		"""

		return Wikipedia.query(self.name_english)
