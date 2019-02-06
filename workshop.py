from data_loader import DataLoader
from gender_predict import predict_gender


def assign_genders(data_loader):
    """
    INTRODUCTORY EXERCISE
    For every movie in the DataLoader, call predict_gender and
    assign the returned genders to the Character objects'
    gender fields.
    """

    return None # Delete this when you are done.

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
