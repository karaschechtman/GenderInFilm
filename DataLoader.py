__author__ = "Kara Schechtman <kws2121@columbia.edu>"
__date__ = "Jan 15, 2019"

DIRECTORY_PATH = "data/"


class DataLoader(object):
    """
    Loads metadata and data of movie files into Movie objects.
    """
    def __init__(self):
        self.movies = []
