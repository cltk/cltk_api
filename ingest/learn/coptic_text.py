import re
import string
import json
import pdb


def learn_coptic_text( document ):


    # Set metadata already known about document
    document.corpus_slug = "coptic"
    document.repository = "Coptic Text Scriptorium"

    # Infer metadata from header
    document.title = str( document.soup.title.string )
    document.author = str( document.soup.author.string )
    # At some point do fancier things grouping these documents
    #document.work = str( document.soup.creation.title.string )
    document.work = document.title

    document.edition_title = "Coptic Text Scriptorium"


    def recursive_walk( elem, data ):

        if elem.name in ['cb','div']:
            data['subwork_n'] += 1

        elif elem.name == "lb":
            if data['text_n'] > 0:
                data = end_text_unit( data )
            data['text_n'] = int( elem.attrs['n'] )

        else:
            if hasattr( elem, "children" ):
                for child_elem in elem.children:
                    data = recursive_walk( child_elem, data )

            else:
                try:
                    data['line_text'] += elem.get_text().replace("\n", " ")
                except AttributeError:
                    data['line_text'] += elem.string.replace("\n", " ")


        return data


    def end_text_unit( data ):
        """End the current text unit"""
        data['line_text'] = data['line_text'].replace('\n', '')
        data['line_text'] = re.sub( " +", " ", data['line_text'] )

        document.text_units.append({
                'n' : data['text_n'],
                'subwork' : str( data['subwork_n'] ),
                'subwork_n' : data['subwork_n'],
                'html' : "",
                'text' : data['line_text']
            })

        data['line_text'] = ""

        return data

    data = {
            'subwork_n' : 0,
            'text_n' : 0,
            'line_text' : ""
        }
    data = recursive_walk( document.soup.body.ab, data )
    data = end_text_unit( data )


    return document
