from data_loader import DataLoader
from gender_predict import predict_gender


def assign_genders(data):
    """
    EXERCISE 1.
    For every movie in the DataLoader, call predict_gender and
    assign the returned genders to the Character objects'
    gender fields.
    """
    for movie in data.movies.values():
        character_genders = predict_gender(movie)
        for character in character_genders:
            movie.get_character(character).gender = character_genders[character]

def get_top_n_billed_by_gender(data, n):
    """
    EXERCISE 2.
    Given a positive integer n, return a dictionary mapping
    genders to movies where the top n billed are all of that
    gender. Dictionary keys should be strings ('M' or 'F')
    and dictionary values should be lists of the titles
    of the movies with the top n billed of that gender.
    If there are no top n billed, the value should be an
    empty list.
    """
    top_n_billed = {"M":[], "F":[]}
    for movie in data.movies.values():
        just_male, just_female = True, True
        i = 0
        imdb_cast = iter(movie.imdb_cast.values())
        while i < n and (just_male or just_female):
            i+=1
            try:
                char = next(imdb_cast)
                gender = char[1]
                if gender=='M':
                    just_female = False
                elif gender=='F':
                    just_male = False
                else:
                    just_male, just_female = False, False
            except StopIteration:
                just_male, just_female = False, False
        if just_male:
            top_n_billed["M"].append(movie.title)
        if just_female:
            top_n_billed["F"].append(movie.title)
    return top_n_billed

def _print_gender_counts(data):
    """
    Helper function to print results for exercise 1.
    """
    m = 0
    f = 0
    for movie in data.movies:
        mov_obj = data.movies[movie]
        for character in mov_obj.characters:
            char_obj = mov_obj.get_character(character)
            if char_obj.gender == 'M':
                m+=1
            elif char_obj.gender == 'F':
                f+=1
    print("Number of male characters: %d" % m)
    print("Number of female characters: %d" % f)

def _print_top_n_billed(top_n_billed, n):
    """
    Helper function to print results for exercise 2.
    """
    if len(top_n_billed['M']) == 0:
        print("No movies with top %d male billed!" % n)
    else:
        print("Movies with top %d male billed:" % n)
        for movie in top_n_billed['M']:
            print ("- %s" % movie)
    if len(top_n_billed["F"]) == 0:
        print("No movies with top %d female billed!" % n)
    else:
        print("Movies with top %d female billed:" % n)
        for movie in top_n_billed["F"]:
            print ("- %s" % movie)


if __name__ == "__main__":
    data = DataLoader(verbose=False)

    print("EXERCISE 1")
    assign_genders(data)
    _print_gender_counts(data)
    print("----------------------------")

    print("EXERCISE 2")
    n = 10 # Feel free to change this number.
    top_n_billed = get_top_n_billed_by_gender(data, n)
    _print_top_n_billed(top_n_billed, n)
    print("----------------------------")
