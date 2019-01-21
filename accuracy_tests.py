from data_loader import DataLoader
from imdb_matching import *
import numpy as np
from ssa_matching import *
from sklearn.metrics import accuracy_score

"""Testing gender prediction accuracy on gold labels."""

VERBOSE = False

# ----------------------- GENERAL UTILITIES -----------------------
PATH_TO_GOLD_LABELS = './data/gold_labels/'

def gender_to_idx(gender):
    if gender == 'UNK':
        return 0
    if gender == 'F':
        return 1
    if gender == 'M':
        return 2
    if gender == 'BOTH':
        return 3
    return -1

def parse_annotated_alignment_file(filename):
    with open(PATH_TO_GOLD_LABELS + filename, 'r') as f:
        char_dict = {}
        for line in f.readlines():
            sname_gen, alignment = line.split(' -> ', 1)
            sname, gen = sname_gen.split(' (', 1)
            gen = gen.rstrip(')')
            alignment = alignment.strip()
            if alignment.startswith('POSSIBILITIES '):
                certain = False
                inames = alignment.strip('POSSIBILITIES ').split(', ')
            elif alignment == 'N/A':
                certain = True
                inames = None
            elif ', ' in alignment:
                certain = True
                inames = alignment.split(', ')
            else:
                certain = True
                inames = alignment
            char_dict[sname] = (gen, inames, certain)
        return char_dict

def parse_annotated_gendered_file(filename):
    with open(PATH_TO_GOLD_LABELS + filename, 'r') as f:
        char_dict = {}
        for line in f.readlines():
            sname, gen = line.strip().split(' (', 1)
            gen = gen.rstrip(')')
            char_dict[sname] = gen
        return char_dict

def merge_dict(ssa_pred_dict, imdb_pred_dict, ssa_trumps=True):
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

