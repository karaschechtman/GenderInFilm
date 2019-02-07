from data_loader import DataLoader
from predict_gender import get_movie_genders_dict


def assign_genders(data_loader):
    """
    EXERCISE 1.
    For every movie in the DataLoader, call predict_gender and
    assign the returned genders to the Character objects'
    gender fields.
    """
    for movie in data_loader.movies.values():
        character_genders = get_movie_genders_dict(movie)
        for character in character_genders:
            movie.get_character(character).gender = character_genders[character]

def _print_gender_counts(data_loader):
    """
    Helper function to print results for exercise 1.
    """
    m = 0
    f = 0
    for movie in data_loader.movies:
        mov_obj = data_loader.movies[movie]
        for character in mov_obj.characters:
            char_obj = mov_obj.get_character(character)
            if char_obj.gender == 'M':
                m+=1
            elif char_obj.gender == 'F':
                f+=1
    print("Number of male characters: %d" % m)
    print("Number of female characters: %d" % f)

if __name__ == "__main__":
    data_loader = DataLoader(verbose=False)

    print("INTRODUCTORY EXERCISE")
    assign_genders(data_loader)
    _print_gender_counts(data_loader)
    print("----------------------------")
