import pdb
import os
import pkgutil
import encodings


class Document:


    def __init__( self, fname_full ):

        # Full path including filename
        self.fname_full = fname_full

        # Set the type of file
        self.file_extension = os.path.splitext( fname_full )

        # Load the encodings
        self.encodings = self._all_encodings()

        # Document metadata
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
        if self.file_extension in ['xml', 'html']:
            print( " -- parsing content", self.fname_full )
            self.soup = BeautifulSoup( self.text_content )


        return

    def _all_encodings(self):
        modnames = set([modname for importer, modname, ispkg in pkgutil.walk_packages(
                        path=[os.path.dirname(encodings.__file__)], prefix='')])
        aliases = set(encodings.aliases.aliases.values())

        return modnames.union(aliases)


    def _read_file(self):

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


    def learn( self ):
        """
        Apply a strategy to infer metadata about this document
        """

        if self.path_params[6] == "latin_text_latin_library":
            learn_latin_library()

        elif self.path_params[6] == "latin_text_lacus_curtius":
            learn_lacus_curtius()

        elif self.path_params[6] == "latin_text_latin_library":
            learn_perseus()



        return


    def save( self ):
        """
        Save document text units and metadata to database
        """

        ingest_document = mongo.db.ingest_documents.insert({
            'fname_full' : document.fname_full
        })

        # Corpus
        corpus = {
                'slug' : document.corpus_slug,
                'title' : document.corpus_slug.title()
            }

        # Author
        author = {
                'slug' : document.author,
                'name_english' : document.author,
                'name_original' : document.author
            }

        # Repository
        repository = {
                'slug' : slugify( document.repository ),
                'title' : document.repository

            }


        # Work
        work = {
                'title' : document.work[0:199],
                'slug' : slugify( document.work[0:199] ),
                'corpus' : document.corpus_slug,
                'authors' : [{
                    'slug' document.author
                }]
                'ingest_document' : document.fname_full

            }

        # Genre
        genre = {
                'title' : document.genre.title(),
                'slug' : document.genre

            }

        # Edition
        edition = {
                'title' : document.edition_title,
                'slug' : slugify( document.edition_title ),
                'repository' : slugify( document.repository )

            }

        # Text units
        for text_unit in document.text_units:

            text = {
                'work' : slugify( document.work[0:199] ),
                'subwork' : {
                    'slug' : text_unit['subwork']
                    'n' : text_unit['subwork_n']
                },
                'genre' : document.genre,
                'n' : text_unit['n'],
                'text' : text_unit['text'],
                'html' : text_unit['html']

            }


        """

        Save things

        """


        return
