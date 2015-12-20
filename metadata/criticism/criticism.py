"""Ingest citations for criticism"""
import time
import string
import random
import urllib.request
from bs4 import BeautifulSoup
from cltk_api.util.db import mongo

class Criticism:

	def __init__(self, dbname):
		"""Setup db connection to mongo"""
		self.dbname = dbname
		self.punctuation_transtable = {ord(c): None for c in string.punctuation}

		return

	def ingest(self, line):
		"""Ingest citation data to the database and mark done for later processing"""

		try:

			cites = self.search_jstor(line)
			for cite in cites:
				cite['line'] = line
				self.save(cite)

		except:
			return False


		return True

	def search_jstor(self, line):
		"""Search for line via JSTOR API"""
		cites = []
		pages = []

		# Make URL to query
		sline = line['line']['text'].translate(self.punctuation_transtable).lower()
		sline = sline.replace(" ","+").lower()
		sline = sline.replace("—", "")

		url = "http://dfr.jstor.org/?view=text&qk0=ft&qw0=1.0&qv0=%22" + sline + "%22&qf0=any&sk=ca"

		# Get the page
		res = urllib.request.urlopen(url)
		html = res.read()
		soup = BeautifulSoup(html)
		pagination = soup.select(".pagination a")
		cites.extend(self._parse_jstor_page(soup))

		# Get the paginated results
		for elem in pagination:
			#If elem doesn't have classes "prevnextlink" and "currentpage"
			try:
				if "prevnextlink" not in elem['class'] and "currentpage" not in elem['class']:
					pages.append("http://dfr.jstor.org/" + elem['href'])
			except:
				try:
					pages.append("http://dfr.jstor.org/" + elem['href'])
				except:
					pass

		time.sleep(random.randint( 2, 5 ))
		for i, page_link in enumerate(pages):
			print(" -- querying page", i + 2)
			res = urllib.request.urlopen(page_link)
			html = res.read()
			soup = BeautifulSoup(html)
			cites.extend(self._parse_jstor_page(soup))
			time.sleep(random.randint( 2, 5 ))

		return cites

	def _parse_jstor_page(self, soup):
		c = []
		res = soup.select("ul.results_item")
		for el in res:
			c.append({
					'title' : el.select(".title")[0].text,
					'author' : el.select(".author")[0].text,
					'cite' : el.select('li')[2].text
				})

		return c

	def save(self, cite):
		"""Save the citation to the db for processing"""
		db = mongo(self.dbname)
		db.criticism.insert(cite)
		return
