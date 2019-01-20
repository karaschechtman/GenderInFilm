from character import Character
from collections import defaultdict
import difflib

'''Predict a movie's cast's gender labels from IMDb.'''

THRESHOLD = 5

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

def baseline_assign(script_to_imdb):
    """
    Baseline assignment function that assigns the IMDb
    character with the highest overlapping character count.
    """
    assignments = {}
    for sname in script_to_imdb:
        inames = script_to_imdb[sname]
        best_fit = 0
        for iname in inames:
            s = difflib.SequenceMatcher(None, sname, iname)
            match = s.find_longest_match(0, len(sname), 0, len(iname))
            if match.size >= best_fit:
                assignments[sname] = iname
                best_fit = match.size
    return assignments

def _hard_backtrack(script_to_imdb, assignments):
    """
    Recursive helper function for hard backtracking.
    """
    # Check completion condition.
    if not script_to_imdb:
        return assignments

    # Choose variable to assign according to MRV heuristic.
    sname = min(script_to_imdb, key=lambda k: len(script_to_imdb[k]))

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
    sname = min(script_to_imdb, key=lambda k: len(script_to_imdb[k]))

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

# ---------------------------- PREDICT ----------------------------
def predict_gender_imdb(movie, alignment_fn, assignment_fn):
    """
    Given a movie, a function to align IMDB data to the characters,
    and a function to choose from potential aligned names, predict
    the gender of characters. Returns a dictionary from character
    names to predicted genders.
    """
    script_to_imdb = defaultdict(list)
    for character in movie.characters.values():
        for iname in movie.imdb_cast:
            if alignment_fn(iname, character):
                script_to_imdb[character].append(iname)

    # Match genders.
    assignment = assignment_fn(script_to_imdb)
    gender_alignments = {}
    if assignment:
        for sname in assignment:
            gender = movie.imdb_cast[assignment[sname]][1]
            if gender == 'M' or gender == 'F':
                gender_alignments[sname] = gender
    return gender_alignments
