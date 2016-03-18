# Finding text reuse via CF module 

from cf.cf import Cf

class MapReuse:
	def __init__(self, settings):

		settings.drop = False
		settings.chunk = True
		settings.compare = True
		settings.associate = False
		settings.export = False

		Cf(settings)
		return
