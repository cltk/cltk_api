"""

Download corpora and ingest them into a Mongo database


"""


import celery
import os, sys
from git.exc import GitCommandError
from cltk.corpus.utils.importer import CorpusImporter
from ingest.document import Document
from ingest.learn.lacus_curtius import learn_lacus_curtius
from ingest.learn.latin_library import learn_latin_library
from ingest.learn.perseus import learn_perseus
from util.db import mongo

CORPUS_IMPORTER_CORPORA = ['chinese', 'coptic', 'greek', 'latin', 'multilingual', 'pali', 'tibetan']


class IngestCorpora:

    """Control downloading and ingesting corpora to the database"""

    def __init__( self, corpus_importer_corpora=CORPUS_IMPORTER_CORPORA, n_processes_for_ingest=1 ):

        # Which Corpora to import
        self.corpus_importer_corpora = corpus_importer_corpora

        # How many processes to use for the ingest
        # (currently not functional)
        self.n_processes_for_ingest = n_processes_for_ingest

        # Reset all the ingested text data
        self.reset_document_data()

        # First download all the corpora
        self.import_corpora()

        # Now we need to ingest text from the downloaded corpora text dirs
        self.ingest_documents()


        return


    def import_corpora( self ):
        """Import all corpora that aren't already downloaded"""

        for corpus_importer_slug in CORPUS_IMPORTER_CORPORA:

            corpus_importer = CorpusImporter( corpus_importer_slug )
            for corpus in corpus_importer.list_corpora:
                try:
                    print(" -- Downloading:", corpus)

                    corpus_importer.import_corpus( corpus )

                except AttributeError:
                    print(" -- -- AttributeError downloading")
                    pass

                except GitCommandError:
                    print(" -- -- Corpus already downloaded")
                    pass


        return


    def ingest_documents( self ):
        """Ingest individual documents from the corpora into the database"""
        home = os.path.expanduser("~")
        documents_to_ingest = []

        # Walk directory
        for root, dirs, files in os.walk( home + "/cltk_data/" ):

            path_params = root.split("/")

            if (
                    "git" not in root
                and len(path_params) > 6
                and path_params[5] == "text"
                and path_params[6] == "latin_text_latin_library"
                ):

                for fname in files:
                    documents_to_ingest.append( os.path.join( root, fname ) )


        # Set the total_documents_for_ingest for logging purposes
        total_documents_for_ingest = len( documents_to_ingest )

        # If we've set the ingest to run on more than one process, start celery task group
        """
        At some point, refigure out how to do this with Celery before deploying
        in production
        if N_PROCESSES_FOR_INGEST > 1:
            tasks = celery.group([ self.learn_and_save( i, fname_full, total_documents_for_ingest ) for i, fname_full in enumerate( documents_to_ingest ) ])
            group_task = tasks.apply_async()

        else:
        """
        for i, fname_full in enumerate( documents_to_ingest ):
            self.learn_and_save( i, fname_full, total_documents_for_ingest )



        return


    def learn_and_save( self, i, fname_full, total_documents_for_ingest ):
        """Learn and predict information about the document"""
        print(" -- Document", i, "of", str( total_documents_for_ingest ) + ":", fname_full )

        # Instantiate new algorithm class to learn about document
        document = Document( fname_full )

        # Get the path params as a list to determine the strategy to use to learn
        # about this document
        path_params = fname_full.split("/")

        # Apply a strategy to infer metadata about this document
        if path_params[6] == "latin_text_latin_library":
            document = learn_latin_library( document )

        elif path_params[6] == "latin_text_lacus_curtius":
            document = learn_lacus_curtius( document )

        elif path_params[6] == "latin_text_latin_library":
            document = learn_perseus( document )

        # Save document metadata and text to database
        document.save()

        return


    def reset_document_data( self ):
        """
        Remove all previously ingested document/corpora data
        (Mostly used for debugging)
        """

        db = mongo( "cltk_api" )

        print( " -- Resetting text ingest data in database" )

        db.authors.drop()
        db.corpora.drop()
        db.works.drop()
        db.subworks.drop()
        db.editors.drop()
        db.editors.drop()
        db.editions.drop()
        db.text.drop()
        db.repositories.drop()

        return
