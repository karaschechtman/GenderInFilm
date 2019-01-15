__author__ = "Kara Schechtman <kws2121@columbia.edu>"
__date__ = "Jan 15, 2019"

DATA_PATH = "data"

IMDB_KEY = "IMDB: "
TITLE_KEY = "Title: "
YEAR_KEY = "Year: "
GENRE_KEY = "Genre: "
DIRECTOR_KEY = "Director: "
RATING_KEY = "Rating: "
BECHDEL_SCORE_KEY = "Bechdel score: "

import os
from movie import Movie

class DataLoader(object):
    """
    Loads metadata and data of movie files into Movie objects.
    """
    def __init__(self):
        self.movies = []
        data_dir = os.path.join(os.getcwd(), DATA_PATH)
        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r') as file:
                    lines = file.readlines()
                    # Ensure the metadata order is correct
                    if IMDB_KEY not in lines[0] or \
                       TITLE_KEY not in lines[1] or \
                       YEAR_KEY not in lines[2] or \
                       GENRE_KEY not in lines[3] or \
                       DIRECTOR_KEY not in lines[4] or \
                       RATING_KEY not in lines[5] or \
                       BECHDEL_SCORE_KEY not in lines[6]:

                       raise Exception(filename +
                                       ' metadata formatted incorrectly.')

                    # Get metadata.
                    imdb = lines[0].split(': ')[1].rstrip()
                    title = ': '.join(lines[1].split(': ')[1:]).rstrip()
                    year = int(lines[2].split(': ')[1].rstrip())
                    genre = lines[3].split(': ')[1].rstrip().split(', ')
                    director = lines[4].split(': ')[1].rstrip()
                    rating = float(lines[5].split(': ')[1].rstrip())
                    bechdel_score = int(lines[6].split(': ')[1].rstrip())

                self.movies.append(Movie(imdb, title, year,
                                         genre, director, rating,
                                         bechdel_score, lines[7:]))
