import re
import string
from util.numerals import fromRoman, InvalidRomanNumeralError
from util.util import strip_punctution

def learn_latin_library( document ):

    # Set metadata already known about document
    document.corpus_slug = "latin"
    document.repository = "The Latin Library"

    # Text numbering
    text_n = 0
    lines_since_last_subwork_update = 0

    # Subwork vars
    if len( document.path_params ) == 9:
        subwork_n = document.path_params[-1].split('.')[0]
    else:
        subwork_n = None
    subwork = subwork_n

    # Process text content and predict information gathered from content
    for text_line in document.text_content.split("\n"):

        # If the line has any textual content
        text_line = text_line.strip()
        len_text_line = len(text_line)
        if len_text_line:

            # If, it's the first line, try to infer author / title
            if text_n == 0:

                # split the first line on any punctuation
                first_line_params = re.split( '[' + string.punctuation + ']', text_line )
                first_line_param_n = 0
                for first_line_param in first_line_params:
                    first_line_param = first_line_param.strip()

                    if len( first_line_param ):

                        if first_line_param_n == 0:
                            document.author = first_line_param

                        else:
                            if len( document.work ):
                                document.work += " " + first_line_param
                            else:
                                document.work = first_line_param

                        first_line_param_n += 1

                # Finally, increase count to the first line/paragraph
                text_n += 1



            # Otherwise check the line for metadata value or textual content
            else:

                # If the line is less than 200 chars, check if it is a title or other data
                if len( text_line ) < 200:

                    # Check how many of the text_line characters are uppercase
                    n_uppercase_chars = 0
                    for char in text_line:
                        if char.isupper():
                            n_uppercase_chars +=1

                    # If most of the text_line characters are uppercase, it's probably a title line
                    if n_uppercase_chars >= (len_text_line * 0.7) or text_line.istitle():

                        # Check if can be parsed as Roman numeral
                        parsed_numeral = None
                        try:
                            text_line_stripped_punc = strip_punctution( text_line ).strip()
                            parsed_numeral = fromRoman( text_line_stripped_punc )

                        except InvalidRomanNumeralError:
                            pass

                        # If we don't have a subwork denoted in the filepath
                        if len( document.path_params ) <= 8:
                            # If the line was able to parsed as a numeral, update subwork and then move to next line
                            if parsed_numeral:
                                subwork_n = parsed_numeral
                                subwork = text_line_stripped_punc

                            # Else, it's still probably some amount of subwork information, but set subwork_n to null
                            else:
                                subwork_n = None
                                if lines_since_last_subwork_update > 0 and subwork:
                                    subwork = subwork + " " + text_line
                                else:
                                    subwork = text_line

                            lines_since_last_subwork_update = 0

                        # Either way, continue and do not add this line to the text units for the doc
                        continue


                # Add text unit to the document text units
                document.text_units.append( {
                        'n' : text_n,
                        'subwork' :  subwork,
                        'subwork_n' :  subwork_n,
                        'html' : text_line,
                        'text' : text_line
                    })
                text_n += 1
                lines_since_last_subwork_update += 1


    # Set document genre
    document.avg_text_len = document.get_avg_text_len()
    if document.avg_text_len > 100:
        document.genre = 'prose'
    elif document.avg_text_len > 0 and document.avg_text_len < 100:
        document.genre = 'poetry'

    # Check if document work title is defined; if not, infer from fname and path
    if len(document.work) == 0:

        if len(document.path_params) == 8:
            document.work = document.path_params[7].split('.')[0].title()

        elif len(document.path_params) == 9:
            document.work = document.path_params[8].split('.')[0].title()

            if len(document.author) == 0:
                document.author = document.path_params[7].split('.')[0].title()

        else:

            print(" -- Error inferring document metada from fullpath:", document.fname_full)

    return document
