__author__ = 'Kara Schechtman <kws2121@columbia.edu>'
__date__ = 'Jan 15, 2019'

DATA_PATH = 'data/agarwal'

IMDB_KEY = 'IMDB: '
TITLE_KEY = 'Title: '
YEAR_KEY = 'Year: '
GENRE_KEY = 'Genre: '
DIRECTOR_KEY = 'Director: '
RATING_KEY = 'Rating: '
BECHDEL_SCORE_KEY = 'Bechdel score: '
IMDB_CAST_KEY = 'IMDB Cast: '

CHARACTER = 'C|'
DIALOGUE = 'D|'

import os
from Character import Character
from collections import OrderedDict
from movie import Movie
from name_processing import variant_to_root

class AgarwalDataManager(object):
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

                    # Extract data from files.
                    imdb = _read_field(lines[0])
                    title = _read_field(lines[1])
                    year = _read_field(lines[2], cast_fn=int)
                    genre = _read_field(lines[3], split=True)
                    director = _read_field(lines[4])
                    rating = _read_field(lines[5], cast_fn=float)
                    bechdel_score = _read_field(lines[6], cast_fn=int)
                    imdb_cast_list = _read_field(lines[7], split=True)
                    imdb_cast = imdb_cast_list if not imdb_cast_list \
                                else [tuple(entry.split(' | ')) for entry in imdb_cast_list]
                    characters = _extract_characters(lines[8:])

                # Create movie object and save.
                self.movies.append(Movie(imdb, title, year,
                                         genre, director, rating,
                                         bechdel_score, imdb_cast,
                                         characters))

    def write(self):
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


def _read_field(line, cast_fn = None, split = False):
    """
    Helper function to handle retrieve field value from the text file.
    """
    field = ': '.join(line.split(': ')[1:]).rstrip() # Read in the field.
    if field == 'None' or field == 'N/A':
        return None
    elif split == True:
        return field.split(', ')
    elif cast_fn:
        return cast_fn(field)
    else:
        return field

def _check_metadata_format(lines):
    """
    Helper function to check the metadata of the file
    is formatted correctly.
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
    Helper to extract information on character dialogue lines
    from the Agarwal script file.
    """
    name = None
    dialogue = ''
    names = OrderedDict()
    for datum in script:
        if datum.startswith(CHARACTER):
            if name in names.keys():
                names[name].append(dialogue.strip())
            else:
                names[name] = [dialogue.strip()]
            name = variant_to_root(datum.split(CHARACTER)[1].strip())
            dialogue = ''
        if datum.startswith(DIALOGUE):
            dialogue += ' ' + datum.split(DIALOGUE)[1].strip()

    # Create and save character objects.
    characters = []
    for name in names:
        line_data = []
        for line in names[name]:
            words = line.split()
            if len(words) != 0:
                line_data.append(len(words))
        if len(line_data) != 0:
            characters.append(Character(name, line_data))
    return characters