# ----------------------- TESTS -----------------------
def _test_assignment_acc_for_movie(gold_dict, movie, alignment_fn, assignment_fn):
    pred_dict = predict_gender_imdb(movie, alignment_fn, assignment_fn)
    ordered_snames = sorted(list(pred_dict.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
        if sname in gold_dict:
            pred_labels.append(pred_dict[sname])
            gold_labels.append(gold_dict[sname][0])
    if len(gold_labels) == 0:   # could not predict genders for any characters
        return None, 0
    acc = accuracy_score(gold_labels, pred_labels)
    return acc, len(gold_labels)

def test_assignment_acc_for_all_labeled_movies(data, alignment_fn, assignment_fn):
    print('IMDB ACCURACY TEST: alignment = {}, assignment = {}'.format(alignment_fn.__name__, assignment_fn.__name__))
    accs = []
    total_num_covered = 0
    total_num_chars = 0
    for fn in os.listdir(PATH_TO_GOLD_LABELS):
        if fn.endswith(' ALIGNED.txt') or fn.endswith(' GENDERED.txt'):
            if fn.endswith(' ALIGNED.txt'):
                gold_dict = parse_annotated_alignment_file(fn)
                title = fn.split(' ALIGNED.txt', 1)[0].replace('_', '\'')
            else:
                gold_dict = parse_annotated_gendered_file(fn)
                title = fn.split(' GENDERED.txt', 1)[0].replace('_', '\'')
            num_chars = len(gold_dict)
            total_num_chars += num_chars
            movie = data.get_movie(title)
            assert(movie is not None)
            acc, num_covered = _test_assignment_acc_for_movie(gold_dict, movie, alignment_fn, assignment_fn)
            if acc is None:
                if VERBOSE:
                    print('Movie: {}. Could not make successful gender alignments.'.format(title))
            else:
                if VERBOSE:
                    print('Movie: {}. Accuracy: {} ({} out of {} characters)'.format(title, round(acc, 4), num_covered, num_chars))
                accs.append(acc)
                total_num_covered += num_covered
    print('Average accuracy: {}. Characters covered: {} / {}%'.format(round(np.mean(accs), 4),
                                                                     total_num_covered,
                                                                     round(total_num_covered/total_num_chars * 100, 2)))
    print('----------------------------')

def _test_ssa_acc_for_movie(gold_dict, movie, ssa_dict, mode, check_decade):
    pred_dict = predict_gender_ssa(ssa_dict, movie, mode, check_decade)
    ordered_snames = sorted(list(pred_dict.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
        if sname in gold_dict:
            if pred_dict[sname] == 'M' or pred_dict[sname] == 'F':
                gold_labels.append(gold_dict[sname][0])
                pred_labels.append(pred_dict[sname])
    if len(gold_labels) == 0:   # could not predict genders for any characters
        return None, 0
    acc = accuracy_score(gold_labels, pred_labels)
    return acc, len(gold_labels)

def test_ssa_acc_for_all_labeled_movies(data, mode, check_decade):
    ssa_dict = make_ssa_dict()
    print('SSA ACCURACY TEST: mode = {}, decade = {}'.format(mode, check_decade))
    accs = []
    total_num_covered = 0
    total_num_chars = 0
    for fn in os.listdir(PATH_TO_GOLD_LABELS):
        if fn.endswith(' ALIGNED.txt') or fn.endswith(' GENDERED.txt'):
            if fn.endswith(' ALIGNED.txt'):
                gold_dict = parse_annotated_alignment_file(fn)
                title = fn.split(' ALIGNED.txt', 1)[0].replace('_', '\'')
            else:
                gold_dict = parse_annotated_gendered_file(fn)
                title = fn.split(' GENDERED.txt', 1)[0].replace('_', '\'')
            num_chars = len(gold_dict)
            total_num_chars += num_chars
            movie = data.get_movie(title)
            assert(movie is not None)
            acc, num_covered = _test_ssa_acc_for_movie(gold_dict, movie, ssa_dict, mode, check_decade)
            if acc is None:
                if VERBOSE:
                    print('Movie: {}. Could not make successful gender alignments.'.format(title))
            else:
                if VERBOSE:
                    print('Movie: {}. Accuracy: {} ({} out of {} characters)'.format(title, round(acc, 4), total_num_covered, num_chars))
                accs.append(acc)
                total_num_covered += num_covered
    print('Average accuracy: {}. Characters covered: {} / {}%'.format(round(np.mean(accs), 4),
                                                                     total_num_covered,
                                                                     round(total_num_covered/total_num_chars * 100, 2)))
    print('----------------------------')

def _test_hybrid_acc_for_movie(gold_dict, movie, ssa_dict, ssa_trump):
    imdb_pred_dict = predict_gender_imdb(movie, alignment_fn=in_align, assignment_fn=soft_backtrack)
    ssa_pred_dict = predict_gender_ssa(ssa_dict, movie, mode='hard', check_decade=True)
    pred_dict = merge_dict(ssa_pred_dict, imdb_pred_dict, ssa_trump)
    ordered_snames = sorted(list(pred_dict.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
        if sname in gold_dict:
            if pred_dict[sname] == 'M' or pred_dict[sname] == 'F':
                gold_labels.append(gold_dict[sname][0])
                pred_labels.append(pred_dict[sname])
    if len(gold_labels) == 0:   # could not predict genders for any characters
        return None, 0
    acc = accuracy_score(gold_labels, pred_labels)
    return acc, len(gold_labels)

def test_hybrid_acc_for_all_labeled_movies(data, ssa_trump):
    ssa_dict = make_ssa_dict()
    print('HYBRID ACCURACY TEST: ssa_trump = {}'.format(ssa_trump))
    accs = []
    total_num_covered = 0
    total_num_chars = 0
    for fn in os.listdir(PATH_TO_GOLD_LABELS):
        if fn.endswith(' ALIGNED.txt') or fn.endswith(' GENDERED.txt'):
            if fn.endswith(' ALIGNED.txt'):
                gold_dict = parse_annotated_alignment_file(fn)
                title = fn.split(' ALIGNED.txt', 1)[0].replace('_', '\'')
            else:
                gold_dict = parse_annotated_gendered_file(fn)
                title = fn.split(' GENDERED.txt', 1)[0].replace('_', '\'')
            num_chars = len(gold_dict)
            total_num_chars += num_chars
            movie = data.get_movie(title)
            assert(movie is not None)
            acc, num_covered = _test_hybrid_acc_for_movie(gold_dict, movie, ssa_dict, ssa_trump)
            if acc is None:
                if VERBOSE:
                    print('Movie: {}. Could not make successful gender alignments.'.format(title))
            else:
                if VERBOSE:
                    print('Movie: {}. Accuracy: {} ({} out of {} characters)'.format(title, round(acc, 4), num_covered, num_chars))
                accs.append(acc)
                total_num_covered += num_covered
    print('Average accuracy: {}. Characters covered: {} / {}%'.format(round(np.mean(accs), 4),
                                                                     total_num_covered,
                                                                     round(total_num_covered/total_num_chars * 100, 2)))
    print('----------------------------')

if __name__ == "__main__":
    data = DataLoader(verbose=False)
    test_ssa_acc_for_all_labeled_movies(data, mode='soft', check_decade='False')
    test_ssa_acc_for_all_labeled_movies(data, mode='soft', check_decade='True')
    test_ssa_acc_for_all_labeled_movies(data, mode='hard', check_decade='False')
    test_ssa_acc_for_all_labeled_movies(data, mode='hard', check_decade='True')
    test_assignment_acc_for_all_labeled_movies(data, in_align, soft_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, threshold_align, soft_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, blended_align, soft_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, in_align, hard_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, threshold_align, hard_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, blended_align, hard_backtrack)
    test_hybrid_acc_for_all_labeled_movies(data, ssa_trump=True)
    test_hybrid_acc_for_all_labeled_movies(data, ssa_trump=False)


