import string


def strip_punctution( s ):

    exclude = set(string.punctuation)

    return ''.join(ch for ch in s if ch not in exclude)
