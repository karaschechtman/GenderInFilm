__author__ = 'Kara Schechtman <kws2121@columbia.edu>'
__date__ = 'Jan 15, 2019'

DATA_PATH = 'data/'

IMDB_KEY = 'IMDB: '
TITLE_KEY = 'Title: '
YEAR_KEY = 'Year: '
GENRE_KEY = 'Genre: '
DIRECTOR_KEY = 'Director: '
RATING_KEY = 'Rating: '
BECHDEL_SCORE_KEY = 'Bechdel score: '
IMDB_CAST_KEY = 'IMDB Cast: '

import os
from character import Character
from movie import Movie

class DataLoader(object):
    """
    Loads metadata and data of movie files into Movie objects.
    """
    def __init__(self):
        self.movies = []
        data_dir = os.path.join(os.getcwd(), DATA_PATH)

        for filename in os.listdir(data_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r') as file:
                    lines = file.readlines()
                    _check_metadata_format(lines)
                    # Get metadata.
                    imdb = _read_field(lines[0])
                    title = _read_field(lines[1])
                    print('Loading %s...' % (title) )
                    year = _read_field(lines[2], cast_fn=int)
                    genre = _read_field(lines[3], split=True)
                    director = _read_field(lines[4])
                    rating = _read_field(lines[5], cast_fn=float)
                    bechdel_score = _read_field(lines[6], cast_fn=int)
                    imdb_cast_list = _read_field(lines[7], split=True)
                    imdb_cast = imdb_cast_list if not imdb_cast_list \
                                else [tuple(entry.split(' | ')) for entry in imdb_cast_list]
                    characters = _extract_characters(lines[9:])

                # Create movie object and save.
                self.movies.append(Movie(imdb, title, year,
                                         genre, director, rating,
                                         bechdel_score, imdb_cast,
                                         characters))
        print('All data loaded!')

def _read_field(line, cast_fn = None, split = False):
    """
    Helper function to handle retrieve field value from the text file.
    """
    field = ': '.join(line.split(': ')[1:]).rstrip() # Read in the field.
    if field == 'None':
        return None
    elif split == True:
        return field.split(', ')
    elif cast_fn:
        return cast_fn(field)
    else:
        return field

def _check_metadata_format(lines):
    """
    Helper function to check format of the metadata in Agarwal.
    """
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

def _extract_characters(script):
    """
    Helper function to create Character objects from file.
    """
    characters = []
    for person in script:
        name_to_lines = person.rstrip().split(': ')
        name = ': '.join(name_to_lines[0:-1])
        line_data = [int(num) for num in name_to_lines[-1].split(', ')]
        characters.append(Character(name, line_data))
    return characters
