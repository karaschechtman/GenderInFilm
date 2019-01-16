__author__ = "Kara Schechtman <kws2121@columbia.edu>"
__date__ = "Jan 15, 2019"

class Movie(object):
    """
    Stores data and metadata about a particular movie.
    """
    def __init__(self, imdb, title, year,
                 genre, director, rating, bechdel_score,
                 data):
        self.imdb = imdb
        self.title = title
        self.year = year
        self.genre = genre
        self.director = director
        self.rating = rating
        self.bechdel_score = bechdel_score
        self.characters = []
