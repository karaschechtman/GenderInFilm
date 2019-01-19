import os

'''Contains scripts to match gender labels to scripts.'''

PATH_TO_DATA = './data/'
THRESHOLD = 5

from collections import defaultdict

import difflib

# ----------------------- GENERAL UTILITIES -----------------------
def _get_imdb_gender_mapping(cast):
    """
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

# --------------------------- ASSIGNMENT --------------------------

# TODO(karaschechtman): baseline of "better" alignments
# (assign alignment with highest quality measured by overlap)

def _hard_backtrack(script_to_imdb, assignments):
    """
    Recursive helper function for hard backtracking.
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
    ordered_inames = []
    for iname in script_to_imdb[sname]:
        num_occurences = sum([1 for s in script_to_imdb if iname in script_to_imdb[s]])
        ordered_inames.append((num_occurences, iname))
    ordered_inames.sort()

    # Try the assignment.
    for iname in ordered_inames:
        # Create the new script to IMDB mapping .
        new_script_to_imdb = script_to_imdb.copy()
        del new_script_to_imdb[sname]
        # Delete iname as a potential match.
        for s in new_script_to_imdb:
            if iname[1] in new_script_to_imdb[s]:
                new_script_to_imdb[s].remove(iname[1])
        assignments[sname] = iname[1]
        backtracked_assignments = _hard_backtrack(new_script_to_imdb, assignments)
        if backtracked_assignments != False:
            return backtracked_assignments
    return False

def hard_backtrack(lines, alignment_fn):
    """
    Match characters in the script to IMDB characters
    for any characters that have IMDB matches.

    Character assignment is formulated as a constraint
    satisfaction problem, with one script character starting
    with a number of potential IMDB matches that will
    be whittled down to one unique match.
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
    assignments_init = dict.fromkeys(script_to_imdb.keys())
    assignments = _hard_backtrack(script_to_imdb, assignments_init)
    if assignments:
        return assignments
    else:
        return False

def _soft_backtrack(script_to_imdb, assignments):
    """
    Recursive helper function for soft backtracking.
    """
    # Check completion condition.
    if not script_to_imdb:
        return assignments

    # Choose variable to assign according to MRV heuristic.
    sname = max(script_to_imdb, key=lambda k: len(script_to_imdb[k]))

    # Order potential assignments according to LCV heuristic.
    # This enforces a soft preference for matching snames
    # to unique inames (repeated iname assignment is not
    # expressly forbidden).
    ordered_inames = []
    for iname in script_to_imdb[sname]:
        num_occurences = sum([1 for s in script_to_imdb if iname in script_to_imdb[s]])
        ordered_inames.append((num_occurences, iname))
    ordered_inames.sort()

    # Try the assignment.
    for iname in ordered_inames:
        del script_to_imdb[sname]
        assignments[sname] = iname[1]
        backtracked_assignments = _soft_backtrack(script_to_imdb, assignments)
        if backtracked_assignments != False:
            return backtracked_assignments
    return False

def soft_backtrack(lines, alignment_fn):
    """
    Match characters in the script to IMDB characters
    for any characters that have IMDB matches.

    Character assignment is formulated as a constraint
    satisfaction problem, with one script character starting
    with a number of potential IMDB matches that will
    be whittled down to one match. This "backtracking" will
    never actually backtrack, since all the constraints
    are soft and approximated through heuristics.
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
    assignments_init = dict.fromkeys(script_to_imdb.keys())
    assignments = _soft_backtrack(script_to_imdb, assignments_init)
    if assignments:
        return assignments
    else:
        return False

# ---------------------------- TESTING ----------------------------
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

def test_alignment_coverage(alignment_fn):
    """
    Checks coverage for an alignment function.
    Provides two statistics
    1. Characters covered - a script character is covered by
    alignment if it matches at least one IMDB name.
    2. Lines with alignments - a line is covered by alignment
    if it is spoken by a character with an aligned name.
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

def test_assignment_coverage(assignment_fn, alignment_fn):
    """
    Tests coverage of assignments from alignments.
    Provides five statistics:
    1. Files with successful assignment - a file produces
    some assignment of names to IMDb characters. Failure
    happens if all possible assignments are inconsistent
    (according to the assignment criteria being used in the
    assignment_fn), or if there is no IMDB data to align.
    2. Number of characters successfully assigned - characters
    with an IMDb match. (TODO)
    3. Number of lines successfully assigned - lines spoken
    by characters with an IMDB match. (TODO)
    4. Number of characters successfully gendered -  characters
    with an IMDb match that has a gender. (TODO)
    5. Number of lines successfully gendered -  lines spoken
    by characters with an IMDb match that has a gender. (TODO)
    """
    total_success = 0
    total_failure = 0
    for fn in os.listdir(PATH_TO_DATA):
        if fn.endswith('.txt'):
            with open(PATH_TO_DATA + fn, 'r') as f:
                assignment = assignment_fn(f.readlines(), alignment_fn)
                if assignment:
                    total_success += 1
                else:
                    total_failure += 1
    total_attempts = total_success + total_failure
    # TODO: move file parsing logic to test function.
    print("ASSIGNMENT TEST: %s assignment with %s alignment" % (assignment_fn.__name__, alignment_fn.__name__))
    print("File assignment successes: {} / {}%  \
           File assignment failures: {} / {}%".format(total_success,
                                           round(total_success/total_attempts * 100, 2),
                                           total_failure,
                                           round(total_failure/total_attempts * 100, 2)))
    print('----------------------------')

if __name__ == "__main__":
    test_alignment_coverage(in_align)
    test_alignment_coverage(threshold_align)
    test_alignment_coverage(blended_align)
    test_assignment_coverage(soft_backtrack, in_align)
    test_assignment_coverage(soft_backtrack, threshold_align)
    test_assignment_coverage(soft_backtrack, blended_align)
    test_assignment_coverage(hard_backtrack, in_align)
    test_assignment_coverage(hard_backtrack, threshold_align)
    test_assignment_coverage(hard_backtrack, blended_align)
