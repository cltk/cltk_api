
import pdb
from flask import abort, request
from flask_restful import Resource, Api
from ingest.ingest_corpora import IngestCorpora

class Ingest(Resource):
    def get(self ):

        ingest_corpora = IngestCorpora()


        return "Ingest successful."
