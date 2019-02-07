from gender.imdb_matching import *
from gender.ssa_matching import *

SSA_DICT = make_ssa_dict()

def get_movie_genders_dict(movie):
    """
    Given a movie object, predict the gender of all characters.
    Returns a dictionary matching from character names to genders.
    If a charater's gender cannot be assigned with
    confidence, the character name will not appear in the dictionary.
    """
    imdb_pred_dict = predict_gender_imdb(movie, alignment_fn=in_align, assignment_fn=soft_backtrack)
    ssa_pred_dict = predict_gender_ssa(SSA_DICT, movie, mode='hard', check_decade=True)
    pred_dict = _merge_dict(ssa_pred_dict, imdb_pred_dict, True)
    ordered_snames = sorted(list(pred_dict.keys()))
    return pred_dict

def _merge_dict(ssa_pred_dict, imdb_pred_dict, ssa_trumps=True):
    ssa_pred_names = set()
    for sname, gen in ssa_pred_dict.items():
        if gen == 'M' or gen == 'F':
            ssa_pred_names.add(sname)
    imdb_pred_names = set()
    for sname, gen in imdb_pred_dict.items():
        if gen == 'M' or gen == 'F':
            imdb_pred_names.add(sname)
    merged_dict = {}
    for sname in set(ssa_pred_names).union(imdb_pred_names):
        if sname in ssa_pred_names and sname not in imdb_pred_names:
            merged_dict[sname] = ssa_pred_dict[sname]
        elif sname not in ssa_pred_names and sname in imdb_pred_names:
            merged_dict[sname] = imdb_pred_dict[sname]
        elif sname in ssa_pred_names and sname in imdb_pred_names:
            if ssa_trumps:
                merged_dict[sname] = ssa_pred_dict[sname]
            else:
                merged_dict[sname] = imdb_pred_dict[sname]
    return merged_dict
