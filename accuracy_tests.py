from data_loader import DataLoader
from imdb_matching import *
from numpy import mean
from ssa_matching import *
from sklearn.metrics import accuracy_score, confusion_matrix

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
    ordered_snames = sorted(list(gold_dict.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
        gold_labels.append(gold_dict[sname][0])
        if sname in pred_dict:
            pred_labels.append(pred_dict[sname])
        else:
            pred_labels.append('UNK')
    acc = accuracy_score(gold_labels, pred_labels)
    return acc

def test_assignment_acc_for_all_labeled_movies(data, alignment_fn, assignment_fn):
    print('ACCURACY TEST: alignment = {}, assignment = {}'.format(assignment_fn.__name__, alignment_fn.__name__))
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
            acc = _test_assignment_acc_for_movie(gold_dict, movie, alignment_fn, assignment_fn)
            print(title, acc)
            accs.append(acc)
    print('Average accuracy:', mean(accs))
    print('----------------------------')

def _test_ssa_acc_for_movie(gold_dict, movie, ssa_dict, mode, check_decade):
    pred_dict = predict_gender_ssa(ssa_dict, movie, mode, check_decade)
    ordered_snames = sorted(list(gold_dict.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
        gold_labels.append(gold_dict[sname][0])
        pred_labels.append(pred_dict[sname])
    acc = accuracy_score(gold_labels, pred_labels)
    return acc

def test_ssa_acc_for_all_labeled_movies(data, mode, check_decade):
    ssa_dict = make_ssa_dict()
    print('ACCURACY TEST: mode = {}, decade = {}'.format(mode, check_decade))
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
            acc = _test_ssa_acc_for_movie(gold_dict, movie, ssa_dict, mode, check_decade)
            print(title, acc)
            accs.append(acc)
    print('Average accuracy:', mean(accs))
    print('----------------------------')

if __name__ == "__main__":
    data = DataLoader(verbose=False)
    # test_ssa_acc_for_all_labeled_movies(data, mode='soft', check_decade='False')
    # test_ssa_acc_for_all_labeled_movies(data, mode='soft', check_decade='True')
    # test_ssa_acc_for_all_labeled_movies(data, mode='hard', check_decade='False')
    # test_ssa_acc_for_all_labeled_movies(data, mode='hard', check_decade='True')
    test_assignment_acc_for_all_labeled_movies(data, in_align, soft_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, threshold_align, soft_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, blended_align, soft_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, in_align, hard_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, threshold_align, hard_backtrack)
    test_assignment_acc_for_all_labeled_movies(data, blended_align, hard_backtrack)

