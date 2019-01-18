__author__ = "Kara Schechtman <kws2121@columbia.edu>"
__date__ = "Jan 15, 2019"

DATA_PATH = "data/agarwal"

IMDB_KEY = "IMDB: "
TITLE_KEY = "Title: "
YEAR_KEY = "Year: "
GENRE_KEY = "Genre: "
DIRECTOR_KEY = "Director: "
RATING_KEY = "Rating: "
BECHDEL_SCORE_KEY = "Bechdel score: "
IMDB_CAST_KEY = "IMDB Cast: "

import os
from movie import Movie

class AgarwalDataManager(object):
    """
    Loads metadata and data of movie files into Movie objects.
    """
    def __init__(self):
        self.movies = []
        data_dir = os.path.join(os.getcwd(), DATA_PATH)

        # none check function
        def check_none(field, cast_fn=str):
            if field == 'None':
                return None
            else:
                return cast_fn(field)

        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r') as file:
                    lines = file.readlines()
                    # Ensure the metadata order is correct.
                    if IMDB_KEY not in lines[0] or \
                       TITLE_KEY not in lines[1] or \
                       YEAR_KEY not in lines[2] or \
                       GENRE_KEY not in lines[3] or \
                       DIRECTOR_KEY not in lines[4] or \
                       RATING_KEY not in lines[5] or \
                       BECHDEL_SCORE_KEY not in lines[6] or \
                       IMDB_CAST_KEY not in lines[7]:

                       raise Exception(filename +
                                       ' metadata formatted incorrectly.')

                    # Get metadata.
                    imdb = check_none(lines[0].split(': ')[1].rstrip())
                    title = check_none(': '.join(lines[1].split(': ')[1:]).rstrip())
                    year = check_none(lines[2].split(': ')[1].rstrip(), int)
                    genre = check_none(lines[3].split(': ')[1].rstrip().split(', '), list)
                    director = check_none(lines[4].split(': ')[1].rstrip())
                    rating = check_none(lines[5].split(': ')[1].rstrip(), float)
                    bechdel_score = lines[6].split(': ')[1].rstrip()
                    bechdel_score = None if bechdel_score == 'N/A' else int(bechdel_score)
                    imdb_cast_list = ': '.join(lines[7].split(': ')[1:]).rstrip().split(', ')
                    imdb_cast = [tuple(entry.split(' | ')) for entry in imdb_cast_list]

                # Create movie object and save.
                self.movies.append(Movie(imdb, title, year,
                                         genre, director, rating,
                                         bechdel_score, imdb_cast,
                                         lines[8:]))

    def write_data(self):
        for movie in self.movies:
            filename = 'data/%s.txt' % (movie.title)
            with open(filename, 'w+') as file:
                print(movie.title)
                file.write('%s%s\n' % (IMDB_KEY, movie.imdb))
                file.write('%s%s\n' % (TITLE_KEY, movie.title))
                file.write('%s%s\n' % (YEAR_KEY, movie.year))
                file.write('%s%s\n' % (GENRE_KEY, ', '.join(movie.genre)))
                file.write('%s%s\n' % (DIRECTOR_KEY, movie.director))
                file.write('%s%s\n' % (RATING_KEY, movie.rating))
                file.write('%s%s\n' % (BECHDEL_SCORE_KEY, movie.bechdel_score))
                file.write('%s%s\n\n' % (IMDB_CAST_KEY, ', '.join('%s | %s' % (tup[0], tup[1]) for tup in movie.imdb_cast)))
                for character in movie.characters:
                    file.write('%s: %s\n' % (character.name, ', '.join(['%s' % (i) for i in character.line_data])))
