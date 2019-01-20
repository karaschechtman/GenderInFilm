import os

'''Contains scripts to match gender labels to scripts.'''

THRESHOLD = 5

from character import Character
from collections import defaultdict
from data_loader import DataLoader

import difflib

# TODO(karaschechtman): rewrite class using data_loader.

# ----------------------- GENERAL UTILITIES -----------------------
def _get_imdb_names(imdb_cast):
    """
    Processes IMDB cahracter data from file and makes a list
    of their names.
    """
    return [c[0].lower() for c in imdb_cast]

def _get_imdb_gender_mapping(imdb_cast):
    """
    Processes IMDB character data from file and makes a dictionary
    mapping from their names to the gender of the actor that
    portrays them.
    """
    char_names = {}
    for c in imdb_cast:
        char_name = c[0].lower()
        gender = c[1].split('(')[-1].strip(')')
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

def hard_backtrack(script_to_imdb):
    """
    Match characters in the script to IMDB characters
    for any characters that have IMDB matches.

    Character assignment is formulated as a constraint
    satisfaction problem, with one script character starting
    with a number of potential IMDB matches that will
    be whittled down to one unique match.
    """
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

def soft_backtrack(script_to_imdb):
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
    assignments_init = dict.fromkeys(script_to_imdb.keys())
    assignments = _soft_backtrack(script_to_imdb, assignments_init)
    if assignments:
        return assignments
    else:
        return False

# ---------------------------- SIMPLE RUN ----------------------------
def imdb_gender_predict(movie, alignment_fn, assignment_fn):
    """
    Given a movie, a function to align IMDB data to the characters,
    and a function to choose from potential aligned names, predict
    the gender of characters. Returns a dictionary from character
    names to predicted genders.
    """
    inames = _get_imdb_gender_mapping(movie.imdb_cast)
    script_to_imdb = defaultdict(list)
    for character in movie.characters:
        for iname in inames:
            if alignment_fn(iname, character.name):
                script_to_imdb[sname].append(iname)

    # Match genders.
    assignment = assignment_fn(script_to_imdb)
    gender_alignments = {}
    if assignment:
        for sname in assignment:
            gender = inames[assignment[sname]]
            if gender == 'M' or gender == 'F':
                gender_alignments[sname] = gender
    return gender_alignments

# ---------------------------- TESTING ----------------------------
def _test_alignment_coverage(movie, alignment_fn):
    """
    Helper for test_alignment_coverage to count matches
    in an individual script.
    """
    inames = _get_imdb_names(movie.imdb_cast)
    chars_matched = 0
    chars_missed = 0
    lines_matched = 0
    lines_missed = 0

    for character in movie.characters:
        if any([alignment_fn(iname, character.name) for iname in inames]):
            chars_matched += 1
            lines_matched += len(character.line_data)
        else:
            chars_missed += 1
            lines_missed += len(character.line_data)

    return chars_matched, chars_missed, lines_matched, lines_missed

def test_all_alignment_coverage(data, alignment_fn):
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
    for movie in data.movies:
        chars_matched, chars_missed, lines_matched, lines_missed = (
                    _test_alignment_coverage(movie, alignment_fn))
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

def _test_assignment_coverage(movie, alignment_fn, assignment_fn):
    success = 0
    failure = 0
    chars_matched = 0
    chars_missed = 0
    lines_matched = 0
    lines_missed = 0
    chars_gendered = 0

    inames = _get_imdb_gender_mapping(movie.imdb_cast)
    script_to_imdb = defaultdict(list)
    aligned_char_count = 0
    aligned_line_count = 0
    # Align script characters to possible IMDb characters.
    for character in movie.characters:
        for iname in inames:
            if alignment_fn(iname, character.name):
                script_to_imdb[character.name].append(iname)
        if character.name not in script_to_imdb.keys():
            chars_missed += 1 # Record lines and character as unmatched.
            lines_missed += len(character.line_data)
        else:
            aligned_line_count += len(character.line_data) # Store for later processing.
            aligned_char_count += 1

    # Check final assignments and calculate final numbers.
    assignment = assignment_fn(script_to_imdb)
    if assignment:
        for sname in assignment:
            gender = inames[assignment[sname]]
            if gender == 'M' or gender == 'F':
                chars_gendered += 1
        success += 1
        chars_matched += aligned_char_count
        lines_matched += aligned_line_count

    else:
        failure += 1
        chars_missed += aligned_char_count
        lines_missed += aligned_line_count

    return success, failure, chars_matched, chars_missed, \
           lines_matched, lines_missed, chars_gendered

