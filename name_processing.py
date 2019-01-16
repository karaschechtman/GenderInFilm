import os

# Transforms a variant of a character name to its root.
def variant_to_root(var):
    var = var.lower()
    var = var.split(' (', 1)[0]  # e.g. lou (quietly) --> lou
    var = var.strip(':')  # carol: --> carol

    # handle voice-overs
    if '\'s voice' in var:  # e.g. cate's voice --> cate
        var = var.split('\'s', 1)[0]
    elif 's\' voice' in var:  # e.g. chris' voice --> chris
        var = var.split('\'', 1)[0]
    elif ' voice' in var or ' voice over' in var or ' voice-over' in var:
        var = var.split(' voice', 1)[0]
    return var

def get_imdb_char_names(cast):
    tuples = cast.strip('IMDB Cast: ').strip().split(', ')
    char_names = set()
    for t in tuples:
        char_name = t.split(' | ', 1)[0]
        char_names.add(char_name.lower())
    return char_names

# need to improve this method
def aligned(iname, sname):
    return sname in iname

def test_char_name_alignment(lines):
    cast = lines[7]
    i_char_names = get_imdb_char_names(cast)
    matched = 0
    missed = 0
    for line in lines[9:]:
        if line.startswith('C|'):
            var = line.strip('C|').strip().lower()
            root = variant_to_root(var)
            if any(aligned(icn, root) for icn in i_char_names):
                matched += 1
            else:
                missed += 1
    return matched, missed

# Results: Total Matched: 179952 / 0.7003. Total Missed: 77002 / 0.2997
def test_all_char_name_alignment():
    path_to_data = './data/data_loader_txt/'
    total_matched = 0
    total_missed = 0
    for fn in os.listdir(path_to_data):
        if fn.endswith('.txt'):
            with open(path_to_data + fn, 'r') as f:
                matched, missed = test_char_name_alignment(f.readlines())
                print('Matched: {}. Missed: {}'.format(matched, missed))
                total_matched += matched
                total_missed += missed
    total_lines = total_matched + total_missed
    print('Total Matched: {} / {}. Total Missed: {} / {}'.format(total_matched, round(total_matched/total_lines, 4), total_missed,

                                                                    round(total_missed/total_lines, 4)))
if __name__ == "__main__":
    test_all_char_name_alignment()