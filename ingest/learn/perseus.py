import re
import bs4

def learn_perseus( document ):

    # Set metadata already known about document
    document.repository = "Perseus Digital Library"

    """
    document.title = root.title.text
    document.author = root.author.text
    document.language = root.language.text
    document.text = root.body.text
    """


    return document
