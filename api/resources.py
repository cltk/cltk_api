

import pdb
import json
from flask import abort, request
from flask_restful import Resource, Api
from util.db import mongo

class Query(Resource):
    def get( self ):


        params = request.args.to_dict()
        db = mongo( "cltk_api" )

        # Check if there is a collection listed in the API query
        if 'collection' in params:
            # Save the request collection for later
            request_collection = params.collection
            del params.collection

        else:
            # default collection is text
            request_collection = "text"

        # Check if there is a collection listed in the API query
        if 'limit' in params:
            # Save the request collection for later
            request_limit = params.limit
            del params.limit

        else:
            # Default limit is 30
            request_limit = 30


        pdb.set_trace()



        return request.args
