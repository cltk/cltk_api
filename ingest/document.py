"""

A document to ingest, coressponding always to a single file residing
in ~/cltk_data

"""


import pdb
import os
import pkgutil
import encodings
from bs4 import BeautifulSoup
from slugify import slugify
from util.db import mongo


class Document:
    """A single document, to be learned about and saved to the database"""


    def __init__( self, fname_full ):

        # Full path including filename
        self.fname_full = fname_full
        self.path_params = fname_full.split("/")

        # Set the type of file
        self.file_extension = os.path.splitext( fname_full )[-1]

        # Load the encodings
        self.encodings = self._all_encodings()

        # self metadata
        self.title = ""
        self.author = ""
        self.genre = ""
        self.corpus_slug = ""
        self.work = ""
        self.digital_repository = ""
        self.edition_title = ""
        self.edition_editor = ""
        self.edition_year = 0
        self.edition_citation = ""
        self.text_units = []
        self.avg_text_len = 0

        # Read file into string for parsing
        self.text_content = self._read_file()

        # If is a parseable document, parse docroot
        self.soup = None
        if self.file_extension in ['.xml', '.html']:
            self.soup = BeautifulSoup( self.text_content )


        return

    def _all_encodings(self):
        """
        Util method that returns all types of file encodings to try to open a
        given document with
        """
        modnames = set([modname for importer, modname, ispkg in pkgutil.walk_packages(
                        path=[os.path.dirname(encodings.__file__)], prefix='')])
        aliases = set(encodings.aliases.aliases.values())

        return modnames.union(aliases)


    def _read_file(self):
        """Open and read a the contents of a file"""

        text_content = ""

        try:
            with open(self.fname_full, encoding='utf-8') as f:
                text_content = f.read()

        except Exception:
            for enc in self.encodings:
                try:
                    with open(self.fname_full, encoding=enc) as f:
                        text_content = f.read()
                    break

                except Exception:
                    pass

        return text_content


    def get_avg_text_len(self):
        """
        Calculate the length of the average text unit (paragraph, line, etc.)
        """

        lengths = []

        if len( self.text_units ):
            for text_unit in self.text_units:
                lengths.append( len( text_unit['text'] ) )

            return sum( lengths ) / len( lengths )

        else:
            return 0


    def save( self ):
        """
        Save document text units and metadata to database
        """

        db = mongo( "cltk_api" )

        ingest_document_id = db.ingest_documents.insert({
            'fname_full' : self.fname_full
        })

        # Corpus
        corpus = {
                'slug' : slugify( self.corpus_slug ),
                'title' : self.corpus_slug.title()
            }
        corpus_id = db.corpora.update({
                                        'slug' : corpus['slug']
                                    },
                                    corpus,
                                    upsert=True )

        # Author
        author = {
                'slug' : slugify( self.author ),
                'name_english' : self.author,
                'name_original' : self.author
            }
        author_id = db.authors.update({
                                        'slug' : author['slug']
                                    },
                                    author,
                                    upsert=True )
        # Repository
        repository = {
                'slug' : slugify( self.repository ),
                'title' : self.repository

            }
        repository_id = db.repositories.update({
                                        'slug' : repository['slug']
                                    },
                                    repository,
                                    upsert=True )


        # Work
        work = {
                'title' : self.work[0:199],
                'slug' : slugify( self.work[0:199] ),
                'corpus' : corpus['slug'],
                'authors' : [{
                    'slug' : author['slug']
                }],
                'ingest_documents' : [self.fname_full]
            }

        existing_work = db.works.find_one({ 'slug' : work['slug'] })
        if existing_work:

            # Check if the author is already listed in the existing work authors
            existing_work_has_current_author = False
            for existing_work_author in existing_work['authors']:
                if author['slug'] == existing_work_author['slug']:
                    existing_work_has_current_author = True

            # If the author is already in the existing work authors, don't add it
            if existing_work_has_current_author:

                db.works.update({
                        'slug' : work['slug']
                    }, {
                        '$addToSet' : {
                                'ingest_documents' : self.fname_full
                            }
                        })

            # Otherwise, if the author isn't listed, add it to the authors set
            else:
                db.works.update({
                        'slug' : work['slug']
                    }, {
                        '$addToSet' : {
                                'authors' : {
                                    'slug' : author['slug']
                                },
                                'ingest_documents' : self.fname_full
                            }
                        })

            work_id = existing_work['_id']

        else:
            work_id = db.works.insert(work)


        # Genre
        genre = {
                'title' : self.genre.title(),
                'slug' : slugify( self.genre )

            }
        genre_id = db.genres.update({
                                        'slug' : work['slug']
                                    },
                                    genre,
                                    upsert=True )

        # Edition
        edition = {
                'title' : self.edition_title,
                'slug' : slugify( self.edition_title ),
                'repository' : slugify( self.repository )

            }
        edition_id = db.editions.update({
                                        'slug' : edition['slug']
                                    },
                                    edition,
                                    upsert=True )

        # Text units
        for text_unit in self.text_units:

            text_id = db.text.insert({
                    'work' : slugify( self.work[0:199] ),
                    'subwork' : {
                        'slug' : text_unit['subwork'],
                        'n' : text_unit['subwork_n']
                    },
                    'genre' : self.genre,
                    'n' : text_unit['n'],
                    'text' : text_unit['text'],
                    'html' : text_unit['html']

                })




        return
