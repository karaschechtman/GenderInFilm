__author__ = "Kara Schechtman <kws2121@columbia.edu>"
__date__ = "Jan 15, 2019"

from Character import Character
from collections import defaultdict
from name_processing import variant_to_root

CHARACTER = 'C|'
DIALOGUE = 'D|'

class Movie(object):
    """
    Stores data and metadata about a particular movie.
    """
    def __init__(self, imdb, title, year,
                 genre, director, rating, bechdel_score,
                 imdb_cast, script):
        # Set metadata.
        self.imdb = imdb
        self.title = title
        self.year = year
        self.genre = genre
        self.director = director
        self.rating = rating
        self.bechdel_score = bechdel_score
        self.imdb_cast = imdb_cast
        self.characters = []

        # Create a mapping from characters to their lines.
        name = None
        dialogue = ''
        names = defaultdict(list)
        for datum in script:
            if datum.startswith(CHARACTER):
                name = variant_to_root(datum.split(CHARACTER)[1].strip())
                names[name].append(dialogue.strip())
                dialogue = ''
            if datum.startswith(DIALOGUE):
                dialogue += ' ' + datum.split(DIALOGUE)[1].strip()

        # Create and save character objects.
        for name in names:
            line_data = []
            for line in names[name]:
                line_data.append(len(line.split()))
            self.characters.append(Character(name, line_data))
