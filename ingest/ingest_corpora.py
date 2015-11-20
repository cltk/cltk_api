import celery
import os, sys
from git.exc import GitCommandError
from cltk.corpus.utils.importer import CorpusImporter
from cltk_api.ingest.document import Document

CORPUS_IMPORTER_CORPORA = ['greek', 'latin', 'chinese', 'coptic', 'multilingual', 'pali', 'tibetan']
N_PROCESSES_FOR_INGEST = 1

mongo = PyMongo(app)

# Ingest documents from the CTLK corpora
def ingest_corpora( ingest_id ):

    # Reset all the ingested text data
    reset_document_data()

    # First download all the corpora
    import_corpora()

    # Now we need to ingest text from the downloaded corpora text dirs
    ingest_documents()


    return


# Import corpora via the CLTK corpora importer
def import_corpora():

    for corpus_importer_slug in CORPUS_IMPORTER_CORPORA:

        corpus_importer = CorpusImporter( corpus_importer_slug )
        for corpus in corpus_importer.list_corpora:
            try:
                print(corpus)
                corpus_importer.import_corpus( corpus )
            except GitCommandError:
                pass


    return


# Ingest the documents to the database
def ingest_documents():
    home = os.path.expanduser("~")
    documents_to_ingest = []

    # Walk directory
    for root, dirs, files in os.walk( home + "/cltk_data/" ):

        path_params = root.split("/")

        if (
                "git" not in root
            and len(path_params) > 6
            and path_params[5] == "text"
            # and path_params[6] == "latin_text_latin_library"
            ):

            for fname in files:
                documents_to_ingest.append( os.path.join( root, fname ) )


    # Set the total_documents_for_ingest for logging purposes
    total_documents_for_ingest = len( documents_to_ingest )

    # If we've set the ingest to run on more than one process, start celery task group
    if N_PROCESSES_FOR_INGEST > 1:
        tasks = celery.group([ learn_and_save( i, fname_full, total_documents_for_ingest ) for i, fname_full in enumerate( documents_to_ingest ) ])
        group_task = tasks.apply_async()

    else:
        for i, fname_full in enumerate( documents_to_ingest ):
            learn_and_save( i, fname_full, total_documents_for_ingest )



    return


# Learn and predict information about the document
@celery.task
def learn_and_save( i, fname_full, total_documents_for_ingest ):
    print(" -- Document", i, "of", str( total_documents_for_ingest ) + ":", fname_full )

    # Instantiate new algorithm class to learn about document
    document = Document( fname_full )
    document.learn()

    # Save document metadata and text to database
    document.save()



# Remove all previously ingested document/corpora data
def reset_document_data( ):

    print( " -- Resetting text ingest data in database" )

    mongo.db.authors.drop()
    mongo.db.corpora.drop()
    mongo.db.works.drop()
    mongo.db.subworks.drop()
    mongo.db.editors.drop()
    mongo.db.editors.drop()
    mongo.db.editions.drop()
    mongo.db.text.drop()
    mongo.db.repositories.drop()

    return
