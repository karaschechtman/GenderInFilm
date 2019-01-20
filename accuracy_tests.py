from data_loader import DataLoader
from imdb_matching import *
from ssa_matching import *
from sklearn.metrics import accuracy_score, confusion_matrix

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

def parse_annotation_file(filename):
    char_dict = {}
    with open(PATH_TO_GOLD_LABELS + filename) as f:
        for line in f.readlines():
            sname_gen, alignment = line.split(' -> ')
            sname, gen = sname_gen.split(' (')
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

def eval(gold, pred):
    ordered_snames = sorted(list(gold.keys()))
    gold_labels = []
    pred_labels = []
    for sname in ordered_snames:
        gold_labels.append(gold[sname][0])
        pred_labels.append(pred[sname])
        if gold_labels[-1] == 'M' and pred_labels[-1] == 'F':
            print(sname, gold_labels[-1], pred_labels[-1])
        elif gold_labels[-1] == 'F' and pred_labels[-1] == 'M':
            print(sname, gold_labels[-1], pred_labels[-1])
    return accuracy_score(gold_labels, pred_labels), confusion_matrix(gold_labels, pred_labels)

if __name__ == "__main__":
    movie_title = 'Avatar'
    data = DataLoader(verbose=False)
    gold = parse_annotation_file('{} ALIGNED.txt'.format(movie_title))
    ssa_dict = make_ssa_dict()
    movie = data.get_movie(movie_title)
    pred = predict_gender_ssa(ssa_dict, movie, mode='soft', check_decade=True)
    print(pred)
    acc, mat = eval(gold, pred)
    print(acc)
    print(mat)
