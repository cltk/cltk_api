import pymongo

def mongo(db, host="localhost", port=27017):
	"""

	A small utility function for dealing with pymongo in very common
	usage scenarios

	Usage:

	>>> from cltk_api.util.db import mongo
	>>> db = mongo( "my_db_name" )
	>>> db.mycollection.insert({
			'foo' : "bar"
		})


	If more advanced configurations are needed, then it may be better
	to deal with pymongo directly


	"""
	client = pymongo.MongoClient(host, port, max_pool_size=None)

	return client[db]