def test_all_assignment_coverage(data, alignment_fn, assignment_fn):
    """
    Tests coverage of assignments from alignments.
    Provides four statistics:
    1. Files with successful assignment - a file produces
    some assignment of names to IMDb characters. Failure
    happens if all possible assignments are inconsistent
    (according to the assignment criteria being used in the
    assignment_fn), or if there is no IMDB data to align.
    2. Number of characters successfully assigned - characters
    with an IMDb match.
    3. Number of lines successfully assigned - lines spoken
    by characters with an IMDB match.
    4. Number of characters successfully gendered -  characters
    with an IMDb match that has a gender.
    """
    total_success = 0
    total_failure = 0
    total_chars_matched = 0
    total_chars_missed = 0
    total_lines_matched = 0
    total_lines_missed = 0
    total_chars_gendered = 0

    for movie in data.movies:
        success, failure, chars_matched, chars_missed, lines_matched, lines_missed, chars_gendered = (
                    _test_assignment_coverage(movie, alignment_fn, assignment_fn))
        total_success += success
        total_failure += failure
        total_chars_matched += chars_matched
        total_chars_missed += chars_missed
        total_lines_matched += lines_matched
        total_lines_missed += lines_missed
        total_chars_gendered += chars_gendered

    total_attempts = total_success + total_failure
    total_chars = total_chars_matched + total_chars_missed
    total_lines = total_lines_matched + total_lines_missed

    print('ASSIGNMENT TEST: %s assignment with %s alignment' % (assignment_fn.__name__, alignment_fn.__name__))
    print('File assignment successes: {} / {}%  \
           File assignment failures: {} / {}%'.format(total_success,
                                                      round(total_success/total_attempts * 100, 2),
                                                      total_failure,
                                                      round(total_failure/total_attempts * 100, 2)))
    print('Characters matched: {} / {}%  \
           Characters missed: {} / {}%'.format(total_chars_matched,
                                               round(total_chars_matched/total_chars * 100, 2),
                                               total_chars_missed,
                                               round(total_chars_missed/total_chars * 100, 2)))

    print('Lines matched: {} / {}%  \
           Lines missed: {} / {}%'.format(total_lines_matched,
                                          round(total_lines_matched/total_lines * 100, 2),
                                          total_chars_missed,
                                          round(total_lines_missed/total_lines * 100,2)))

    print('Characters gendered: {} / {}%  \
           Characters not gendered: {} / {}%'.format(total_chars_gendered,
                                                     round(total_chars_gendered/total_chars * 100, 2),
                                                     total_chars - total_chars_gendered,
                                                     round((total_chars - total_chars_gendered)/total_chars * 100, 2)))

    print('----------------------------')

if __name__ == "__main__":
    data = DataLoader()
    test_all_alignment_coverage(data, in_align)
    test_all_alignment_coverage(data, threshold_align)
    test_all_alignment_coverage(data, blended_align)
    test_all_assignment_coverage(data, in_align, soft_backtrack)
    test_all_assignment_coverage(data, threshold_align, soft_backtrack)
    test_all_assignment_coverage(data, blended_align, soft_backtrack)
    test_all_assignment_coverage(data, in_align, hard_backtrack)
    test_all_assignment_coverage(data, threshold_align, hard_backtrack)
    test_all_assignment_coverage(data, blended_align, hard_backtrack)
