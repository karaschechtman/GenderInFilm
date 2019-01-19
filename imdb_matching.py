import os

'''Contains scripts to match gender labels to scripts.'''

PATH_TO_DATA = './data/'
THRESHOLD = 5

from collections import defaultdict

import difflib

# ----------------------- GENERAL UTILITIES -----------------------
def _get_imdb_gender_mapping(cast):
    """
    Helper for test_alignment_coverage and test_assignment_coverage.
    Processes IMDB character data from file and makes a dictionary
    mapping from their names to the gender of the actor that
    portrays them.
    """
    cast_list = cast.strip('IMDB Cast: ').strip().split(', ')
    char_names = {}
    for c in cast_list:
        char_to_actor = c.split(' | ', 1)
        char_name = char_to_actor[0].lower()
        gender = char_to_actor[1].split('(')[-1].strip(')')
        char_names[char_name] = gender
    return char_names


# --------------------------- ALIGNMENT ---------------------------
def in_align(iname, sname):
    """
    Test if two names are aligned to each other by
    checking inclusion. Baseline.
    """
    return sname in iname

def threshold_align(iname, sname, threshold=THRESHOLD):
    """
    Test if two names are aligned to each other. Names
    count as aligned if they share at least as many characters
    as specified in the threshold.
    """
    s = difflib.SequenceMatcher(None, sname, iname)
    match = s.find_longest_match(0, len(sname), 0, len(iname))
    if match.size >= threshold:
        return True
    return False

def blended_align(iname, sname, threshold=THRESHOLD):
    """
    Inclusion test with a fallback to character overlap.
    """
    if sname in iname:
        return True
    s = difflib.SequenceMatcher(None, sname, iname)
    match = s.find_longest_match(0, len(sname), 0, len(iname))
    if match.size >= threshold:
        return True
    return False

def _count_matches_per_script(lines, alignment_fn):
    """
    Helper for test_alignment_coverage to count matches
    in an individual script.
    """
    cast = lines[7]
    i_char_mapping = _get_imdb_gender_mapping(cast)
    chars_matched = 0
    chars_missed = 0
    lines_matched = 0
    lines_missed = 0

    for line in lines[9:]:
        char_data = line.split(':')
        sname = char_data[0]
        if any([alignment_fn(iname, sname) for iname in i_char_mapping]):
            chars_matched += 1
            lines_matched += len(char_data[1].split(', '))
        else:
            chars_missed += 1
            lines_missed += len(char_data[1].split(', '))

    return chars_matched, chars_missed, lines_matched, lines_missed

def test_alignment_coverage(alignment_fn, verbose=False):
    """
    Checks coverage for an alignment function - whether
    each name in the script is matched to at least one
    other name by alignment_fn, and how many lines that
    coverage represents.
    """
    total_chars_matched = 0
    total_lines_matched = 0
    total_chars_missed = 0
    total_lines_missed = 0
    for fn in os.listdir(PATH_TO_DATA):
        total_num_files = 0
        if fn.endswith('.txt'):
            with open(PATH_TO_DATA + fn, 'r') as f:
                chars_matched, chars_missed, lines_matched, lines_missed = (
                    _count_matches_per_script(f.readlines(), alignment_fn))
                if verbose:
                    print('Matched: {}. Missed: {}'.format(matched, missed))
                total_chars_matched += chars_matched
                total_chars_missed += chars_missed
                total_lines_matched += lines_matched
                total_lines_missed += lines_missed

    total_chars = total_chars_matched + total_chars_missed
    total_lines = total_lines_matched + total_lines_missed

    print('ALIGNMENT TEST: %s' % (alignment_fn.__name__))
    print('Total Characters Covered: {} / {}% \
    Total Characters Missed: {} / {}%' .format(total_chars_matched,
                                              round(total_chars_matched/total_chars * 100, 2),
                                              total_chars_missed,
                                              round(total_chars_missed/total_chars * 100, 2)))
    print('Total Lines Covered: {} / {}% \
    Total Lines Missed: {} / {}%' .format(total_lines_matched,
                                              round(total_lines_matched/total_lines * 100, 2),
                                              total_lines_missed,
                                              round(total_lines_missed/total_lines * 100, 2)))
    print('----------------------------')

# --------------------------- ASSIGNMENT --------------------------
def _backtrack(script_to_imdb, assignments):
    """
    Recursive helper function for backtracking.
    """
    # Check completion condition.
    if not script_to_imdb:
        return assignments

    # Choose variable to assign according to MRV heuristic.
    sname = max(script_to_imdb, key=lambda k: len(script_to_imdb[k]))

    # Check failure condition.
    if len(script_to_imdb[sname]) == 0:
        return False

    # Order potential assignments according to LCV heuristic.
    # This enforces a soft preference for matching snames
    # to unique inames (which is not expressly forbidden).
    ordered_inames = []
    for iname in script_to_imdb[sname]:
        num_occurences = sum([1 for s in script_to_imdb if iname in script_to_imdb[s]])
        ordered_inames.append((num_occurences, iname))
    ordered_inames.sort()

    # Try the assignment.
    for iname in ordered_inames:
        del script_to_imdb[sname]
        assignments[sname] = iname
        backtracked_assignments = _backtrack(script_to_imdb, assignments)
        if backtracked_assignments != False:
            return backtracked_assignments
    return False

def backtrack(lines, alignment_fn):
    """
    Match characters in the script to IMDB characters
    using backtracking for any characters that have IMDB
    matches.

    Character assignment is formulated as a constraint
    satisfaction problem, with one script character starting
    with a number of potential IMDB matches that will
    be whittled down to one match.
    """
    cast = lines[7]
    inames = _get_imdb_gender_mapping(lines[7])
    script_to_imdb = defaultdict(list)

    # Align script characters with IMDB matches to possible
    # IMDB characters.
    for line in lines[9:]:
        sname = line.split(':')[0]
        for iname in inames:
            if alignment_fn(iname, sname):
                script_to_imdb[sname].append(iname)

    # Run CSP to match characters to names.
    assignments = dict.fromkeys(script_to_imdb.keys())
    if _backtrack(script_to_imdb, assignments):
        return assignments
    else:
        return False

def test_assignment_coverage(assignment_fn, alignment_fn, verbose=False):
    total_success = 0
    total_failure = 0
    for fn in os.listdir(PATH_TO_DATA):
        if fn.endswith('.txt'):
            with open(PATH_TO_DATA + fn, 'r') as f:
                assignment = assignment_fn(f.readlines(), alignment_fn)
                if assignment:
                    if verbose:
                        print(assignment)
                    total_success += 1
                else:
                    total_failure += 1
    total_attempts = total_success + total_failure
    print("ASSIGNMENT TEST: %s assignment with %s alignment" % (assignment_fn.__name__, alignment_fn.__name__))
    print("Script assignment successes: {} / {}%  \
           Script assignment failures: {} / {}%".format(total_success,
                                           round(total_success/total_attempts * 100, 2),
                                           total_failure,
                                           round(total_failure/total_attempts * 100, 2)))
    print('----------------------------')

if __name__ == "__main__":
    test_alignment_coverage(in_align)
    test_alignment_coverage(threshold_align)
    test_alignment_coverage(blended_align)
    test_assignment_coverage(backtrack, in_align)
    test_assignment_coverage(backtrack, threshold_align)
    test_assignment_coverage(backtrack, blended_align)
