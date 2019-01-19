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
            if filename.endswith(".txt"):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r') as file:
                    lines = file.readlines()
                    _check_metadata_format(lines)

                    # Extract data from files.
                    imdb = _check_none(lines[0].split(': ')[1].rstrip())
                    title = _check_none(': '.join(lines[1].split(': ')[1:]).rstrip())
                    year = _check_none(lines[2].split(': ')[1].rstrip(), int)
                    genre = _check_none(lines[3].split(': ')[1].rstrip())
                    if genre is not None:
                        genre = genre.split(', ')
                    director = _check_none(lines[4].split(': ')[1].rstrip())
                    rating = _check_none(lines[5].split(': ')[1].rstrip(), float)
                    bechdel_score = lines[6].split(': ')[1].rstrip()
                    bechdel_score = None if bechdel_score == 'N/A' else int(bechdel_score)
                    imdb_cast_list = _check_none(': '.join(lines[7].split(': ')[1:]).rstrip())
                    imdb_cast = None
                    if imdb_cast_list is not None:
                        imdb_cast_list = imdb_cast_list.split(', ')
                        imdb_cast = [tuple(entry.split(' | ')) for entry in imdb_cast_list]
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


""" HELPER FUNCTIONS """

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

def _check_none(field, cast_fn=str):
    """
    Helper function to check if the text of any given file
    is None.
    """
    if field == 'None':
        return None
    else:
        return cast_fn(field)
