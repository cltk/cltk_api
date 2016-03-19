"""
A class for interfacing with Wikipedia to associate metadata and images to
the CLTK named entities

Example usage:
>>> from cltk_api.metadata.entities.wikipedia import Wikipedia
>>> Wikipedia.query("Aeneas")
{
	'name': 'Aeneas',
	'summary': 'In Greco-Roman mythology, Aeneas (/ᵻˈniːəs/; Greek: Αἰνείας, Aineías, possibly derived from Greek αἰνή meaning "praised") was a Trojan hero, the son of the prince Anchises and the goddess Venus (Aphrodite). His father was the second cousin of King Priam of Troy, making Aeneas Priam\'s second cousin, once removed. He is a character in Greek mythology and is mentioned in Homer\'s Iliad. Aeneas receives full treatment in Roman mythology, most extensively in Virgil\'s Aeneid where he is an ancestor of Romulus and Remus. He became the first true hero of Rome.'
	'images': ['https://upload.wikimedia.org/wikipedia/commons/c/c0/Denier_frapp%C3%A9_sous_C%C3%A9sar_c%C3%A9l%C3%A9brant_le_mythe_d%27En%C3%A9e_et_d%27Anchise.jpg', 'https://upload.wikimedia.org/wikipedia/commons/a/aa/Capitoline_she-wolf_Musei_Capitolini_MC1181.jpg', 'https://upload.wikimedia.org/wikipedia/commons/9/9f/Aineias_Ankhises_Louvre_F118.jpg', 'https://upload.wikimedia.org/wikipedia/commons/3/3c/William_Blake_Richmond_-_Venus_and_Anchises_-_Google_Art_Project.jpg', 'https://upload.wikimedia.org/wikipedia/commons/4/4c/Wikisource-logo.svg', 'https://upload.wikimedia.org/wikipedia/commons/2/2f/B._PINELLI%2C_Enea_e_il_Tevere.jpg', 'https://upload.wikimedia.org/wikipedia/commons/7/76/Aeneas_and_Turnus.jpg', 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Gu%C3%A9rin_%C3%89n%C3%A9e_racontant_%C3%A0_Didon_les_malheurs_de_la_ville_de_Troie_Louvre_5184.jpg', 'https://upload.wikimedia.org/wikipedia/commons/a/a8/Venus_as_Huntress_Appears_to_Aeneas.jpg', 'https://upload.wikimedia.org/wikipedia/en/4/4a/Commons-logo.svg', 'https://upload.wikimedia.org/wikipedia/commons/f/f7/Aeneas%27_Flight_from_Troy_by_Federico_Barocci.jpg'],
	}

"""

import wikipedia

class Wikipedia:

	@staticmethod
	def query(entity_name):
		"""
		Retrieve data from Wikipedia for a given input entity name
		:return wikipedia_entity: dict
		"""

		# Return a wikipedia entity dictionary
		wikipedia_entity = {}

		# Get a list of results from wikipedia for the input entity name
		entity_results = wikipedia.search(entity_name)

		# For the moment, just use the first wikipedia entry
		# Perhaps work in wikipedia.suggest in the future
		if len(entity_results):
			wikipedia_entity['name'] = entity_results[0]

			# Get the summary
			wikipedia_entity['summary'] = wikipedia.summary(wikipedia_entity['name'])

			# Get the page and images
			wikipedia_page = wikipedia.page(wikipedia_entity['name'])
			wikipedia_entity['images'] = wikipedia_page.images


			# Get anything else we might need...


		return wikipedia_entity
