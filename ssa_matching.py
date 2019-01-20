PATH_TO_SSA = './data/ssa_names_1880_2017/'
SSA_MIN = 1880
SSA_MAX = 2017
FEMALE_TITLES = {'ms', 'miss', 'mrs', 'mother', 'mom', 'momma', 'sister', 'aunt', 'grandma', 'grandmother',
                 'lady', 'mistress', 'duchess', 'madam', 'madame', 'princess', 'girl', 'woman'
                 'waitress'}
MALE_TITLES = {'mr', 'mister', 'father', 'dad', 'brother', 'uncle', 'grandpa', 'grandfather',
               'master', 'duke', 'prince', 'boy', 'man'}

# return dict: year -> list of name_scores
def make_ssa_dict():
    year_to_names = {}
    for fn in os.listdir(PATH_TO_SSA):
        if fn.startswith('yob'):
            year = fn.rsplit('.txt', 1)[0]
            year = year.split('yob', 1)[1]
            year = int(year)
            name_scores = get_name_scores(PATH_TO_SSA + fn)
            year_to_names[year] = name_scores
    return year_to_names

# return dict: name -> score, i.e. num_female / (num_male + num_female)
def get_name_scores(ssa_fn):
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

# fallback if IMDb is missing gender info for this character
def predict_gender(ssa_dict, char_name, movie_year=None, check_decade=True):
    char_name = char_name.replace('/', ' ')  # separate into different tokens
    toks = char_name.lower().split()
    # first check for obvious gendered titles
    for tok in toks:
        if tok in FEMALE_TITLES:
            return 1.0
        elif tok in MALE_TITLES:
            return 0.0
    # check token by token to see if there are matches with SSA name lists;
    # favor earlier tokens since name lists are of first names
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
            return sum_score / year_count
    return None

def test_gender_coverage(ssa_dict, lines):
    year = lines[2].strip('Year: ').strip()
    if year == 'None':
        year = None
    else:
        year = int(year)
    matched, missed = 0, 0
    already_matched = set()
    already_missed = set()
    for line in lines[9:]:
        if line.startswith('C|'):
            var = line.strip('C|').strip().lower()
            if var in already_matched:
                matched += 1
            elif var in already_missed:
                missed += 1
            else:
                root = variant_to_root(var)
                gen = predict_gender(ssa_dict, root, movie_year=year, check_decade=True)
                if gen is not None:
                    matched += 1
                    already_matched.add(var)
                else:
                    missed += 1
                    already_missed.add(var)
    return matched, missed

# Results wo decade constraint: Total Matched: 205441 / 0.7995. Total Missed: 51513 / 0.2005
# Result w decade constraint: Total Matched: 187315 / 0.729. Total Missed: 69639 / 0.271
def test_all_gender_coverage():
    ssa_dict = make_ssa_dict()
    total_matched = 0
    total_missed = 0
    for fn in os.listdir(PATH_TO_DATA):
        if fn.endswith('.txt'):
            with open(PATH_TO_DATA + fn, 'r') as f:
                lines = f.readlines()
                matched, missed = test_gender_coverage(ssa_dict, lines)
                print('Matched: {}. Missed: {}'.format(matched, missed))
                total_matched += matched
                total_missed += missed
    total_lines = total_matched + total_missed
    print('Total Matched: {} / {}. Total Missed: {} / {}'.format(total_matched, round(total_matched/total_lines, 4), total_missed,
                                                                 round(total_missed/total_lines, 4)))
