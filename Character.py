__author__ = "Kara Schechtman <kws2121@columbia.edu>"
__date__ = "Jan 15, 2019"

class Character(object):
    """
    Stores data and metadata about a particular chracter,
    associating lines to each character.
    Name stores the name of the character.
    Line data is a list of ints. Each entry represents a line
    and has a value equal to the number of words in that line.
    Gender is set to None by default.
    """
    def __init__(self, name, line_data):
        self.name = name
        self.line_data = line_data
        self.gender = None
