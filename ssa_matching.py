__author__ = 'Serina Chang <sc3003@columbia.edu>'
__date__ = 'Jan 20, 2019'

import os

'''SSA-based and rule-based gender prediction for character names.'''

# ----------------------- GENERAL UTILITIES -----------------------
def char_name_to_tokens(char_name):
    char_name = char_name.replace('/', ' ')
    return char_name.lower().split()

# --------------------- RULE-BASED PREDICTION ---------------------
FEMALE_TERMS = {'ms', 'miss', 'mrs', 'mother', 'mom', 'momma', 'sister',
                'aunt', 'grandma', 'grandmother', 'lady', 'mistress',
                'madam', 'madame', 'princess', 'girl', 'woman'
                'waitress', 'female'}
MALE_TERMS = {'mr', 'mister', 'father', 'dad', 'brother', 'uncle',
              'grandpa', 'grandfather', 'master', 'prince',
              'boy', 'man', 'male'}

def score_gender_rb(char_name):
    """
    The simplest gender scorer: checks for gendered terms in the
    character name, such as 'girl' and 'boy'.
    """
    toks = char_name_to_tokens(char_name)
    for tok in toks:
        if tok in FEMALE_TERMS:
            return 1.0
        elif tok in MALE_TERMS:
            return 0.0
    return None

# --------------------- SSA-BASED PREDICTION ---------------------
PATH_TO_SSA = './data/ssa_names_1880_2017/'
SSA_MIN = 1880
SSA_MAX = 2017
HARD_F_CUTOFF = .9
HARD_M_CUTOFF = .1
SOFT_F_CUTOFF = .5
SOFT_M_CUTOFF = .5

def make_ssa_dict():
    """
    Makes a dictionary of year mapped to SSA name_scores.
    """
    year_to_names = {}
    for fn in os.listdir(PATH_TO_SSA):
        if fn.startswith('yob'):
            year = fn.rsplit('.txt', 1)[0]
            year = year.split('yob', 1)[1]
            year = int(year)
            name_scores = get_name_scores(PATH_TO_SSA + fn)
            year_to_names[year] = name_scores
    return year_to_names

def get_name_scores(ssa_fn):
    """
    Makes SSA name_scores, i.e. a dictionary of name mapped to score, where score
    equals the number of times that name was assigned to a female baby divided
    by the total number of times that name was assigned to a baby of either
    gender.
    """
    name_to_counts = {}
    with open(ssa_fn, 'r') as f:
        content = f.readlines()
        for line in content:
            line = line.strip()
            name, gender, count = line.split(',')
            name = name.lower()
            count = int(count)
            if name not in name_to_counts:
                name_to_counts[name] = [0, 0]
            if gender == 'F':
                name_to_counts[name][0] += count
            else:
                name_to_counts[name][1] += count
    for name, counts in name_to_counts.items():
        score = counts[0]/sum(counts)
        name_to_counts[name] = score
    return name_to_counts

def score_gender_ssa(ssa_dict, char_name, movie_year=None, check_decade=True):
    """
    Scores a character's gender based on SSA name_scores (after trying rule-based.
    If check_decade is True, only the years in the decade preceding the movie are
    checked for name_scores; otherwise, all years are checked. After collecting all
    name_scores for this name, the name_scores are averaged.
    """
    rb_pred = score_gender_rb(char_name)
    if rb_pred is not None:
        return rb_pred
    toks = char_name_to_tokens(char_name)
    for tok in toks:
        sum_score = 0
        year_count = 0
        if check_decade and movie_year is not None:
            year_range = range(movie_year-9, movie_year+1)
        else:
            year_range = range(SSA_MIN, SSA_MAX+1)
        for year in year_range:
            if year in ssa_dict and tok in ssa_dict[year]:
                sum_score += ssa_dict[year][tok]
                year_count += 1
        if year_count > 0:
            print(tok)
            return sum_score / year_count
    return None

def score_to_category(score, mode):
    if score is None:
        return 'UNK'
    if mode == 'hard' and score > HARD_F_CUTOFF:
        return 'F'
    if mode == 'hard' and score < HARD_M_CUTOFF:
        return 'M'
    if mode == 'soft' and score > SOFT_F_CUTOFF:
        return 'F'
    if mode == 'soft' and score < SOFT_M_CUTOFF:
        return 'M'
    return 'UNK'

def predict_gender_ssa(ssa_dict, movie, mode, check_decade=True):
    """
    Predicts gender based on gender score. The modes, 'hard' or 'soft', determine the score cutoff
    for each gender.
    """
    assert(mode == 'hard' or mode == 'soft')
    gender_alignments = {}
    year = movie.year
    for character in movie.characters.values():
        sname = character.name
        gen = 'UNK'
        if ' and ' in sname:
            individual_names = sname.split(' and ')
            categories = []
            for name in individual_names:
                score = score_gender_ssa(ssa_dict, name, movie_year=year, check_decade=check_decade)
                categories.append(score_to_category(score, mode))
            if 'UNK' not in categories:
                if 'F' in categories and 'M' not in categories:
                    gen = 'F'
                elif 'M' in categories and 'F' not in categories:
                    gen = 'M'
                else:
                    gen = 'BOTH'
        else:
            score = score_gender_ssa(ssa_dict, sname, movie_year=year, check_decade=check_decade)
            gen = score_to_category(score, mode)
        gender_alignments[sname] = gen
    return gender_alignments

if __name__ == "__main__":
    ssa_dict = make_ssa_dict()
    char_name = 'whitney james'
    print(score_gender_ssa(make_ssa_dict(), char_name, movie_year=1988, check_decade=True))