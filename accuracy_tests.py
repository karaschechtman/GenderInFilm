from data_loader import DataLoader
from imdb_matching import *
import numpy as np
from ssa_matching import *
from sklearn.metrics import accuracy_score

"""Testing gender prediction accuracy on gold labels."""

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

# ----------------------- TESTS -----------------------
def _test_assignment_acc_for_movie(gold_dict, movie, alignment_fn, assignment_fn):
    pred_dict = predict_gender_imdb(movie, alignment_fn, assignment_fn)
    ordered_snames = sorted(list(pred_dict.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
        pred_labels.append(pred_dict[sname])
        gold_labels.append(gold_dict[sname][0])
    if len(gold_labels) == 0:   # could not predict genders for any characters
        return None, 0
    acc = accuracy_score(gold_labels, pred_labels)
    return acc, len(gold_labels)

def test_assignment_acc_for_all_labeled_movies(data, alignment_fn, assignment_fn):
    print('IMDB ACCURACY TEST: alignment = {}, assignment = {}'.format(alignment_fn.__name__, assignment_fn.__name__))
    accs = []
    for fn in os.listdir(PATH_TO_GOLD_LABELS):
        if fn.endswith(' ALIGNED.txt') or fn.endswith(' GENDERED.txt'):
            if fn.endswith(' ALIGNED.txt'):
                gold_dict = parse_annotated_alignment_file(fn)
                title = fn.split(' ALIGNED.txt', 1)[0]
            else:
                gold_dict = parse_annotated_gendered_file(fn)
                title = fn.split(' GENDERED.txt', 1)[0]
            movie = data.get_movie(title)
            assert(movie is not None)
            acc, num_eval = _test_assignment_acc_for_movie(gold_dict, movie, alignment_fn, assignment_fn)
            if acc is None:
                print('Could not make successful gender alignments.')
            else:
                print('Movie: {}. Accuracy: {} ({} out of {} characters)'.format(title, round(acc, 4), num_eval, len(gold_dict)))
                accs.append(acc)
    print('Average accuracy:', np.mean(accs))
    print('----------------------------')

def _test_ssa_acc_for_movie(gold_dict, movie, ssa_dict, mode, check_decade):
    pred_dict = predict_gender_ssa(ssa_dict, movie, mode, check_decade)
    ordered_snames = sorted(list(gold_dict.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
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
    for fn in os.listdir(PATH_TO_GOLD_LABELS):
        if fn.endswith(' ALIGNED.txt') or fn.endswith(' GENDERED.txt'):
            if fn.endswith(' ALIGNED.txt'):
                gold_dict = parse_annotated_alignment_file(fn)
                title = fn.split(' ALIGNED.txt', 1)[0]
            else:
                gold_dict = parse_annotated_gendered_file(fn)
                title = fn.split(' GENDERED.txt', 1)[0]
            movie = data.get_movie(title)
            assert(movie is not None)
            acc, num_eval = _test_ssa_acc_for_movie(gold_dict, movie, ssa_dict, mode, check_decade)
            if acc is None:
                print('Could not make successful gender alignments.')
            else:
                print('Movie: {}. Accuracy: {} ({} out of {} characters)'.format(title, round(acc, 4), num_eval, len(gold_dict)))
                accs.append(acc)
    print('Average accuracy:', round(np.mean(accs), 4))
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

